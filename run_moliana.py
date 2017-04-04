import os
import moliana

pDym = os.path.join('C:\Program Files (x86)\Dymola 2017 FD01\\bin64','Dymola.exe')

pLib = 'Q:\\Git\\AMSUN\\HumanBehaviour'

rp_name = 'report'

dm = moliana.DymolaMode(pLib, pDym, report_name = rp_name)
dm.execute_check('html')