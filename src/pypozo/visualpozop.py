import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import sys
import argparse


def simpleplotly(pozo, registro):
    nombre = pozo.name
    fig = go.Figure()

    registro = pozo.data[registro]

    profundidad = np.arange( registro.start, registro.stop, registro.step)

    fig.add_trace(go.Scatter(x=registro.values, y=profundidad, mode='lines', name=registro.mnemonic))
    fig.update_layout(title=nombre)
    fig.update_xaxes(title_text=registro.units)
    fig.update_yaxes(title_text='Profundidad (m)')
    fig.show()
    