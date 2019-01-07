
import convertRS2RPR
import os
import maya.cmds as cmds
import maya.mel as mel


def rpr_render():
	
	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")
	
	cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
	cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
	cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", {pass_limit})
	
	cmds.optionVar(rm="RPR_DevicesSelected")
	cmds.optionVar(iva=("RPR_DevicesSelected", 1))


	cmds.fireRender(waitForItTwo=True)
	
	mel.eval("renderIntoNewWindow render")
	output = os.path.join("{res_path}", "{scene_name}_converted")
	cmds.renderWindowEditor("renderView", edit=True, dst="color")
	cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)


def main():

	cmds.file("{scene}", f=True, options="v=0;", ignoreVersion=True, o=True)
	convertRS2RPR.auto_launch()
	rpr_render()
	cmds.file( rename='converted_scene.ma')
	cmds.file( save=True, type='mayaAscii' )
	cmds.evalDeferred(cmds.quit(abort=True))
