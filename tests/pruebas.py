from pypozo.processpozo import processdata
from pypozo.visualpozo import simpleplot

ruta = "data/PALO BLANCO 791_PROCESADO.las"
ruta2 = "data"

pozo = processdata(ruta)
#simpleplot(pozo,'GR')
larinov = pozo.larinov_vsh(plot = True)
brittlness = pozo.brittlness(plot = True)
#archie = pozo.sw_archie(plot = True)
pozo.savepozo(ruta2, 'PALOBLANCO791_REPROCESADO')

