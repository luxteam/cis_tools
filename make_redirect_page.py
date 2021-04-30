import argparse
import os
import jinja2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redirect_link", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--file_name", required=True)

    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(os.path.join(args.output_path))

    env = jinja2.Environment(
        loader=jinja2.PackageLoader("make_redirect_page", "templates"),
        autoescape=True
    )
    template = env.get_template("redirect_report_page.html")

    redirect_page = template.render(title="Redirect report page", redirect_link=args.redirect_link)

    with open(os.path.join(args.output_path, args.file_name), "w") as html_file:
        html_file.write(redirect_page)


if __name__ == '__main__':
    main()