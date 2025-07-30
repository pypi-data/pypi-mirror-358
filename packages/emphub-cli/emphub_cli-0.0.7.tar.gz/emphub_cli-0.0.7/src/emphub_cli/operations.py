import yaml
from datetime import datetime
import shutil
import os
import tarfile
from glob import glob
from .miniohelpers import getClient


def getConfig(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)
        return config


def pullPackage(package, tag, config):
    client = getClient(config)
    bucket = config["registry"]["bucket"]
    path = "{}/{}/{}/".format(
        os.path.expanduser(config["local-storage"]["path"]),
        package, tag
    )
    now = datetime.now()
    obj = client.fget_object(
        bucket,
        "{}/{}/package.tgz".format(package, tag),
        path + "package.tgz"
    )
    delta = datetime.now() - now
    shutil.rmtree(path + "package", ignore_errors=True)
    tar = tarfile.open(path + "package.tgz")
    tar.extractall(path=path)
    os.rename(path + tar.getmembers()[0].name, path + "package")
    tar.close()
    bitfile_name = glob(path + "package/*.bit")[0]
    os.replace(bitfile_name, path + "package/top.bit")
    os.rename(path + "connections.xml", path + "package/connections.xml")
    return obj, delta


def pushPackage(package, tag, path, config):
    client = getClient(config)
    bucket = config["registry"]["bucket"]
    size = os.path.getsize(path)
    now = datetime.now()
    client.fput_object(
        bucket,
        "{}/{}/package.tgz".format(package, tag),
        path
    )
    delta = datetime.now() - now
    return size, delta
