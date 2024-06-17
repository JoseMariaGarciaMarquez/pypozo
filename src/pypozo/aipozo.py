""""
AIpozo
This module is used to create a class
"""

import numpy as np
import tensorflow as tf
import scipy.stats as stats
import scipy.signal as signal

from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def fluidefficiency(Gc):
    fef = Gc/(2+Gc)
    return fef

def Gfunction():
    return None

def realldeepnetwork(n_inputs):
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(64, activation='relu', input_shape=(n_inputs,)))
    model.add(tf.keras.layers.Dense(64, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='linear'))
    return model    
    

""""
Only predictive models here
"""

def aifracking():
    """"
    Fracking model must have the next information:
    - Well logs Earth model:
        - GR
        - RES
        - DENSITY
        - NEUT
        - SONIC
    Optional:
        - BRITTLNESS 
    - General information:
    - Frac Fliud propierties:
        - Viscosity
        - Density
        - Volume

    """