""""
Preprocessing data for the model
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy.signal as signal
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler

def remove_nan_values(registro):
    arr = registro.values
    arr = np.array(arr)
    arr = arr[~np.isnan(arr)]
    return arr

def normalize_data(registro):
    arr = registro.values
    arr = np.array(arr)
    arr = arr.reshape(-1, 1)
    scaler = StandardScaler()
    arr = scaler.fit_transform(arr)
    return arr

def remove_outliers(registro):
    arr = registro.values
    arr = np.array(arr)
    z = np.abs(stats.zscore(arr))
    arr = arr[(z < 3).all(axis=1)]
    return arr

def transform_data(registro, transformation):
    arr = registro.values
    arr = np.array(arr)
    if transformation == 'sqrt':
        arr2 = np.sqrt(arr)
    elif transformation == 'log':
        arr2 = np.log(arr)
    else:
        raise ValueError("Invalid transformation. Please choose 'sqrt' or 'log'.")
    
    fig, ax = plt.subplots(1,2, figsize = (9,4), dpi = 150, sharey = True)
    # Plot histogram of original data
    ax[0].hist(arr, bins=10, color='blue', alpha=0.5, label='Original Data')
    # Plot histogram of transformed data
    ax[1].hist(arr2, bins=10, color='red', alpha=0.5, label='Transformed Data')
    
    for i in range(2):
        ax[i].set_xlabel('Value')
        ax[i].set_ylabel('Frequency')
        ax[i].set_title('Histogram of Data')
        ax[i].legend()
    
    plt.show()
    return arr