from pypozo.processpozo import processdata

ruta = "data/PALO BLANCO 791_PROCESADO.las"
ruta2 = "data"

pozo = processdata(ruta)
pozo.simpleplot('GR')
larinov = pozo.larinov_vsh(plot = True)
brittlness = pozo.brittlness(plot = True)
pozo.savepozo(ruta2, 'PALOBLANCO791_REPROCESADO.las')

