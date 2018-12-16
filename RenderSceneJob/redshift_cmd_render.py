import maya.standalone
import sys
import os
import maya.cmds as cmds
from convertRS2RPR import auto_launch as convert
from subprocess import Popen

def rpr_render(scene):

	current_path = os.getcwd().replace("\\", "/")
	scene = os.path.join(current_path, scene).replace("\\", "/")
	output_path = os.path.join(current_path, "Output").replace("\\", "/")

	renderer_folder = os.path.split(sys.executable)[0]
	renderer_exec_name = "Render"
	params = [renderer_exec_name]
	params += ['-r', 'FireRender']
	params += ['-cam', 'camera1']
	params += ['-im', 'converted_{scene_name}']
	params += ['-of', 'jpg']
	params += ['-rd', output_path]
	params += [scene]
	p = Popen(params, cwd=renderer_folder)
	stdout, stderr = p.communicate()

	with open(os.path.join("Output", "rsRenderTool.log"), 'w', encoding='utf-8') as file:
		stdout = stdout.decode("utf-8")
		file.write(stdout)

	with open(os.path.join("Output", "rsRenderTool.log"), 'a', encoding='utf-8') as file:
		file.write("\n ----STEDERR---- \n")
		stderr = stderr.decode("utf-8")
		file.write(stderr)

def rs_render(scene):

	current_path = os.getcwd().replace("\\", "/")
	scene = os.path.join(current_path, scene).replace("\\", "/")
	output_path = os.path.join(current_path, "Output").replace("\\", "/")

	renderer_folder = os.path.split(sys.executable)[0]
	renderer_exec_name = "Render"
	params = [renderer_exec_name]
	params += ['-r', 'redshift']
	params += ['-cam', 'camera1']
	params += ['-im', '{scene_name}']
	params += ['-of', 'jpg']
	params += ['-rd', output_path]
	params += [scene]
	p = Popen(params, cwd=renderer_folder)
	stdout, stderr = p.communicate()

	with open(os.path.join("Output", "rprRenderTool.log"), 'w', encoding='utf-8') as file:
		stdout = stdout.decode("utf-8")
		file.write(stdout)

	with open(os.path.join("Output", "rprRenderTool.log"), 'a', encoding='utf-8') as file:
		file.write("\n ----STEDERR---- \n")
		stderr = stderr.decode("utf-8")
		file.write(stderr)

def main():

	maya.standalone.initialize("Python")

	scene = "{scene}"

	rs_render(scene)

	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
			cmds.loadPlugin("RadeonProRender")

	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
			cmds.loadPlugin("RadeonProRender")

	cmds.file(scene, o=True, f=True, options="v=0;", ignoreVersion=True)

	convert()

	cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", {pass_limit})
	cmds.file(save=True, type='mayaAscii')

	rpr_render(scene)

	os.rename("{scene_name}.log", os.path.join("Output", "{scene_name}.log"))
	os.rename(os.path.join("Output", "color", "converted_{scene_name}.jpg"), os.path.join("Output", "converted_{scene_name}.jpg"))
	os.remove(os.path.join("Output", "opacity", "converted_{scene_name}.jpg"))
	os.rmdir(os.path.join("Output", "opacity"))
	os.rmdir(os.path.join("Output", "color"))


if __name__ == '__main__':
	main()