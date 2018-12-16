
import convertRS2RPR.auto_launch as convert
import os

def rpr_render():
	
	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")
	
	cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
	cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
	cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", {pass_limit})
	
	cmds.optionVar(rm="RPR_DevicesSelected")
	cmds.optionVar(iva="RPR_DevicesSelected", 1)


	cmds.fireRender(waitForItTwo=True)
	
	mel.eval("renderIntoNewWindow render")
	output = os.path.join("{res_path}", "Output", "{scene_name}")
	cmds.renderWindowEditor("renderView", edit=True, dst="color")
	cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)


def redshift_render():
	
	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")
	
	cmds.setAttr("defaultRenderGlobals.currentRenderer", "redshift", type="string")
	cmds.setAttr("redshiftOptions.imageFormat", 4)
	cmds.setAttr("redshiftOptions.jpegQuality", 100)
	
	mel.eval("renderIntoNewWindow render")
	output = os.path.join("{res_path}", "Output", "{scene_name}")
	cmds.renderWindowEditor("renderView", edit=True, dst="color")
	cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)
	

def main():

	cmds.file("{scene}", f=True, options="v=0;", ignoreVersion=True, o=True)
	redshift_render()
	convert()
	rpr_render()
	evalDeferred("quit -abort");
