import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
from shutil import copyfile


def get_windows_titles():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    titles = []

    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)

    return titles


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--tool', required=True)
    parser.add_argument('--pass_limit', required=True)
    parser.add_argument('--render_device', required=True)
    parser.add_argument('--scene', required=True)

    args = parser.parse_args()

    with open("maya_render.mel") as f:
        mel_template = f.read()

    melScript = mel_template.format(scene = args.scene, render_device = args.render_device, \
        pass_limit = args.pass_limit)

    with open('maya_render.mel', 'w') as f:
        f.write(melScript)

    cmdRun = '''
    set MAYA_CMD_FILE_OUTPUT=Output/maya_log.txt 
    set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
    "C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\maya.exe" -command "source maya_render.mel; evalDeferred -lp (rpr_render());"''' \
        .format(scene=args.scene, tool=args.tool)

    with open('launch_render.bat', 'w') as f:
        f.write(cmdRun)

    p = psutil.Popen('launch_render.bat', stdout=subprocess.PIPE)
    rc = -1

    while True:
        try:
            rc = p.wait(timeout=30)
        except psutil.TimeoutExpired as err:
            fatal_errors_titles = ['maya', 'Radeon ProRender Error', 'Student Version File', 'Script Editor']
            if set(fatal_errors_titles).intersection(get_windows_titles()):
                rc = -1
                try:
                    error_screen = pyscreenshot.grab()
                    error_screen.save(os.path.join('Output', 'error_screenshot.jpg'))
                except:
                    pass
                for child in reversed(p.children(recursive=True)):
                    child.terminate()
                p.terminate()
                break
        else:
            break

    return rc


if __name__ == "__main__":
    rc = main()
    exit(rc)
