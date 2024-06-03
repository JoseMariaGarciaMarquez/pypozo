import numpy as np
import matplotlib.pyplot as plt



figsize = (5, 15)
dpi = 110
font_title = {'family': 'monospace', 'weight': 'bold', 'size': 20}
font_axis = {'family': 'monospace', 'weight': 'bold', 'size': 15}


def simpleplot(pozo, registro):
        nombre = pozo.name            
        """
        This function plots a single curve from the well data.
        Use the curve mnemonic to plot it.
        """
        if isinstance(registro, str):
            registro = pozo.data[registro]

        profundidad = np.arange( registro.start, registro.stop, registro.step)
        fig, ax = plt.subplots(figsize = figsize, dpi = dpi)
        ax.plot(registro.values, profundidad)
        ax.set_xlabel('{}[{}]'.format(registro.mnemonic, registro.units), fontdict=font_axis)
        ax.set_ylabel('Depth [m]', fontdict=font_axis)
        ax.set_title('{}'.format(registro.mnemonic), fontdict=font_title)
        ax.grid()
        ax.invert_yaxis()
        plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
                 '|{}|\n'
                 '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(nombre))
        plt.show()
