import os

def createDir(nameDir):
    if not os.path.exists(nameDir):
        os.mkdir(nameDir)

def getNameFiles(path):
    return os.listdir("{}/Metrics".format(path))


def get_flies_sorted(path):
    names_info = getNameFiles(path)
    return sorted(names_info, key=lambda x: float(x[:-16]))