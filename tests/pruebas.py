from welly import Well
from pypozo.processpozo import processdata
from pypozo import visualpozo

ruta = "data/PALO BLANCO 791_PROCESADO.las"
ruta2 = "data"

pozo = Well.from_las(ruta)

data = processdata(pozo)
visualpozo.simpleplot(pozo,'GR')
visualpozo.completeplot(pozo)
larinov = data.larinov_vsh(plot = True)
brittlness = data.brittlness(plot = True)
#archie = pozo.sw_archie(plot = True)
data.savepozo(ruta2, 'PALOBLANCO791_REPROCESADO')