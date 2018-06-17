import argparse
import sys
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
import platform


def main():

    parser = argparse.ArgumentParser()
    
    parser.add_argument('--tool', required=True)
    parser.add_argument('--scene', required=True)
    parser.add_argument('--render_mode', required=True)
    parser.add_argument('--pass_limit', required=True)

    args = parser.parse_args()

    with open ("blender_render.py") as f:
        blender_script_template = f.read()

    BlenderScript = blender_script_template.format(work_dir=work_dir, render_mode=args.render_mode,
                                                   pass_limit=args.pass_limit,
                                                   res_path=args.res_path, resolution_x=args.resolution_x,
                                                   resolution_y=args.resolution_y, package_name=args.package_name,
                                                   start=0)


    with open("blender_render.py", 'w') as f:
        f.write(BlenderScript)

    cmdRun = '"{tool}" -b "{scene}" -P "{template}"\n' \
        .format(tool=args.tool, scene=args.scene, template="blender_render.py")

    system_pl = platform.system()

    if (system_pl == 'Linux'):
        with open('launch_render.sh', 'w') as f:
            f.write(cmdRun)
        os.system('chmod +x launch_render.sh')

    elif (system_pl == "Windows"):
        with open('launch_render.bat', 'w') as f:
            f.write(cmdRun)

    elif system_pl == 'Darwin':
        with open('launch_render.sh', 'w') as f:
           f.write(cmdRun)
        os.system('chmod +x launch_render.sh')
    
    print(system_pl)

    p = subprocess.Popen(cmdScriptPath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    with open(os.path.join(args.output, "renderTool.log"), 'w') as file:
        stdout = stdout.decode("utf-8")
        file.write(stdout)

    with open(os.path.join(args.output, "renderTool.log"), 'a') as file:
        file.write("\n ----STEDERR---- \n")
        stderr = stderr.decode("utf-8")
        file.write(stderr)

    rc = -1

    try:
        rc = p.wait(timeout=100)
    except psutil.TimeoutExpired as err:
        rc = -1
        error_screen = pyscreenshot.grab()
        error_screen.save(os.path.join(args.output, 'Output/error_screenshot.jpg'))
        for child in reversed(p.children(recursive=True)):
            child.terminate()
        p.terminate()

    return rc

if __name__ == "__main__":
    rc = main()
    exit(rc)
