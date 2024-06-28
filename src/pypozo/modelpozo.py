""""
ModelPozo
"""

import numpy as np
import gempy as gp
import matplotlib.pyplot as plt

def earthmodeling():
    """"
    This function is to create a geological model for a well.
    """

def create_model():
    # Create a model
    geo_model = gp.create_model('Modelo de Pozo')
    geo_model = gp.init_data(geo_model, [0, 1000, 0, 1000, 0, 1000], [50, 50, 50],
                             path_o = "Modelo de Pozo_orientations.csv",
                             path_i = "Modelo de Pozo_surface_points.csv")
    geo_model = gp.map_series_to_surfaces(geo_model,
                                          {"Strat_Series": ('rock2', 'rock1'), "Basement_Series": ('basement')})
    geo_model = gp.set_is_fault(geo_model, {'Fault1': 'fault'})
    geo_model.surfaces.colors.change_colors({'rock1': '#015482', 'rock2': '#9f0052', 'fault': '#ffbe00', 'basement': '#728f02'})
    gp.plot.plot_data(geo_model, direction='y')
    gp.plot.plot_data(geo_model, direction='x')
    gp.plot.plot_data(geo_model, direction='z')
    gp.plot.plot_data_3D(geo_model)
    return geo_model