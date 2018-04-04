import jinja2
import os
import argparse
import hashlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', required=False)
    args = parser.parse_args()

    env = jinja2.Environment(
        loader=jinja2.PackageLoader('main', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('index.html')

    folders = []
    files_list = {}
    exact = {}

    for baseline in os.listdir(args.input_path):
        baseline_path = os.path.join(args.input_path, baseline)
        if os.path.isdir(baseline_path):
            folders.append(baseline)

    for baseline in os.listdir(args.input_path):
        baseline_path = os.path.join(args.input_path, baseline)
        for path, dirs, files in os.walk(baseline_path):
            for file in files:
                file_key = os.path.relpath(os.path.join(path, file), baseline_path).replace("\\", "/")
                if file_key not in files_list and not file_key.endswith('placeholder.txt'):
                    files_list[file_key] = {}
                    exact.update({file_key: True})
                    for base in folders:
                        try:
                            files_list[file_key].update({base:
                                                     hashlib.md5(open(os.path.join(args.input_path, base,file_key), 'rb').read()).hexdigest()})
                        except Exception as err:
                            files_list[file_key].update({base: ""})
                            print(str(err))
                            
                    if len(set(files_list[file_key].values())) > 1:
                        exact.update({file_key: False})

    html_result = template.render(title='Baselines compare', files_list=files_list, folders=folders, exact=exact)

    with open(os.path.join(args.input_path, 'compare.html'), 'w') as html_file:
        html_file.write(html_result)


if __name__ == '__main__':
    main()
