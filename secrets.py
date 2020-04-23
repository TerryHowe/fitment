import yaml


def get_secret():
    with open('.secrets.yml') as file:
        contents = file.read()
    return yaml.load(contents)