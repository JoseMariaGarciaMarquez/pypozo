import numpy as np
import matplotlib.pyplot as plt



figsize = (6, 8)
dpi = 120
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


def poliplot(pozo, registros):
    """"
    This function plots multiple curves from the well data.
    Use the curve mnemonics to plot them.
    """

    nombre = pozo.name
    ancho = len(registros)*6
    alto = len(registros)*3

    fig, axs = plt.subplots(1, len(registros), figsize = (ancho, alto), dpi = dpi, sharey = True)
    axs[0].set_ylabel('Depth [m]', fontdict=font_axis)

    for i, registro in enumerate(registros):
        if isinstance(registro, str):
            registro = pozo.data[registro]
        profundidad = np.arange(registro.start, registro.stop, registro.step)
        
        axs[i].plot(registro.values, profundidad, label=registro.mnemonic)

        axs[i].set_xlabel('{}[{}]'.format(registro.mnemonic, registro.units), fontdict=font_axis)
        axs[i].set_title('{}'.format(registro.mnemonic), fontdict=font_title)
        axs[i].grid()
        axs[i].legend()
        
    axs[0].invert_yaxis()
    plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
                 '|{}|\n'
                 '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(nombre))

    plt.show()

def completeplot(pozo):
        nombre = pozo.name
        """
        This function plots all the curves from the well data.
        Recieves the well data as input.
        Returns a plot with all the curves.
        """

        registros = pozo.data.keys()
        lista_registros = list(registros)
        ancho = len(lista_registros)*6
        alto = 8
        fig, ax = plt.subplots(1,len(lista_registros), figsize = (ancho, alto), dpi = dpi, sharey = True)
        for i in range(len(lista_registros)):
            registro = pozo.data[lista_registros[i]]
            profundidad = np.arange( registro.start, registro.stop, registro.step)
            ax[i].plot(registro.values, profundidad)
            ax[i].set_xlabel('{}[{}]'.format(registro.mnemonic, registro.units), fontdict=font_axis)
            ax[i].set_title('{}'.format(registro.mnemonic), fontdict=font_title)
            ax[i].grid()
            ax[i].invert_yaxis()
        ax[0].set_ylabel('Depth [m]', fontdict=font_axis)


        plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
                 '|{}|\n'
                 '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(nombre))
        plt.show()
