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
from pypozo.visualpozo import simpleplot


class processdata:
    def __init__(self, pozo):
        self.pozo = pozo
        self.nombre = self.pozo.name
        self.listaregistros = list(self.pozo.data.keys())
        print("{}\n{}".format(self.nombre, self.listaregistros))
            
    """"
    Section to process data ----------------------------------------------------------------------------------------------------
    """

    def larinov_vsh(self, plot=False):
        """
        Calculate the volume of shale using the Larionov equation.
        It is calculated based on GR and saved in the well as VSH-LAR.
        Calculate grindex, which is the normalized gamma ray index.
        And use the Larionov equation to calculate the volume of shale.
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
            simpleplot(self.pozo,'VSH-LAR')

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
        SW = (a/(phi.values**m*rt.values**n))
        self.pozo.data['SW_ARCHIE'] = SW

        if plot:
            self.simpleplot(self.pozo,'SW_ARCHIE')

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
            simpleplot(self.pozo,'BRITT')

        return brittlness
    

    def savepozo(self, ruta, nombre_archivo):
        """
        Save the well data to a LAS file.

        Parameters
        ----------
        ruta : str
            Path to save the LAS file.
        nombre_archivo : str
            Name of the LAS file.        
        """


        # Create LAS file object
        las = lasio.LASFile()

        # Define version section
        las.version = lasio.SectionItems([
            lasio.HeaderItem(mnemonic='VERS', unit='', value='2.0', descr='Version of LAS file'),
            lasio.HeaderItem(mnemonic='WRAP', unit='', value='NO', descr='Wrap mode')
        ])

        # Obtain depth information
        first_curve = next(iter(self.pozo.data.values()))
        depths = first_curve.basis
        
        # Check for NaN values in depths
        if any(map(lambda x: x is None or x != x, depths)):
            raise ValueError("Depths contain NaN values")

        # Ensure depths are sorted
        depths = sorted(depths)

        start_depth = depths[0]
        stop_depth = depths[-1]
        step = abs(depths[1] - depths[0])

        # Define well information
        well_info = [
            ('STRT', start_depth, 'M', 'START DEPTH'),
            ('STOP', stop_depth, 'M', 'STOP DEPTH'),
            ('STEP', step, 'M', 'STEP VALUE'),
            ('NULL', -999.25, '', 'NULL VALUE'),
            ('COMP', 'PyPozo', '', 'Company Name'),
            ('WELL', '{}'.format(self.pozo.name), '', 'Well Name'),
            ('PROV', 'Province', '', 'Province'),
            ('SRVC', 'Service Company', '', 'Service Company'),
            ('DATE', 'Date', '', 'Log Date'),
        ]
        las.well = lasio.SectionItems([lasio.HeaderItem(mnemonic=mnemonic, unit=unit, value=value, descr=descr) for mnemonic, value, unit, descr in well_info])

        # Add depth curve
        las.curves.append(lasio.CurveItem(mnemonic='DEPT', unit='M', data=depths, descr='Depth'))

        # Add other curves to LAS file
        for curve_name, curve in self.pozo.data.items():
            if curve_name == 'DEPT':
                continue  # Skip the depth curve as it's already added
            curve_data = curve.values
            unit = getattr(curve, 'unit', '')
            descr = getattr(curve, 'description', '')
            las.curves.append(lasio.CurveItem(mnemonic=curve_name, unit=unit, data=curve_data, descr=descr))

        # Define output path and save LAS file
        output_path = f"{ruta}/{nombre_archivo}.las"
        las.write(output_path, version=2.0)
        print(f"Archivo LAS guardado en: {output_path}")



