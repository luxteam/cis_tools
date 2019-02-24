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
import logging

def core_ver_str():
	core_ver = API_VERSION
	mj = (core_ver & 0xFFFF00000) >> 28
	mn = (core_ver & 0xFFFFF) >> 8
	return "%x.%x" % (mj, mn)


def set_value(path, name, value):
	if hasattr(path, name):
		setattr(path, name, value)
	else:
		logging.warning("No attribute found ")

def get_value(path, name, value):
	if hasattr(path, name):
		return getattr(path, name)
	else:
		logging.warning("No attribute found ")


def render(scene_name):

	# open scene
	bpy.ops.wm.open_mainfile(filepath=os.path.join(r"{res_path}", scene_name))

	# get scene name
	scene_name, scene = helpers.get_current_scene()

	# RPR Settings
	if not addon_utils.check("rprblender")[0]:
		addon_utils.enable("rprblender", default_set=True, persistent=False, handle_error=None)
	set_value(scene.render, 'engine', "RPR")

	# Render device in RPR
	set_value(helpers.get_user_settings(), "include_uncertified_devices", True)

	if '{render_device_type}' == 'dual':
		helpers.set_render_devices(use_cpu=True, use_gpu=True)
	elif '{render_device_type}' == 'cpu':
		helpers.set_render_devices(use_cpu=True, use_gpu=False)
	elif '{render_device_type}' == 'gpu':
		helpers.set_render_devices(use_cpu=False, use_gpu=True)

	device_name = helpers.render_resources_helper.get_used_devices()

	# frame range
	set_value(scene, "frame_start", {startFrame})
	set_value(scene, "frame_end", {endFrame})
	iterations = {pass_limit}
	if iterations:
		set_value(bpy.context.scene.rpr.render.rendering_limits, 'iterations', iterations)

	# image format
	set_value(scene.render.image_settings, 'file_format', 'JPEG')
	set_value(scene.render.image_settings, 'quality', 100)
	set_value(scene.render.image_settings, 'compression', 0)
	set_value(scene.render.image_settings, 'color_mode', 'RGB')

	# output
	set_value(scene.render, 'filepath', os.path.join("{res_path}", "Output", "{sceneName}"))
	set_value(scene.render, 'use_placeholder', True)
	set_value(scene.render, 'use_file_extension', True)
	set_value(scene.render, 'use_overwrite', True)

	# start render animation
	if {startFrame} == {endFrame}:
		TIMER = datetime.datetime.now()
		bpy.ops.render.render(write_still=True, scene=scene_name)
		render_time = datetime.datetime.now() - TIMER
	else:
		TIMER = datetime.datetime.now()
		bpy.ops.render.render(animation=True, scene=scene_name)
		render_time = datetime.datetime.now() - TIMER


if __name__ == "__main__":
		
	render(r'{scene_name}')
