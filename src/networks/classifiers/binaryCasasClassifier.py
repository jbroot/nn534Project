#max is so slow
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers as l

from processData.binaryCasasProcess import binaryCasasData as bcData
from names import binaryCasasNames as bcNames
from networks import commonBlocks as cBlocks, defaults
from utils import common, globalVars as gv
from utils import filePaths as fp
from pathlib import Path
import pandas as pd
import glob

BATCH_SIZE = 64
N_TIME_STEPS = 32
EPOCHS = 2 if gv.DEBUG else 6

def run():
    df = getSynthData()
    trainModel(df)

"""
Merge multiple .csv files into one dataframe
"""
def getSynthData():
    synth_dir = Path(__file__).parent.parent.parent/'synthetic-data'
    all_files = glob.glob(str(synth_dir) + "/*.csv")
    df_from_each_file = (pd.read_csv(f, header = None) for f in all_files)
    df = pd.concat(df_from_each_file, ignore_index=True)
    return df

def trainModel(df: pd.DataFrame):
    train=df.sample(frac=0.8, random_state=200) #random state is a seed value
    test=df.drop(train.index)
    x_train = train.iloc[:, :bcNames.pivots.activities.start]
    y_train = train.iloc[:, bcNames.pivots.activities.start:]
    x_test = test.iloc[:, :bcNames.pivots.activities.start]
    y_test = test.iloc[:, bcNames.pivots.activities.start:]
    print(train.shape)


def basic_cnn() -> keras.models.Model:
    inputLayer = keras.Input(shape=(N_TIME_STEPS, len(bcNames.features))) #should be 48 channels
    x = cBlocks.conv_block(inputLayer, 24, defaults.leaky_relu(),) #16 timesteps
    x = cBlocks.conv_block(x, 15, defaults.leaky_relu()) #8 timesteps
    x = cBlocks.conv_block(x, 11, defaults.leaky_relu()) #4 timesteps
    x = cBlocks.conv_block(x, 8, defaults.leaky_relu()) #2 timesteps
    x = cBlocks.conv_block(x, len(bcNames.allActivities), activation=keras.activations.softmax)
    x = l.Flatten()(x)
    model = keras.models.Model(inputLayer, x, name="Basic_CNN_Classifier")
    model.compile(loss = keras.losses.CategoricalCrossentropy(),
                  optimizer = defaults.optimizer(), metrics = defaults.METRICS)
    return model

#Nathan uses temporal CNNs

def multi_head_cnn():
    pass

def run_classifiers(data:common.ml_data):
    model = basic_cnn()
    # print(model.summary())
    history = model.fit(data.train.gen, epochs=EPOCHS, steps_per_epoch = defaults.STEPS_PER_EPOCH,
                        validation_data=data.test.gen, validation_steps=defaults.VALIDATION_STEPS)
    return model, history

if __name__ == "__main__":
    # allHomes = bcData.get_all_homes_as_xy_split_gen(
    #     batchSize=BATCH_SIZE, nTimesteps=N_TIME_STEPS,
    #     xyPivot=bcNames.pivots.activities.start, firstN=gv.DATA_AMT
    # )
    # run_classifiers(allHomes[0].data)
    run()
    exit()