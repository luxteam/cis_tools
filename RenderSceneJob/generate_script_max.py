import os
import argparse

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	parser.add_argument('--scene')
	parser.add_argument('--pass_limit')
	parser.add_argument('--render_device')
	args = parser.parse_args()
	
	folder = args.folder
	scene = args.scene
	scene = folder + "\\\\" + scene
	render_device = args.render_device
	if render_device == 'gpu':
		render_device = '2'
	elif render_device == 'cpu':
		render_device = '1'
	elif render_device == 'dual':
		render_device = '3'

	with open("max_render.ms") as f:
            max_template = f.read()
	maxScript = max_template.format(scene=args.scene, pass_limit=int(args.pass_limit), render_device=args.render_device)

	with open("max_render.ms", 'w') as f:
            f.write(maxScript)
			
if __name__ == "__main__":

	main()
