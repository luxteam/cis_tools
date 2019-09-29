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


def resolveFilePath():
    unresolved_files = cmds.filePathEditor(query=True, listFiles="", unresolved=True, attributeOnly=True)
    if unresolved_files:
        try:
            new_path = "{project}";
            for item in unresolved_files:
                cmds.filePathEditor(item, repath=new_path, recursive=True, replaceAll=True)
        except:
            pass


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
	with open("rpr_render_info.json", 'w') as f:
		json.dump(report, f, indent=4)

def main():

	initializeRPR()
	mel.eval("setProject(\"{project}\")")
	cmds.file("{scene}", f=True, options="v=0;", ignoreVersion=True, o=True)
	resolveFilePath()
	convertRS2RPR.auto_launch()
	rpr_render()
	cmds.evalDeferred(cmds.quit(abort=True))