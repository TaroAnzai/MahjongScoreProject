from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

def render_mail_template(template_name, **context):
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )

    text_template = env.get_template(f"{template_name}.txt")
    html_template = env.get_template(f"{template_name}.html")

    text_body = text_template.render(**context)
    html_body = html_template.render(**context)
    return text_body, html_body
