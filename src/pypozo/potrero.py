""""
Modulo unico
"""
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

class pozodata:
    def __init__(self, tipo, ruta) -> None:
        """"
        Clase que permite cargar un archivo .las y obtener la informacion de este   
        """
        self.tipo = tipo
        if self.tipo == 'single':
            self.pozo = Well.from_las(ruta)
            self.nombre = self.pozo.name
            print("Pozo {} cargado correctamente".format(self.nombre))
            
        elif self.tipo == 'multi':
            self.pozo = Project.from_las(ruta)
            self.nombre = self.pozo[0].name
            print("Pozo {} cargado correctamente".format(self.nombre))

        self.figsize = (5, 15)
        self.dpi = 110
        self.font_title = {'family': 'monospace', 'weight': 'bold', 'size': 20}
        self.font_axis = {'family': 'monospace', 'weight': 'bold', 'size': 15}
    """"
    Aqui se definen los metodos para visualizar los datos del pozo
    simpleplot: Grafica simple de las curvas del pozo
    dobleplot: Grafica doble de las curvas del pozo
    histplot: Histograma de las curvas del pozo
    boxplot: Boxplot de las curvas del pozo
    """
    def simpleplot(self, registro):
        """
        Grafica simple de las curvas del pozo
        Recibe el nombre de la curva a graficar
        Si el tipo de pozo es 'single' se recibe el nombre de la curva a graficar
        Si el tipo de pozo es 'multi' se recibe el objeto Curve a graficar, y la función busca
        en los archivos del pozo la curva con el mismo nombre, para unificarlas en un solo objeto Curve.
        """
        if isinstance(registro, str):

            if self.tipo == 'single':
                registro = self.pozo.data[registro]
                profundidad = np.arange( registro.start, registro.stop, registro.step)

            if self.tipo == 'multi':
                registro = self.unify_curves(registro)
                profundidad = np.arange( registro.start, registro.stop + registro.step, registro.step)

        
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

    def dobleplot(self, registro1, registro2):
        """
        Grafica doble de las curvas del pozo
        """
        if isinstance(registro1, str):
            registro1 = self.pozo.data[registro1]
        if isinstance(registro2, str):
            registro2 = self.pozo.data[registro2]

        profundidad = np.arange( registro1.start, registro1.stop, registro1.step)
        fig, ax = plt.subplots(figsize = self.figsize, dpi = self.dpi)
        ax.plot(registro1.values, profundidad, label = registro1.mnemonic)
        ax.plot(registro2.values, profundidad, label = registro2.mnemonic)
        ax.set_xlabel('{}[{}]'.format(registro1.mnemonic, registro1.units)  , fontdict=self.font_axis)
        ax.set_ylabel('Depth [m]', fontdict=self.font_axis)
        ax.set_title('{}'.format(registro1.mnemonic), fontdict=self.font_title)
        ax.grid()
        ax.invert_yaxis()
        ax.legend()
        plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
             '|{}|\n'
             '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(self.nombre))
        plt.show()

    def coplot(self, registros):
        """
        Grafica doble de las curvas del pozo
        """

        fig, axs = plt.subplots(1, len(registros), figsize = self.figsize, dpi = self.dpi, sharey = True)
        axs[0].set_ylabel('Depth [m]', fontdict=self.font_axis)

        for i, registro in enumerate(registros):
            for reg in registro:
                reg = self.pozo.data[reg]
                profundidad = np.arange(reg.start, reg.stop, reg.step)
                
                axs[i].plot(reg.values, profundidad, label=reg.mnemonic)

                axs[i].set_xlabel('{}[{}]'.format(reg.mnemonic, reg.units), fontdict=self.font_axis)
                axs[i].set_title('{}'.format(reg.mnemonic), fontdict=self.font_title)
                axs[i].grid()
                axs[i].legend()
        axs[0].invert_yaxis()
        plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
             '|{}|\n'
             '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(self.nombre))

        plt.show()

    def histplot(self, registro):
        """
        Histograma de las curvas del pozo
        """
        if isinstance(registro, str):
            registro = self.pozo.data[registro]

        fig, ax = plt.subplots(figsize = (6,6), dpi = 200)
        sns.histplot(registro.values, kde = True, ax = ax)
        ax.set(xlabel='{}[{}]'.format(registro.mnemonic, registro.units), ylabel='Frecuencia',
               title='Histograma de {}'.format(registro.mnemonic))
        plt.show()

    def boxplot(self, registro):
        """
        Boxplot de las curvas del pozo
        """
        if isinstance(registro, str):
            registro = self.pozo.data[registro]

        fig, ax = plt.subplots(figsize = (6,6), dpi = 200)
        sns.boxplot(registro.values, ax = ax)
        ax.set(xlabel='{}[{}]'.format(registro.mnemonic, registro.units),
               title='Boxplot de {}'.format(registro.mnemonic))
        plt.show()
    """"
    En esta seccion se definen los metodos para calcular el volumen de lutitas y la saturacion de agua entre otros cálculos
    """
    def larinov_vsh(self, plot=False):
        """
        Calcula el volumen de lutitas a partir de la ecuación de Larionov.
        Se calcula a partir de gr y se guarda en el pozo como VSH-LAR.
        Se calcula grindex que es el índice de rayos gamma normalizado.
        Y se usa la ecuación de Larionov para calcular el volumen de lutitas.
        vsh = 0.083*((2**(2*grindex) - 1))
        """
        
        if self.tipo == 'single':
            gr = self.pozo.data['GR']
        if self.tipo == 'multi':
            gr = self.unify_curves('GR')

        gr_cleanrock = min(gr.values)
        gr_shale = max(gr.values)
        grindex = (gr.values - gr_cleanrock) / (gr_shale - gr_cleanrock) 
        VSH = 0.083*((2**(2*grindex) - 1))
        vsh = Curve(data=VSH, index=gr.index, mnemonic='VSH-LAR', units='V/V')

        if self.tipo == 'single':
            self.pozo.data['VSH-LAR'] = vsh
        if self.tipo == 'multi':
            for i in range(len(self.pozo)):
                self.pozo[i].data['VSH-LAR'] = vsh
        
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
        self.pozo.data['SW'] = SW
        
        if plot:
            fig, ax = plt.subplots(figsize = (3,9), dpi = 200)
            profundidad = np.arange(phi.start, phi.stop, phi.step)
            ax.plot(SW, profundidad)
            ax.set(xlabel='SW[%]', ylabel='Depth [m]', title='Saturación de agua')
            ax.grid()
            ax.invert_yaxis()
            plt.show()
        
        return SW
    
    def sw_simandoux(self, rw, m=2, n=2, plot=False):
        """
        Calcula la saturación de agua a partir de la ecuación de Simandoux.
        """
        if 'PHIE' not in self.pozo.data or 'M1R6' not in self.pozo.data:
            raise ValueError("Se requieren los registros de Porosidad (PHI) y Resistividad (RT) para calcular la saturación de agua.")
        
        phi = self.pozo.data['PHIE']
        rt = self.pozo.data['M1R6']
        SW = (rw/(phi**m*rt**n))
        self.pozo.data['SW'] = SW
        
        if plot:
            fig, ax = plt.subplots(figsize = (3,9), dpi = 200)
            profundidad = np.arange(phi.start, phi.stop, phi.step)
            ax.plot(SW, profundidad)
            ax.set(xlabel='SW[%]', ylabel='Depth [m]', title='Saturación de agua')
            ax.grid()
            ax.invert_yaxis()
            plt.show()
        
        return SW

    def brittlness(self, plot=False):
        """
        Calcula el índice de brittleness a partir de la ecuación de Rickman.
        """
        if 'DTC' not in self.pozo.data or 'DTS' not in self.pozo.data:
            raise ValueError("Se requieren los registros de DTC y DTS para calcular el índice de brittleness.")

        dtc = self.pozo.data['DTC']
        brittlness = -0.012 * dtc.values + 1.4921
        self.pozo.data['BRITT'] = Curve(data=brittlness, index=dtc.index, mnemonic='BRITT', units='V/V')

        if plot:
            self.simpleplot('BRITT')

        return brittlness
    
    def correlacion(self, registro1, registro2):
        """
        Calcula la correlación entre dos registros.
        """
        if isinstance(registro1, str):
                registro1 = self.pozo.data[registro1]
        if isinstance(registro2, str):
                registro2 = self.pozo.data[registro2]
            
        correlacion = stats.pearsonr(registro1.values, registro2.values)
        return correlacion
    
    def savepozo(self, ruta, nombre_archivo):
        """
        Guarda el pozo en un archivo .las
        
        """

        las = lasio.LASFile()

        las.version = lasio.SectionItems([
            lasio.HeaderItem(mnemonic='VERS', unit='', value='2.0', descr='Version of LAS file'),
            lasio.HeaderItem(mnemonic='WRAP', unit='', value='NO', descr='Wrap mode')
        ])


        first_curve = next(iter(self.pozo.data.values()))
        depths = first_curve.basis
        start_depth = depths[-1]
        stop_depth = max(depths)
        step = depths[0] - depths[1]  


        well_info = [
            ('STRT', start_depth, 'M', 'START DEPTH'),
            ('STOP', stop_depth, 'M', 'STOP DEPTH'),
            ('STEP', step, 'M', 'STEP VALUE'),
            ('NULL', -999.25, '', 'NULL VALUE'),
            ('COMP', 'PyPozo', '', 'Company Name'),
            ('WELL', '{}'.format(self.pozo.name), '', 'Well Name'),
            #('FLD', '{}'.format(self.pozo.location.location), '', 'Field Name'),
            #('LOC', '{}'.format(self.pozo.location.location), '', 'Location'),
            ('PROV', 'Province', '', 'Province'),
            ('SRVC', 'Service Company', '', 'Service Company'),
            ('DATE', 'Date', '', 'Log Date'),
        ]
        las.well = lasio.SectionItems([lasio.HeaderItem(mnemonic=mnemonic, unit=unit, value=value, descr=descr) for mnemonic, value, unit, descr in well_info])


        for curve_name, curve in self.pozo.data.items():
            curve_data = curve.values
            unit = curve.unit if hasattr(curve, 'unit') else ''
            descr = curve.description if hasattr(curve, 'description') else ''
            las.curves.append(lasio.CurveItem(mnemonic=curve_name, unit=unit, data=curve_data, descr=descr))

        output_path = f"{ruta}/{nombre_archivo}.las"

        las.write(output_path, version=1.2)
        print(f"Archivo LAS guardado en: {output_path}")
    
    """

    """
    def unify_curves(self, registro):
        """
        Esta función permite unificar las curvas de un mismo pozo en un solo objeto Curve.
        Recibe el nombre de la curva a unificar y devuelve un objeto Curve con todas las curvas unificadas.

        """
        registros = []
        profundidades = []
        for i in range(len(self.pozo)):
            if registro in self.pozo[i].data:
                regis = self.pozo[i].data[registro]
                registros.append(regis)
                profundidades.append((regis.start, regis.stop))
            
        if not registros:
            raise ValueError(f"Registro '{registro}' no encontrado en ningún archivo.")
        
        max_prof = max(p[1] for p in profundidades)
        min_prof = min(p[0] for p in profundidades)
        
        step = registros[0].step
        profundidad = np.arange(min_prof, max_prof, step)
        
        valores_interpolados = np.full_like(profundidad, np.nan)
        
        for regis in registros:
            start_idx = int((regis.start - min_prof) / step)
            stop_idx = start_idx + len(regis.values)
            valores_interpolados[start_idx:stop_idx] = regis.values
        
        curva_unica = Curve(data=valores_interpolados, index=profundidad, mnemonic=registro, units=registros[0].units)
    
        return curva_unica

    def projecttocsv(self, registros, ruta, nombre_archivo):
        """
        Convierte un proyecto en un archivo csv
        """
        curvas = []
        headers = []
        profundidades = []

        for registro in registros:
            curva = self.unify_curves(registro)
            curvas.append(curva.values)
            headers.append(curva.mnemonic)
            profundidades.append((curva.start, curva.stop, curva.step))

        # Encontrar la longitud máxima de las curvas
        max_length = max(len(curva) for curva in curvas)

        max_prof = max(p[1] for p in profundidades)
        min_prof = min(p[0] for p in profundidades)
        # Crear la columna de profundidad (DEPTH)
        depth = np.linspace(min_prof, max_prof, max_length)  # Esto es un ejemplo. Ajusta según tus datos reales de profundidad

        # Rellenar las curvas más cortas con NaN
        for i in range(len(curvas)):
            if len(curvas[i]) < max_length:
                curvas[i] = np.pad(curvas[i], (0, max_length - len(curvas[i])), constant_values=np.nan)

        # Crear un diccionario con los datos, incluyendo la columna DEPTH
        data = {'DEPTH': depth}
        for i in range(len(headers)):
            data[headers[i]] = curvas[i]
        
        # Crear un DataFrame
        df = pd.DataFrame(data)
        
        # Guardar el DataFrame en un archivo CSV
        file_path = f"{ruta}/{nombre_archivo}.csv"
        df.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {file_path}")


    def projecttopozo(self, registros):
        """
        Convierte un proyecto en un pozo
        """
        curvas = []

        for registro in registros:
            curvas.append(self.unify_curves(registro))

        nuevo_pozo = Well()
        nuevo_pozo.location = self.pozo[0].location
        nuevo_pozo.name = self.pozo[0].name
        nuevo_pozo.uwi = self.pozo[0].uwi
        nuevo_pozo.data = dict(zip(registros, curvas))

        

        
        

        



