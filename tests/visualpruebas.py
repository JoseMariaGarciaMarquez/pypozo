""""
In this file we will test the visualpozo module
How to use visualpozo:
1. Import the module
2. Call the simpleplot function
3. Pass the well object and the curve mnemonic as arguments
4. Run the script
"""

from welly import Well
from pypozo import visualpozo

ruta = "data/PALO BLANCO 791_PROCESADO.las"

pozo = Well.from_las(ruta)

visualpozo.simpleplot(pozo, 'GR')
visualpozo.completeplot(pozo)

registros = ['GR', 'CAL', 'SP', 'SW', 'VPVS']
registros2 = ['GR', 'CAL', 'SP', 'DPHI', 'PHIE', 'SW', 'VPVS', 'POISDIN', 'FRAC_NAT', 'FRAC_IND', 'DTC', 'DTS', 'SPHI', 'ZDEN', 'BRITT']
visualpozo.poliplot(pozo, registros)
