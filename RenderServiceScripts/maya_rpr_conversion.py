import convertRS2RPR
import os
import maya.cmds as cmds
import maya.mel as mel
import datetime
import json


def initializeRPR():
	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")

	cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
	cmds.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 1)
	cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", 1)
	cmds.fireRender(waitForItTwo=True)
	mel.eval("renderIntoNewWindow render")


def rpr_render():
	
	cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
	
	cmds.optionVar(rm="RPR_DevicesSelected")
	cmds.optionVar(iva=("RPR_DevicesSelected", 1))

	cameras = cmds.ls(type="camera")
	for cam in cameras:
	    if cmds.getAttr(cam + ".renderable"):
	        cmds.lookThru(cam)

	cmds.fireRender(waitForItTwo=True)
	
	start_time = datetime.datetime.now()
	mel.eval("renderIntoNewWindow render")
	render_time = (datetime.datetime.now() - start_time).total_seconds()
	output = os.path.join("{res_path}", "{scene_name}_converted")
	cmds.renderWindowEditor("renderView", edit=True, dst="color")
	cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)

	# results json
	report = {{}}
	report['render_time'] = round(render_time, 2)
	report['width'] = cmds.getAttr("defaultResolution.width")
	report['height'] = cmds.getAttr("defaultResolution.height")
	report['iterations'] = cmds.getAttr("RadeonProRenderGlobals.completionCriteriaIterations")
	with open(os.path.join(".", "render_info.json"), 'w') as f:
		json.dump(report, f, indent=4)

def main():

	initializeRPR()
	mel.eval("setProject(\"{project}\")")
	cmds.file("{scene}", f=True, options="v=0;", ignoreVersion=True, o=True)
	convertRS2RPR.auto_launch()
	rpr_render()
	cmds.evalDeferred(cmds.quit(abort=True))