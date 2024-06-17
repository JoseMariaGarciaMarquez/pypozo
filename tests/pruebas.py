from welly import Well
from pypozo.processpozo import processdata
from pypozo import visualpozo

ruta = "data/PALO BLANCO 791_PROCESADO.las"
ruta12 = "data/70449_abedul1_gn_1850_800_05mz79p.las"
ruta2 = "data"
ruta3 = "data/ABEDUL1_REPROCESADO.las"

pozo = Well.from_las(ruta)

data = processdata(pozo)
visualpozo.simpleplot(pozo,'M1R9')
larinov = data.larinov_vsh(plot = True)
brittlness = data.brittlness(plot = True)
registros = ["GR", "BRITT", "ZDEN", "CNCF", "DTC", "M1R6"]
visualpozo.poliplot(pozo, registros)


abedul = Well.from_las(ruta12)
data2 = processdata(abedul)
visualpozo.completeplot(abedul)
larinov2 = data2.larinov_vsh(plot = True)
registros2 = ["GR", "NEUT", "VSH-LAR"]
visualpozo.poliplot(abedul, registros2)
data2.savepozo(ruta2, 'ABEDUL1_REPROCESADO')

abedul2 = Well.from_las(ruta3)
data3 = processdata(abedul2)
visualpozo.completeplot(abedul2)