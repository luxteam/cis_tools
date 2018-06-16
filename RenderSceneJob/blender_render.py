import bpy
import addon_utils
import datetime
import sys
import json
import os
from rprblender import node_editor
from rprblender import material_browser
from rprblender import helpers
from pyrpr import API_VERSION
from shutil import copyfile

def core_ver_str():
	core_ver = API_VERSION
	mj = (core_ver & 0xFFFF00000) >> 28
	mn = (core_ver & 0xFFFFF) >> 8
	return "%x.%x" % (mj, mn)

def render(*argv):

	#get scene name
	Scenename = bpy.context.scene.name

	# RPR Settings
	if((addon_utils.check("rprblender"))[0] == False) : 
		addon_utils.enable("rprblender", default_set=True, persistent=False, handle_error=None)
	bpy.data.scenes[Scenename].render.engine = "RPR"
	
	bpy.data.scenes[Scenename].rpr.render.rendering_limits.iterations = {pass_limit}

	device_name = ""
	# Render device in RPR
	if '{render_device}' == 'dual':
		device_name = "CPU" + " + " + helpers.render_resources_helper.get_used_devices()
		bpy.context.user_preferences.addons["rprblender"].preferences.settings.device_type_plus_cpu = True
		bpy.context.user_preferences.addons["rprblender"].preferences.settings.device_type = 'gpu'
	elif '{render_device}' == 'cpu':
		device_name = "CPU"
		bpy.context.user_preferences.addons["rprblender"].preferences.settings.device_type = 'cpu'
		bpy.context.user_preferences.addons["rprblender"].preferences.settings.device_type_plus_cpu = False
	elif '{render_device}' == 'gpu':
		device_name = helpers.render_resources_helper.get_used_devices()
	bpy.context.user_preferences.addons["rprblender"].preferences.settings.include_uncertified_devices = True

	# frame range
	bpy.data.scenes[Scenename].frame_start = 1
	bpy.data.scenes[Scenename].frame_end = 1

	name_scene = bpy.path.basename(bpy.context.blend_data.filepath)

	# output
	output = os.path.join("C:\\JN\\WS\\Render_Scene_Test\\Output", name_scene)
	bpy.data.scenes[Scenename].render.filepath = output 
	bpy.data.scenes[Scenename].render.use_placeholder = True
	bpy.data.scenes[Scenename].render.use_file_extension = True
	bpy.data.scenes[Scenename].render.use_overwrite = True

	# start render animation
	TIMER = datetime.datetime.now()
	bpy.ops.render.render(write_still=True,scene=Scenename)
	Render_time = datetime.datetime.now() - TIMER

	# get version of rpr addon
	for mod_name in bpy.context.user_preferences.addons.keys():
		if (mod_name == 'rprblender') : 
			mod = sys.modules[mod_name]
			ver = mod.bl_info.get('version')
			version = str(ver[0]) + "." + str(ver[1]) + "." + str(ver[2])
		
	image_format = (bpy.data.scenes[Scenename].render.image_settings.file_format).lower()
	if (image_format == 'jpeg'):
		image_format = 'jpg'

	# LOG
	log_name = os.path.join("C:\\JN\\WS\\Render_Scene_Test\\Output", name_scene + ".json")
	report = {{}}
	report['render_version'] = version
	report['render_mode'] = 'gpu'
	report['core_version'] = core_ver_str()
	report['render_device'] = device_name
	report['tool'] = "Blender " + bpy.app.version_string.split(" (")[0]
	report['scene_name'] = bpy.path.basename(bpy.context.blend_data.filepath)
	report['render_time'] = Render_time.total_seconds()
	report['date_time'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

	with open(log_name, 'w') as file:
		json.dump([report], file, indent=' ')
	

if __name__ == "__main__":
		
		render()
