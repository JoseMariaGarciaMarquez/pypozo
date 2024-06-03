from welly import Well
from pypozo.visualpozo import simpleplot

ruta = "data/PALO BLANCO 791_PROCESADO.las"

pozo = Well.from_las(ruta)

simpleplot(pozo, 'GR')

