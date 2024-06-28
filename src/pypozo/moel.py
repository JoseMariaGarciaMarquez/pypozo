import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from welly import Well
from welly import Synthetic
from pypozo.processpozo import processdata

def realldeepnetwork(n_inputs):
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(64, activation='relu', input_shape=(n_inputs,)))
    model.add(tf.keras.layers.Dense(64, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='linear'))
    return model
   
ruta = "data/PALO BLANCO 791_PROCESADO.las"
palo = Well.from_las(ruta)

gr = palo.data['GR']
sp = palo.data['SP']
dt = palo.data['DT']

modelo = realldeepnetwork(3)