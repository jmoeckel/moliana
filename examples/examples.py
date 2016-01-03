# -*- coding: utf-8 -*-
"""
Small examples to show different usages of moliana.

@author: Jens Möckel
"""

import os
os.chdir('..')
import moliana
os.chdir('./example')

###############################################################################
def example1():
    """
    Usage of DymolaMode().
    - Applied to test_library
    - HTML report is generated with name 'example1' to directory 'reports'
    """

    pDym = os.path.join('C:\Program Files (x86)\Dymola 2016\\bin64','Dymola.exe')
    pLib = 'test_library'

    dlc = moliana.DymolaMode(pLib, pDym, report_name ='example1', report_path = 'reports')
    dlc.execute_check('html')

    return True

def example2():
    """
    Usage of DymolaMode().
    - Applied to test_library
    - HTML report is generated with name 'example2' to directory 'reports'
    - Level of Detail set to 3
    """

    pDym = os.path.join('C:\Program Files (x86)\Dymola 2016\\bin64','Dymola.exe')
    pLib = 'test_library'

    rp_name = 'example2'
    rp_path = 'reports'
    lod = 3

    dlc = moliana.DymolaMode(pLib, pDym, report_name = rp_name, report_path = rp_path, modelica_lib_depth = lod)
    dlc.execute_check('html')

    return True

def example3():
    """
    Usage of DymolaMode().
    - Applied to test_library
    - HTML report is generated with name 'example3' to directory 'reports'
    - Level of Detail set to 3
    - First Level is set to L1Pck1
    """

    pDym = os.path.join('C:\Program Files (x86)\Dymola 2016\\bin64','Dymola.exe')
    pLib = 'test_library'

    options = {'report_name' : 'example3',
               'report_path' : 'reports',
               'modelica_lib_depth' : 3,
               'modelica_lib_firstlevel' : 'L1Pck1'}

    dlc = moliana.DymolaMode(pLib, pDym, **options)
    dlc.execute_check('html')

    return True

def example4():
    """
    Usage of DymolaMode().
    - Applied to test_library
    - HTML report is generated with name 'example41' to directory 'reports'
    - HTML report is generated with name 'example42' to directory 'reports'
    - Second Report has different colors
    - Same DymolaMode instance is used.
    """

    pDym = os.path.join('C:\Program Files (x86)\Dymola 2016\\bin64','Dymola.exe')
    pLib = 'test_library'

    options = {'report_name' : 'example41',
               'report_path' : 'reports'}

    #First check
    dlc = moliana.DymolaMode(pLib, pDym, **options)
    dlc.execute_check('html')

    #Second Check
    dlc.report_name = 'example42'
    dlc.report_colors = {'cFalse': 'blue'}
    dlc.execute_check('html')

    return True

def example5():
    """
    Usage of Report():
    - Applied to report 'example1.html'
    - read in data
    - change disp and convert back to html as 'example5.html'
    """

    rep = moliana.Report()
    rep.read_html(os.path.join('reports','example1.html'))

    rep.name = 'example5'
    rep.disp.append({'Key':'This line', 'Val':'is new'})
    rep.generate_html()

    return True

def example6():
    """
    Usage of Report():
    - comparison of two reports 'example6.html' (which is a manually altered
      copy of 'example2.html')
    - an HTML-report 'example6_compare.html' is generated to 'reports'
    """

    rep1 = moliana.Report()
    rep1.name = 'example6'
    rep1.path = 'reports'
    rep1.read_html()

    rep2 = moliana.Report()
    rep2.name = 'example2'
    rep2.path = 'reports'
    rep2.read_html()

    rep1.compare_to(rep2)

    return True

def example7():
    """
    Usage of Converter():
    - convert 'example6.html' into a report()
    - after that converts back to a html file ('example7.html')
    """
    conv = moliana.Converter()

    rep = conv.html_to_report(os.path.join('reports','example6.html'))
    rep.name = 'example7'

    conv.report_to_html(rep)

    return True

if __name__ == "__main__":
    example1()
