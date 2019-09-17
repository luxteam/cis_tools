import bpy
import addon_utils
import datetime
import sys
import json
import os
import logging
import pyrpr


def initializeRPR():
	scene = bpy.context.scene
	enable_rpr_render(scene)
	set_value(scene.rpr.limits, 'seconds', 1)
	bpy.ops.render.render()


def set_value(path, name, value):
	if hasattr(path, name):
		setattr(path, name, value)
	else:
		print("No attribute found {{}}".format(name))


def get_value(path, name):
	if hasattr(path, name):
		return getattr(path, name)
	else:
		print("No attribute found ")


def enable_rpr_render(scene):
	if not addon_utils.check('rprblender')[0]:
		addon_utils.enable('rprblender', default_set=True, persistent=False, handle_error=None)
	set_value(scene.render, 'engine', 'RPR')


def set_render_device():
	render_devices = bpy.context.preferences.addons['rprblender'].preferences.settings.final_devices
	set_value(bpy.context.preferences.addons['rprblender'].preferences.settings.final_devices, "cpu_state", False)
	set_value(bpy.context.preferences.addons['rprblender'].preferences.settings.final_devices, "gpu_states[0]", True)
	device_name = pyrpr.Context.gpu_devices[0]['name']

	return device_name


def render(scene_name):

	# open scene
	bpy.ops.wm.open_mainfile(filepath=os.path.join(r"{res_path}", scene_name))

	# get scene name
	scene = bpy.context.scene

	# enable rpr
	enable_rpr_render(scene)

	# Render device in RPR
	device_name = set_render_device()

	if {min_samples}:
		set_value(scene.rpr.limits, 'min_samples', {min_samples})
	if {max_samples}:
		set_value(scene.rpr.limits, 'max_samples', {max_samples})
	if {noise_threshold}:
		set_value(scene.rpr.limits, 'noise_threshold', {noise_threshold})
	set_value(scene.rpr.limits, 'seconds', 1800)

	if {width}:
		set_value(bpy.context.scene.render, 'resolution_x', {width})
	if {height}:
		set_value(bpy.context.scene.render, 'resolution_y', {height})

	# image format
	set_value(scene.render.image_settings, 'quality', 100)
	set_value(scene.render.image_settings, 'compression', 0)
	set_value(scene.render.image_settings, 'color_mode', 'RGB')
	set_value(scene.render.image_settings, 'file_format', 'JPEG')

	# output
	set_value(scene.render, 'filepath', os.path.join("{res_path}", "Output", "{sceneName}"))
	set_value(scene.render, 'use_placeholder', True)
	set_value(scene.render, 'use_file_extension', True)
	set_value(scene.render, 'use_overwrite', True)

	# start render animation
	render_time = 0
	startFrame = {startFrame}
	endFrame = {endFrame}
	if startFrame == endFrame:
		if startFrame != 1:
			scene.frame_set(startFrame)
			set_value(scene.render, 'filepath', os.path.join("{res_path}", "Output", "{sceneName}_" + str(startFrame).zfill(3)))
		start_time = datetime.datetime.now()
		bpy.ops.render.render(write_still=True, scene=scene_name)
		render_time += (datetime.datetime.now() - start_time).total_seconds()
	else:
		for each in range(startFrame, endFrame+1):
			scene.frame_set(each)
			set_value(scene.render, 'filepath', os.path.join("{res_path}", "Output", "{sceneName}_" + str(each).zfill(3)))
			start_time = datetime.datetime.now()
			bpy.ops.render.render(write_still=True, scene=scene_name)
			render_time += (datetime.datetime.now() - start_time).total_seconds()

	# results json
	report = {{}}
	report['render_time'] = round(render_time, 2)
	report['width'] = get_value(bpy.context.scene.render, 'resolution_x')
	report['height'] = get_value(bpy.context.scene.render, 'resolution_y')
	report['min_samples'] = get_value(scene.rpr.limits, 'min_samples')
	report['max_samples'] = get_value(scene.rpr.limits, 'max_samples')
	report['noise_threshold'] = get_value(scene.rpr.limits, 'noise_threshold')
	with open(os.path.join("{res_path}", "render_info.json"), 'w') as f:
		json.dump(report, f, indent=' ')


if __name__ == "__main__":
	initializeRPR()
	render(r'{scene_name}')
