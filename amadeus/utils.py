import glob
import os
import urllib
import shutil
import zipfile


def glob_files_relative_to_from_dir(path, target_dir, pattern):
    resource_dir = os.path.join(path, target_dir)
    file_search = os.path.join(resource_dir, pattern)
    return glob.glob(file_search)


def glob_files(path, pattern):
    file_search = os.path.join(path, pattern)
    return glob.glob(file_search)


def zipdir(zipname, path, **kwargs):
    ziph = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
    for root, dir, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, basename(file)), basename(file))
    ziph.close()


def unziptodir(zipname, target, **kwargs):
    ziph = zipfile.ZipFile(zipname, 'r', zipfile.ZIP_DEFLATED)
    ziph.extractall(target)
    ziph.close()


def rmtree(path):
    shutil.rmtree(path)


def dir_name(filename):
    return os.path.dirname(filename)


def basename(filepath):
    return os.path.basename(filepath)


def user_dir():
    return os.path.expanduser('~')


def abs_path_for_file(filename):
    return os.path.abspath(filename)


def path_join(path, filename):
    return os.path.join(path, filename)


def does_file_exist(abspathfilename):
    return os.path.isfile(abspathfilename)


def does_directory_exist(directory):
    return os.path.isdir(directory)


def make_directory(directory, force=False):
    if force and does_directory_exist(directory):
        rmtree(directory)
    os.makedirs(directory)


def get_cwd():
    return os.getcwd()


def in_truths(value):
    return value in [True, 'T', 'yes', 'true', 'True', 'TRUE']


def is_str(value):
    return isinstance(value, basestring)


def url_encode(value):
    return urllib.quote_plus(value)
