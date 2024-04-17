import os
import re
import yaml


def replace_variables_in_string(string):
    def replace_variables(match):
        variable_name = match.group(1)
        variable_value = os.environ.get(variable_name, '')
        return variable_value
    pattern = r'\$(\w+)'
    replaced_string = re.sub(pattern, replace_variables, string)
    return replaced_string


def Config(file_path_: str):
    with open(file_path_, 'r') as file:
        config = yaml.safe_load(file)
    config = replace_variables_in_string(str(config))
    config = eval(config)
    return config




