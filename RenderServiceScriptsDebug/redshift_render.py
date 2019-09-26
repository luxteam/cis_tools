import os
import maya.cmds as cmds
import maya.mel as mel
import datetime
import json


def resolveFilePath():
	unresolved_files = cmds.filePathEditor(query=True, listFiles="", unresolved=True, attributeOnly=True)
	if unresolved_files:
		try:
			new_path = "{project}";
			for item in unresolved_files:
				cmds.filePathEditor(item, repath=new_path, recursive=True, replaceAll=True)
		except:
			pass

	aov_nodes = cmds.ls(type="RedshiftAOV")
	for node in aov_nodes:
		cmds.setAttr(node + ".filePrefix", "{res_path}", type="string")


def main():

	mel.eval("setProject(\"{project}\")")

	# scene name
	split_name = cmds.file(q=True, sn=True, shn=True).split('.')
	scenename = '.'.join(split_name[0:-1])

	cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "{res_path}/Output/" + scenename, type="string")

	resolveFilePath()

	if {max_samples}:
		cmds.setAttr("redshiftOptions.unifiedMaxSamples", {max_samples})
	if {min_samples}:
		cmds.setAttr("redshiftOptions.unifiedMinSamples", {min_samples})
	if {noise_threshold}:
		cmds.setAttr("redshiftOptions.unifiedAdaptiveErrorThreshold", {noise_threshold})

	if {width}:
		cmds.setAttr("defaultResolution.width", {width})
	if {height}:
		cmds.setAttr("defaultResolution.height", {height})

	cmds.setAttr("redshiftOptions.progressiveRenderingEnabled", 0)

	# results json
	report = {{}}
	report['width'] = cmds.getAttr("defaultResolution.width")
	report['height'] = cmds.getAttr("defaultResolution.height")
	report['min_samples'] = cmds.getAttr("redshiftOptions.unifiedMinSamples")
	report['max_samples'] = cmds.getAttr("redshiftOptions.unifiedMaxSamples")
	report['noise_threshold'] = cmds.getAttr("redshiftOptions.unifiedAdaptiveErrorThreshold")
	with open(os.path.join(".", "render_info.json"), 'w') as f:
		json.dump(report, f, indent=4)
