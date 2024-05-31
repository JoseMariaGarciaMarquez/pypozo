from pypozo.potrero import pozodata

ruta01 = '/Users/Chemitas/Desktop/Desk/proyectos/pypozo/Pozos/datos/PALO BLANCO-791/PALO BLANCO 791_PROCESADO.las'
ruta02 = '/Volumes/T7 Shield/mac/UNAM/ultimo_semestre/Geofisica_integral/Proyecto/Abedul/Originales/70398_abedul1_bhc_1845_300_05mz79p.las'
ruta03 = '/Volumes/T7 Shield/mac/UNAM/ultimo_semestre/Geofisica_integral/Proyecto/Abedul/Originales/*.las'
rutasave = '/Users/Chemitas/Desktop/Desk/proyectos/pypozo/Pozos/datos/PALO BLANCO-791/save'

tipo1 = 'single'
tipo2 = 'multi'

pozito = pozodata(tipo1, ruta01)
abedul = pozodata(tipo2, ruta03)
curvas = ['GR', 'CALI', 'SP', 'SPHI']

pozito.simpleplot('GR')
pozito.dobleplot('GR', 'SW')
pozito.histplot('GR')
larinov = pozito.larinov_vsh('GR')
fragilidad = pozito.brittlness(plot=True)

pozito.savepozo(rutasave,'PALO-BLANCO')
registros2 = [
    ['GR'], ['SW']
]

pozito.coplot(registros2)





abedul.simpleplot('GR')
abedul.simpleplot('DT')
registros3 = [['GR'], ['DT'], ['SN', 'SP']]
abedul.coplot(registros3)


#abedul.savepozo(rutasave, 'ABEDUL-DEF')
#larinov_abedul = abedul.larinov_vsh('GR')

