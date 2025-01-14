from dataclasses import dataclass
import pandas as pd

from utils import common

@dataclass(frozen=True)
class folder:
    data = "data/"
    raw = "raw/"
    processed = 'processed/'
    misc = "misc/"
    kmModel = "kmModels/"
    img = "img/"
    statefulGanImg = img + "statefulGan/"
    basicGanImg = img + "basicGan/"


@dataclass(frozen=True)
class binary_casas:
    """
    A data class of filenames for the binary CASAS dataset
    with methods to return ml_data objects of pd.DataFrames given those filenames
    """
    _fileExtension = ".csv"
    _trainSuffix = "Train" + _fileExtension
    _testSuffix = "Test" + _fileExtension

    _filePath = folder.data + "binaryCasas/" + folder.processed
    _trainFile = _filePath + "{filename}" + _trainSuffix
    _testFile = _filePath + "{filename}" + _testSuffix

    _homeName = "b{}"
    _home1Name = _homeName.format("1")
    _home2Name = _homeName.format("2")
    _home3Name = _homeName.format("3")


    h1Home = common.ml_data(
        train=_trainFile.format(filename=_home1Name),
        test = _testFile.format(filename=_home1Name)
    )

    h2Home = common.ml_data(
        train=_trainFile.format(filename=_home2Name),
        test = _testFile.format(filename=_home2Name)
    )

    h3Home = common.ml_data(
        train=_trainFile.format(filename=_home3Name),
        test = _testFile.format(filename=_home3Name)
    )

    allHomes = [h1Home, h2Home, h3Home]

    @staticmethod
    def _get_home(fileNames:common.ml_data):
        dfs = fileNames.apply(pd.read_csv)
        return dfs

    @staticmethod
    def get_home1():
        return binary_casas._get_home(binary_casas.h1Home)

    @staticmethod
    def get_home2():
        return binary_casas._get_home(binary_casas.h2Home)

    @staticmethod
    def get_home3():
        return binary_casas._get_home(binary_casas.h3Home)

    @staticmethod
    def get_all_homes():
        return [binary_casas.get_home1(), binary_casas.get_home2(), binary_casas.get_home3()]



@dataclass(frozen=True)
class extensions:
    kerasModel = ".km"


if __name__ == "__main__":
    homes = binary_casas.get_all_homes()
    #example
    print(homes[0].train)
    exit()