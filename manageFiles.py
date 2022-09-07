import os

def createDir(nameDir):
    if not os.path.exists(nameDir):
        os.mkdir(nameDir)

def getNameFiles(path):
    return os.listdir(path)


def get_flies_sorted(path):
    names_info = getNameFiles("{}/Metrics".format(path))
    return sorted(names_info, key=lambda x: float(x[:-16]))

def get_files_info_net():
    lst_files = os.listdir("./metrics_csv")    
    return list(filter(lambda name: 'metrics_' in name, lst_files))