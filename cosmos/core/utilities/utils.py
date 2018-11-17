import os


class Utils(object):

    @staticmethod
    def get_python_path(path):
        return f"{path.replace('/', '.')}"[:-3]

    @staticmethod
    def get_file_directory(path):
        return os.path.basename(os.path.dirname(path))
