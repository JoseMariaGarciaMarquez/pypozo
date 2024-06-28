import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style

style.use('Solarize_Light2')

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
    if registro.units == "OHMM":
        ax.set_xscale('log')
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
        if registro.units == "OHMM":
             axs[i].set_xscale('log')
        
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

def scatterplot_2d(pozo, registro1, registro2):
    """
    This function plots a 2D scatter plot between two curves.
    Use the curve mnemonics to plot them.
    """
    nombre = pozo.name
    registro1 = pozo.data[registro1]
    registro2 = pozo.data[registro2]
    profundidad = np.arange(registro1.start, registro1.stop, registro1.step)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    scatter = ax.scatter(registro1.values, profundidad, c=registro2.values, cmap='viridis')
    
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label('{} [{}]'.format(registro2.mnemonic, registro2.units), fontdict=font_axis)
    
    ax.set_xlabel('{} [{}]'.format(registro1.mnemonic, registro1.units), fontdict=font_axis)
    ax.set_ylabel('Depth [m]', fontdict=font_axis)
    ax.set_title('{} vs {}'.format(registro1.mnemonic, registro2.mnemonic), fontdict=font_title)
    ax.grid()
    plt.suptitle('---------------------------------------------------------------------------------------------------------------------------------------\n'
                 '|{}|\n'
                 '---------------------------------------------------------------------------------------------------------------------------------------\n\n'.format(nombre))
    plt.show()
