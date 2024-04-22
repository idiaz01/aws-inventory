import yaml


def load_yaml(file_path):
    """
    Load a yaml file and return the content as a dictionary
    :param file_path: path to the yaml file
    :return: dictionary with the content of the yaml file
    """
    with open(file_path, 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)
