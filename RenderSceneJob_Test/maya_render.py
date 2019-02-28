import os
import maya.cmds as cmds
import maya.mel as mel


def rpr_render():
	
	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")
	
	cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
	cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
	iterations = {pass_limit}
	if iterations:
		cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", iterations)
	if cmds.getAttr("RadeonProRenderGlobals.completionCriteriaIterations") > 1000:
		cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", 1000)
	
	render_device_type = "{render_device_type}"
	if render_device_type == "gpu":
		cmds.optionVar(rm="RPR_DevicesSelected")
		cmds.optionVar(iva=("RPR_DevicesSelected", 1))
	elif render_device_type == "cpu":
		cmds.optionVar(rm="RPR_DevicesSelected")
		cmds.optionVar(iva=("RPR_DevicesSelected", 0))
	else:
		cmds.optionVar(rm="RPR_DevicesSelected")
		cmds.optionVar(iva=("RPR_DevicesSelected", 1))
		cmds.optionVar(iva=("RPR_DevicesSelected", 1))

	cameras = cmds.ls(type="camera")
	for cam in cameras:
	    if cmds.getAttr(cam + ".renderable"):
	        cmds.lookThru(cam)

	startFrame = {startFrame}
	endFrame = {endFrame}
	
	if startFrame == endFrame:
		cmds.fireRender(waitForItTwo=True)
		mel.eval("renderIntoNewWindow render")
		output = os.path.join("{res_path}", "{scene_name}")
		cmds.renderWindowEditor("renderView", edit=True, dst="color")
		cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)
	else:
		for i in range(startFrame, endFrame + 1):
			cmds.fireRender(waitForItTwo=True)
			cmds.currentTime(i)
			mel.eval("renderIntoNewWindow render")
			output = os.path.join("{res_path}", "{scene_name}_" + str(i))
			cmds.renderWindowEditor("renderView", edit=True, dst="color")
			cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)

def main():

	mel.eval("setProject(\"{project}\")")
	cmds.file("{scene}", f=True, options="v=0;", ignoreVersion=True, o=True)
	rpr_render()
	cmds.evalDeferred(cmds.quit(abort=True))