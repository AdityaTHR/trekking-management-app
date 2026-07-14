from jinja2 import Template


def prepare_template(filename, data):
    with open(filename, "r") as file:
        template = Template(file.read())
        output = template.render(data=data)
        return output
