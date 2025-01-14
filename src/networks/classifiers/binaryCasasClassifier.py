#max is so slow
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers as l
import numpy as np
import os

from processData.binaryCasasProcess import binaryCasasData as bcData, postProcess as pp
from names import binaryCasasNames as bcNames
from networks import commonBlocks as cBlocks, defaults
from utils import common, globalVars as gv
from networks.gans import stateFulGan as sfg, betterBaseGan as bbg, genApi
import matplotlib.pyplot as plt

BATCH_SIZE = sfg.BATCH_SIZE
N_TIME_STEPS = 16
EPOCHS = 10
PATH_ASSETS = os.getcwd()
STEPS_PER_EPOCH = 250

def run():
    print("######### No GAN #########")
    # trtr("CNN_on_real")

    print("######### Base GAN #########")
    loadGan = False
    gan = bbg.get_gan(loadGan)
    gan = bbg.train_gan(gan, 1)
    genOut = []
    for sampleNum in range(1000):
        if sampleNum % 500 == 0:
            print("On sample num {} with batch size {}".format(sampleNum, BATCH_SIZE))
        genOut.append(genApi.get_gen_out(gan.generator, bbg.NOISE_DIM, batchSize=bbg.BATCH_SIZE))

    #np.ndarray in shape (samples, time steps, features)
    genOut = np.concatenate(genOut, axis=0)
    genOut = pp.gen_out_to_real_normalized(genOut)

    x,y = genOut[...,:bcNames.nFeatures], genOut[...,-1,bcNames.nFeatures:]
    print("X and Y shapes:", x.shape, y.shape)
    tstr(x, y, "base_GAN")

    # print("######## Stateful GAN #########")
    # loadGan = True
    # loadGan = False
    # gan = sfg.get_gan(loadGan)
    # gan = sfg.run_gan(gan, 10)

    # genOut = []
    # for sampleNum in range(1000):
    #     if sampleNum % 500 == 0:
    #         print("On sample num {} with batch size {}".format(sampleNum, BATCH_SIZE))
    #     genOut.append(genApi.get_gen_out(gan.generator, sfg.NOISE_DIM, batchSize=sfg.BATCH_SIZE))

    # #np.ndarray in shape (samples, time steps, features)
    # genOut = np.concatenate(genOut, axis=0)
    # genOut = pp.gen_out_to_real_normalized(genOut)

    # x,y = genOut[...,:bcNames.nFeatures], genOut[...,-1,bcNames.nFeatures:]
    # print("X and Y shapes:", x.shape, y.shape)
    # tstr(x, y, "stateful_GAN")


def tstr(x, y, title): 
    allHomes = bcData.get_all_homes_as_xy_split_gen(
        batchSize=BATCH_SIZE, nTimesteps=N_TIME_STEPS,
        xyPivot=bcNames.pivots.activities.start, firstN=gv.DATA_AMT
    )
    model = basic_cnn()
    history = model.fit(x, y, epochs=EPOCHS, steps_per_epoch = STEPS_PER_EPOCH,
                        validation_data=allHomes[0].data.test.gen, validation_steps=defaults.VALIDATION_STEPS)
    test_result_0 = model.evaluate(allHomes[0].data.test.gen, steps=defaults.VALIDATION_STEPS, verbose=2)
    test_result_1 = model.evaluate(allHomes[1].data.test.gen, steps=defaults.VALIDATION_STEPS, verbose=2)
    test_result_2 = model.evaluate(allHomes[2].data.test.gen, steps=defaults.VALIDATION_STEPS, verbose=2)
    print(history.history)
    plt.figure()
    plt.title(title)
    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0, 1])
    plt.legend(loc='lower right')
    plt.savefig(PATH_ASSETS + "/img/accuracy/" + title + ".png")
    print(test_result_0[1])
    print(test_result_1[1])
    print(test_result_2[1])

def trtr(title):
    allHomes = bcData.get_all_homes_as_xy_split_gen(
        batchSize=BATCH_SIZE, nTimesteps=N_TIME_STEPS,
        xyPivot=bcNames.pivots.activities.start, firstN=gv.DATA_AMT
    )
    model = basic_cnn()
    history = model.fit(allHomes[0].data.train.gen, epochs=EPOCHS, steps_per_epoch = STEPS_PER_EPOCH,
                        validation_data=allHomes[0].data.test.gen, validation_steps=defaults.VALIDATION_STEPS)

    vals = []
    preds = []
    for i in range(1000):
        # tuple with (x, y) or (features, target). Target is the class, one-hot encoded
        vals.append(next(allHomes[0].data.train.gen))
        #here is one minibatch time-series of predictions
        #shape: (sample, time step, features)
        preds.append(model(vals[-1][0]))

    #now find a graph to visualize this: independent variables are the predictions (not the features) this is 14 variables, one prediction for each class
    #the dependent variable is the class label (1 variable with 14 options; the y part of (x, y) tuple)
    #I'd begin by considering a unique color for each of the 14 class labels.
    #tips: graph with Matplotlib, Seaborn; organize data with NumPy and Pandas
    #tsne can be used to visualize high-dimensional data in a few dimensions

    return



    # test_result_0 = model.evaluate(allHomes[0].data.test.gen, steps=defaults.VALIDATION_STEPS, verbose=2)
    # test_result_1 = model.evaluate(allHomes[1].data.test.gen, steps=defaults.VALIDATION_STEPS, verbose=2)
    # test_result_2 = model.evaluate(allHomes[2].data.test.gen, steps=defaults.VALIDATION_STEPS, verbose=2)
    # print(history.history)
    # plt.figure()
    # plt.title(title)
    # plt.plot(history.history['accuracy'], label='accuracy')
    # plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
    # plt.xlabel('Epoch')
    # plt.ylabel('Accuracy')
    # plt.ylim([0, 1])
    # plt.legend(loc='lower right')
    # plt.savefig(PATH_ASSETS + "/img/accuracy/" + title + ".png")
    # print(test_result_0[1])
    # print(test_result_1[1])
    # print(test_result_2[1])

def basic_cnn() -> keras.models.Model:
    inputLayer = keras.Input(shape=(N_TIME_STEPS, len(bcNames.features)))#should be 48 channels
    x = l.Dense(24, keras.activations.sigmoid)(inputLayer)
    x = cBlocks.conv_block(x, 24, defaults.leaky_relu(),) #8 timesteps
    x = cBlocks.conv_block(x, 15, defaults.leaky_relu()) #4 timesteps
    x = cBlocks.conv_block(x, 11, defaults.leaky_relu()) #2 timesteps
    x = cBlocks.conv_block(x, len(bcNames.allActivities), activation=keras.activations.softmax)
    x = l.Flatten()(x)
    model = keras.models.Model(inputLayer, x, name="Basic_CNN_Classifier")
    model.compile(loss = keras.losses.CategoricalCrossentropy(),
                  optimizer = defaults.optimizer(), metrics = ['accuracy'])
    return model

def rnn() -> keras.models.Model:
    inputLayer = keras.Input(shape=(N_TIME_STEPS, len(bcNames.features)))#should be 48 channels
    x = l.GRU(300)(inputLayer)
    x = l.Dropout(.2)(x)
    x = l.Dense(200)(x)
    x = l.Dropout(.2)(x)
    x = l.Dense(100)(x)
    x = l.Dense(100, activation='relu')(x)
    x = l.Dropout(.2)(x)
    x = l.Dense(len(bcNames.allActivities), activation = keras.activations.softmax)(x)
    model = keras.models.Model(inputLayer, x, name="RNN")
    model.compile(loss = keras.losses.CategoricalCrossentropy(),
                  optimizer = defaults.optimizer(), metrics = [keras.metrics.CategoricalAccuracy])
    return model

if __name__ == "__main__":
    if gv.DEBUG:
        # common.enable_tf_debug()
        pass
    trtr("trtr")