from pypozo.processpozo import processdata

ruta = "data/PALO BLANCO 791_PROCESADO.las"

pozo = processdata(ruta)
pozo.simpleplot('GR')

