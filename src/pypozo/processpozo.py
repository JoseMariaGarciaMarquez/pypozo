import lasio
import welly
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt

from welly import Well
from welly import Curve
from welly import Project


class processdata:
    def __init__(self, lasfile):
        self.pozo = Well.from_las(lasfile)
        self.figsize = (5, 15)
        self.dpi = 110
        self.font_title = {'family': 'monospace', 'weight': 'bold', 'size': 20}
        self.font_axis = {'family': 'monospace', 'weight': 'bold', 'size': 15}
    
    """"
    Section to plot data
    """
    def simpleplot(self, registro):
        """
        This function plots a single curve from the well data.
        Use the curve mnemonic to plot it.
        """
        if isinstance(registro, str):
            registro = self.pozo.data[registro]
            

        profundidad = np.arange( registro.start, registro.stop, registro.step)
        fig, ax = plt.subplots(figsize = self.figsize, dpi = self.dpi)
        ax.plot(registro.values, profundidad)
        ax.set_xlabel('{}[{}]'.format(registro.mnemonic, registro.units), fontdict=self.font_axis)
        ax.set_ylabel('Depth [m]', fontdict=self.font_axis)
        ax.set_title('{}'.format(registro.mnemonic), fontdict=self.font_title)
        ax.grid()
        ax.invert_yaxis()
        plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
             '|{}|\n'
             '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(self.nombre))
        plt.show()

    """"
    Section to process data
    """

    def larinov_vsh(self, plot=False):
        """
        Calcula el volumen de lutitas a partir de la ecuación de Larionov.
        Se calcula a partir de gr y se guarda en el pozo como VSH-LAR.
        Se calcula grindex que es el índice de rayos gamma normalizado.
        Y se usa la ecuación de Larionov para calcular el volumen de lutitas.
        vsh = 0.083*((2**(2*grindex) - 1))
        """
        
        gr = self.pozo.data['GR']


        gr_cleanrock = min(gr.values)
        gr_shale = max(gr.values)
        grindex = (gr.values - gr_cleanrock) / (gr_shale - gr_cleanrock) 
        VSH = 0.083*((2**(2*grindex) - 1))
        vsh = Curve(data=VSH, index=gr.index, mnemonic='VSH-LAR', units='V/V')


        self.pozo.data['VSH-LAR'] = vsh

        
        if plot:
            self.simpleplot('VSH-LAR')

        return vsh
    
    def sw_archie(self, a=1, m=2, n=2, plot=False):
        """
        Calcula la saturación de agua a partir de la ecuación de Archie.
        a = exponente de cementación
        m = exponente de la porosidad
        n = exponente de la resistividad
        """
        if 'PHIE' not in self.pozo.data or 'M1R6' not in self.pozo.data:
            raise ValueError("Se requieren los registros de Porosidad (PHI) y Resistividad (RT) para calcular la saturación de agua.")
        
        phi = self.pozo.data['PHIE']
        rt = self.pozo.data['M1R6']
        SW = (a/(phi**m*rt**n))
        self.pozo.data['SW_ARCHIE'] = SW

        if plot:
            self.simpleplot('SW_ARCHIE')

        return SW
    
    def brittlness(self, plot=False):
        """
        This function calculates the brittlness index from the DTC curve.
        DTC is the compressional wave velocity.
        The brittlness index is calculated as:
        brittlness = -0.012 * DTC + 1.4921
        """
        if 'DTC' not in self.pozo.data or 'DTS' not in self.pozo.data:
            raise ValueError("DTC or DTS curves are required to calculate brittlness.")

        dtc = self.pozo.data['DTC']
        brittlness = -0.012 * dtc.values + 1.4921
        self.pozo.data['BRITT'] = Curve(data=brittlness, index=dtc.index, mnemonic='BRITT', units='V/V')

        if plot:
            self.simpleplot('BRITT')

        return brittlness