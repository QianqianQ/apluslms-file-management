import os
import sys
from hashlib import sha256
import logging


logger = logging.getLogger(__name__)


def _sig(file):
    # return (
    #         stat.S_IFMT(st.st_mode),
    #         st.st_size,
    #         st.st_mtime)
    st = os.stat(file)
    return {"mtime": st.st_mtime_ns,
            "checksum": 'sha256:' + sha256(open(file, 'rb').read()).hexdigest()}


def get_file_manifest(directory):
    """
    get manifest of files
    :param directory: str, the path of the directory
    :return: a nested dict with rel_file_name as the key and the value is a dict holding the file mtime and the size
    """
    # IGNORE = set(['.git', '.idea', '__pycache__'])  # or NONIGNORE if the dir/file starting with '.' is ignored

    manifest = dict()

    for basedir, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.')]
        for filename in files:
            file = os.path.join(basedir, filename)
            file_manifest = _sig(file)
            file_name = os.path.relpath(file, start=directory)
            manifest[file_name] = file_manifest

    return manifest


def check_directory(directory, upload_file):
    """ Check whether the static directory and the index.html file exist
    :param directory: str, the path of a static directory
    :param upload_file: str, the file type to upload ('html', 'yaml')
    :return: the path of the static directory, the path of the index.html file
             and the modification time of the index.html
    """

    # The path of the subdirectory that contains static files
    target_dir = os.path.join(directory, '_build', upload_file)
    index_file = os.path.join(target_dir, 'index.' + upload_file)
    if not os.path.exists(target_dir):
        raise FileNotFoundError("_build/{} directory not found".format(upload_file))
    elif not os.path.isdir(target_dir):
        raise NotADirectoryError("'_build/{}' is not a directory".format(upload_file))
    elif not os.path.exists(index_file):
        raise FileNotFoundError("index.{} not found".format(upload_file))

    index_mtime = _sig(index_file)["mtime"]

    return target_dir, index_file, index_mtime


class EnvVarNotFoundError(Exception):
    def __init__(self, *var_name):
        self.msg = " & ".join(*var_name) + " missing!"

    def __str__(self):
        return repr(self.msg)


def examine_env_var():
    required = {'PLUGIN_API', 'PLUGIN_TOKEN', 'PLUGIN_COURSE', 'ACTION'}

    if required <= os.environ.keys():
        pass
    else:
        missing = [var for var in required if var not in os.environ]
        raise EnvVarNotFoundError(missing)


class GetFileUpdateError(Exception):
    pass


class UploadError(Exception):
    pass


class PublishError(Exception):
    pass


def error_print():
    return '{}. {}, line: {}'.format(sys.exc_info()[0],
                                     sys.exc_info()[1],
                                     sys.exc_info()[2].tb_lineno)

