# -*- coding: utf-8 -*-
#
# Copyright (C) 2016  Jens Möckel <moeckeljens@googlemail.com>, All Rights
# Reserved
#
# Implemented by Jens Möckel
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
"""
MOLIANA - MOdelica LIbrary ANAlyser for Dymola.

Analysation of modelica libraries based on Dymolas checkModel()

This module provides
    DymolaMode():
        Automated execution of Dymolas checkModel()

    Report():
        Representation of results

    Converter():
        Converts content of Report instances to HTML files and vice versa

EXAMPLES:
Several examples are provided on 'https://github.com/jmoeckel/moliana/wiki/Examples'.

API:
Each class contains a full documentation of the provided API. Furthermore, an
overview is given on 'https://github.com/jmoeckel/moliana/wiki/UserInterface'.

SOFTWARE REQUIREMENTS:
- This module has been implemented and tested with Python 3.4.3 on a Windows 7
  and Windows 10 platform
- DymolaMode requires Dymola 2016 or newer.
"""

import os;
import subprocess;
import sys
import re
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('Moliana')

logger.info('Welcome to Moliana')

##############################################################################
class DymolaMode(object):
    """
    Returns a new DymolaMode instance.

    Instance provides the possibility to apply automated Dymolas checkModel()
    to a Modelica library.

    NOTE:
    This will only work with Dymola 2016 and newer as the Dymola fuction
    'getLastError' does not provide necesary information in older versions.

    ATTRIBUTES:
    modelica_lib_path (string):
        Path to a Modelica library

    dymola_path(string):
        Path to the Dymola installation, e.g. dymola.exe

    OPTIONAL ATTRIBUTES:
    dymola_pedantic (bool, default=False):
        If true, checkModel() is executed in pedantic mode

    modelica_lib_firstlevel (string, default=''):
        A subpackage of the library. checkModel() is applied to this package
        (and all packages/models in this one).
        Note, that if your chosen Top-Level package is e.g. a third-level
        package, modelica_lib_firstlevel must include the complete path in the
        library.
        Example:
        Given structure: lib > A > B. Then:
        modelica_lib_path = '...\lib'
        modelica_lib_firstlevel = 'A\B'

    modelica_lib_depth (int, default=1):
        How many levels should be listet in the report, e.g. level 1 will list
        all top-level packages/models, level 2 additionally all second-level
        packages/models and so on.
        Note1:
            Level of displayed packageshas no influence on how many levels are
            actually checked - checkModel() is always applied to all packages/
            models in modelica_lib_firstlevel
        Note2:
            Setting modelica_lib_depth to '-1' will show all packages/models in
            the report.

    report_path(string, default=[chosen first level]):
        path attribute of a report instance

    report_name (string, default='report'):
        name attribute of a report instance

    report_mode (string, default='full'):
        mode attribute of a report instance

    report_disp (list of dictionaries, default=
                    [{'Key':'Checked Library', 'Val':[chosen first level in Modelica syntax]},
                     {'Key':'Pedantic Mode', 'Val': self.dymola_pedantic},
                     {'Key':'Level of Detail', 'Val': self.modelica_lib_depth}])):
                     {'Key':Branch', 'Val': [Either name of branch or 'no git']}
        disp attribute of a report instance

    report_colors (dictionary, default={'cTrue':'white','cFalse':'red', 'cNF':'yellow','cErr':'red','cWrn':'yellow'})
        colors attribute of a report instance

    For more detailled informations regardings the reports attributes, take a
    look a the documentation of the report class

    API:
    execute_check():
        Applies Dymolas checkModel() on given library (modelica_lib_path) or
        respectively chosen top level package (modelica_lib_firstlevel).

    get_report():
        Returns the current Report instance.

    For more details take a look at the module itsself
    """

    def __init__(self, modelica_lib_path, dymola_path, **kwargs):

                      
        self.modelica_lib_path = os.path.abspath(modelica_lib_path)
        self.dymola_path = dymola_path

        #list of all options
        self._options = ['dymola_pedantic', 'modelica_lib_firstlevel',
                         'modelica_lib_depth', 'git_mode', 'report_path',
                         'report_name', 'report_mode', 'report_disp',
                         'report_colors']

        #check if all options are allowed
        _Validator('general_kwargs',kwargs,self._options)

        #fill non chosen options with None
        for option in self._options:
             if not option in kwargs:
                 kwargs[option] = None


        #initialize options with user input or default values
        self.dymola_pedantic = kwargs['dymola_pedantic'] or False
        self.modelica_lib_firstlevel = os.path.join(self.modelica_lib_path, kwargs['modelica_lib_firstlevel'] or '')
        self.modelica_lib_depth =  kwargs['modelica_lib_depth'] or 1

        #initialize report attributes
        self.report_name = kwargs['report_name']
        self.report_path = kwargs['report_path']
        self.report_mode = kwargs['report_mode']
        self.report_colors = kwargs['report_colors']
        self.report_disp = kwargs['report_disp']

        #additional variables
        self._Report = Report()
        self._modelica_lib_firstlevel_mosyntax =  self.modelica_lib_firstlevel.replace(os.path.dirname(self.modelica_lib_path)+'\\','').replace('\\','.')



        if self._modelica_lib_firstlevel_mosyntax[-1]=='.':
            self._modelica_lib_firstlevel_mosyntax = self._modelica_lib_firstlevel_mosyntax[:-1]


    #PUBLIC API
    ###########################################################################
    def execute_check(self, flag=None):
        """
        Applies Dymolas checkModel() to chosen packages/models.

        ARGUMENTS:
        flag (string, default=None)
            If flag is 'html', an HTML report is generated.

        RETURNS:
        A Report instance, which contains the results of the check.
        """
        
        # sample all considered models and adapt the path for Dymola-internal use
        dirpath = os.path.join(self.modelica_lib_path, self.modelica_lib_firstlevel)
        models = self._get_models_of_modelica_library_recursively(dirpath,[])
        models = [model.replace(self.modelica_lib_path, os.path.basename(self.modelica_lib_path)).replace('\\','.') for model in models]

        # open Dymola and load Library
        dymola = self._establish_dymola_connection()
        
        #check recursivley the library
        results = []
        logger.info('Starting to check models. Checking ...')
        for model in models:
            logger.info('... {}'.format(model))
            dic = self._executing_dymola_checkModel(dymola, model)
            results.append(dic)
        logger.info('Finished ({} models have been checked)'.format(len(models)))

        #fill report element with data from logfile
        self._fill_report(results)
        
        #cleaning up        
        self._cleanUp(dymola)

        if flag == 'html':
            self._Report.generate_html()

        return self._Report


    def get_report(self):
        """
        Returns the current Report instance of the DymolaMode instance

        RETURNS:
        Report instance
        """

        return self._Report


    #PRIVATE API
    ###########################################################################
    def _establish_dymola_connection(self):
        """
        Establish connection to Dymola and load chosen library.
        Also parameter 'Advanced.PedanticModelica' is set.
        
        RETURNS:
        dymola: an instance of the DymolaInterface
        """

        logger.info('Establishing connection to Dymola ...')
        sys.path.append(os.path.join(self.dymola_path, 'Modelica\\Library\\python_interface\\dymola.egg'))
        from dymola.dymola_interface import DymolaInterface        
        logger.info('... Done')
        
        #open Dymola
        logger.info('Instantiating Dymola interface ...')
        dymola = DymolaInterface()
        logger.info('... Done')
        
        #activate Modelica pedantic check   
        dymola.ExecuteCommand("Advanced.PedanticModelica = {}".format(self.dymola_pedantic))
        
        #open library     
        logger.info('Loading Modelica library ...')
        success = dymola.openModel(os.path.join(self.modelica_lib_path,'package.mo'))
        if success:
            logger.info('... Done')
        else:
            logger.error('... Library not loaded')
                
        
        return dymola

        
    def _get_models_of_modelica_library_recursively(self, curPckDP, models):
        """
        Recursively assembling paths of all to be considered packages/models up
        to the chosen level of detail.

        ARGUMENTS:
        curPckDP: path to a directory, which must be a package, e.g. containing
                  a file package.order (string)
        RETURNS:
        models: list of considered models
        """
    
        if not os.path.exists(os.path.join(curPckDP, 'package.order')):
            return
        
        with open(os.path.join(curPckDP, 'package.order')) as file:
            lContent = file.read().splitlines()
            
        for elem in lContent:
    
            # path for filesystem
            pCurEl = os.path.join(curPckDP,elem)
    
            # if it is dir/pck -> go one step further,
            # if not, it is a mo file -> add to list
            if os.path.isdir(pCurEl):
                self._get_models_of_modelica_library_recursively(pCurEl,models)
    
            else:
                models.append(pCurEl)
                
        return models
        

    def _executing_dymola_checkModel(self, dymola, model):
        """
        Applied Dymolas checkModel() to a given package/model.
        Results are written to a .log file (this is executed within Dymola).

        ARGUMENT:
        dymola: an instance of DymolaInterface
        model: string, path of considered model in Modelica notification
        
        RETURNS:
        dic, dictionary, that contains the results of a test
        """

        success = dymola.checkModel(model)
        lerr = dymola.getLastError()
        
        nErr = len(re.findall('Error:', lerr))
        nWrn = len(re.findall('Warning:', lerr))    
        
        if not success:
            res = False
        elif nWrn > 0:
            res = True
        else:
            res = True
            
        lines = lerr.splitlines()
        if not success and nErr == 0:
            notes = [lines[1]]
        elif nErr > 0 or nWrn > 0:
            notes = [line for line in lines if line.startswith('Error:') or line.startswith('Warning:')]
        else:
            notes = []
        

        dic = {'Pck': model.replace('{}.'.format(self._modelica_lib_firstlevel_mosyntax),''),
           'Res': res,
           'Err': nErr,
           'Wrn': nWrn,
           'Notes': '<br/>'.join(notes), 
           'colPck': 'white',
           'colRes': '{}'.format(self._Report.colors['cTrue'] if res ==True else self._Report.colors['cFalse']),
           'colErr': '{}'.format('white' if nErr==0 else self._Report.colors['cErr']),
           'colWrn': '{}'.format('white' if nWrn==0 else self._Report.colors['cWrn'])
           }     
        
        return dic


    def _fill_report(self, results):
        """
        Report instance is filled with all available informations.
        """

        # set reports attributes equal to user settings or default values
        self._Report.name = self.report_name or 'report'
        self._Report.path = self.report_path or self.modelica_lib_firstlevel
        self._Report.mode = self.report_mode or 'full'
        self._Report.disp = self.report_disp or [{'Key': 'Checked Library', 'Val': self._modelica_lib_firstlevel_mosyntax},
                                                 {'Key': 'Pedantic Mode', 'Val': self.dymola_pedantic},
                                                 {'Key': 'Level of Detail', 'Val': self.modelica_lib_depth},
                                                 {'Key': 'Branch', 'Val': self._get_branch(self.modelica_lib_path)}]

        # set meta data
        self._Report.meta = {'pck': self._modelica_lib_firstlevel_mosyntax,
                             'ped': self.dymola_pedantic,
                             'lod': self.modelica_lib_depth,
                             'git': self._get_branch(self.modelica_lib_path),
                             'viewport': 'width=device-width, initial-scale=1.0, user-scalable=yes'}

        # replace default colors with user input
        if self.report_colors:
            for key in self.report_colors:
                self._Report.colors[key] = self.report_colors[key]

        # add results to _Report
        self._Report.cont = results
        

    def _get_branch(self,modelica_lib_path):
        """
        Get the current branch of the git repository (if the chosen library is
        actually one).

        ARGUMENTS:
        modelica_lib_path (string):
            path of the modelica library.

        RETURNS:
        branch (string):
            if modelica_lib_path is a git repository =>name of the current HEAD
            else: empty string.
        """

        currentDir = os.getcwd();
        os.chdir(modelica_lib_path)
        try: 
           s = subprocess.check_output('git branch',universal_newlines=True) 
           
           branch = s[s.find('*')+1:s.find('\n',s.find('*'))].strip()
        except:
           branch = 'no git'

        os.chdir(currentDir)
        return branch
        

    def _cleanUp(self, dymola):
        """
        Several actions after finishing the library check, e.g. closing Dymola        
        """
        
        logger.info('Cleaning up')
        
        #close dymola
        dymola.close()



    ###########################################################################
    #PYTHON-LIKE GETTER AND SETTER METHODS
    ###########################################################################
    @property
    def dymola_path(self):
        return self.__dymola_path

    @dymola_path.setter
    def dymola_path(self,s):
        _Validator('dymola_path',s)
        self.__dymola_path = s

    @property
    def dymola_pedantic(self):
        return self.__dymola_pedantic

    @dymola_pedantic.setter
    def dymola_pedantic(self,s):
        _Validator('dymola_pedantic',s)
        self.__dymola_pedantic = s

    @property
    def modelica_lib_path(self):
        return self.__modelica_lib_path

    @modelica_lib_path.setter
    def modelica_lib_path(self,s):
        _Validator('modelica_lib_path',s)
        self.__modelica_lib_path = s

    @property
    def modelica_lib_firstlevel(self):
        return self.__modelica_lib_firstlevel

    @modelica_lib_firstlevel.setter
    def modelica_lib_firstlevel(self,s):
        _Validator('modelica_lib_firstlevel',s)
        self.__modelica_lib_firstlevel = s

    @property
    def modelica_lib_depth(self):
        return self.__modelica_lib_depth

    @modelica_lib_depth.setter
    def modelica_lib_depth(self,n):
        _Validator('modelica_lib_depth',n)
        self.__modelica_lib_depth = n

    @property
    def report_name(self):
        return self.__report_name

    @report_name.setter
    def report_name(self,s):
        _Validator('report_name',s)
        self.__report_name = s

    @property
    def report_path(self):
        return self.__report_path

    @report_path.setter
    def report_path(self,s):
        _Validator('report_path',s)
        self.__report_path = s

    @property
    def report_mode(self):
        return self.__report_mode

    @report_mode.setter
    def report_mode(self,s):
        _Validator('report_mode',s)
        self.__report_mode = s

    @property
    def report_disp(self):
        return self.__report_disp

    @report_disp.setter
    def report_disp(self,lst):
        _Validator('report_disp',lst)
        self.__report_disp = lst

    @property
    def report_colors(self):
        return self.__report_colors

    @report_colors.setter
    def report_colors(self,dic):
        _Validator('report_colors',dic)
        self.__report_colors = dic


class Report(object):
    """
    Returns a new Report instance. Each attribute is initialized as None
    (except for colors).

    ATTRIBUTES:
    path (string, default=None):
        Path to the directory, where the report file should be stored.

    name (string, default=None):
        Name of the report (without file extension).

    disp (list of dictionaries default=None):
        Key-value pairs of informations, that should be printed to the report.
        Mandatory keys: 'Key', 'Val',
        Example: disp = [{'Key':'Library', 'Val':Lib},
                         {'Key':'Pedantic Mode', 'Val':False},
                         {'Key':'Level of Detail', 'Val':1}]

    cont (list of dictionaries, default=None):
        Content of the report, so the actual results of the check including
        color informations for each result.
        Mandatory keys: 'Pck', 'Res', 'Err', 'Wrn'
        Example: cont = [{'Pck':Lib, 'Res':'True', 'Err':'9', 'Wrn':'2'}]

    mode (string, default=None):
        Either an HTML report only contains the name of the package/model and
        the result (mode='compact') or there are two more columns giving the
        numbers of errors and warnings (mode='full').

    meta (dictionairy, default=None):
        Meta informations, which are used, if the report instance should be
        compared to another instance. These informations are also stored in the
        HTML report.
        Mandatory keys:
            'pck' (path of checked library)
            'ped' (Dymola checkModel() mode)
            'lod' (level of detail)
            'viewport' (viewoptions for html)

    colors (dictionary, default= {'cTrue':'white','cFalse':'red', 'cNF':'yellow','cErr':'red','cWrn':'yellow'})
        Background colors of cells in the HTML report.
        Mandatory keys:
            'cTrue' (cells in the result-column, which contain the keyword 'True')
            'cFalse' (cells in the result-column, which contain the keyword 'False')
            'cNF' (cells in the result-column, which contain the keyword 'Not found')
            'cErr' (cells in the errors-column, which have entries greater than 0)
            'cWrn' (cells in the warnings-column, which have entries greater than 0)


    API:
    generate_html():
        An HTML file is generated, which contains two tables. First table gives
        an overview over chosen options, second table displays row-wise results
        of checkModel() applied on some packages/models.

    read_html(filepath=None):
        A HTML file, which must correspond to the structure given by
        generate_html(), is parsed and its content set as values of the report
        instance.
        If filepath is not given, this reports name and path are checked for a
        HTML file.

    compare_to(rep2):
        Results of this report instance are compared to results of report
        instance rep2. Both report instances must correspond to the same
        library, the same level of detail and the same dymola checkModel()
        mode.

    For more details take a look at the module itsself
    """

    def __init__(self, **kwargs):

        #allowed options
        options = 'name path disp cont mode meta colors'.split()

        #check if all options are allowed
        _Validator('general_kwargs', kwargs, options)

        #fill non chosen options with none
        for option in options:
             if not option in kwargs:
                 kwargs[option] = None

        #set default values
        self.name = kwargs['name']
        self.path = kwargs['path']
        self.disp = kwargs['disp']
        self.cont = kwargs['cont']
        self.mode = kwargs['mode']
        self.meta = kwargs['meta']
        self.colors = kwargs['colors'] or {'cTrue':'white',
                                           'cFalse':'red',
                                           'cNF':'yellow',
                                           'cErr':'red',
                                           'cWrn':'yellow'}


    #PUBLIC API
    ###########################################################################
    def generate_html(self):
        """
        Generates an HTML file, which contains the infomations given by the
        report instance. Informations are displayed table-wise.
        """

        conv = Converter()
        conv.report_to_html(self)


    def read_html(self, filepath=None):
        """
        Parses a given HTML file (based on name and path) and stores available
        information within the report instance.

        OPTIONAL ARGUMENT:
        filepath (string):
            path to a report-html file. If not given, reports name and path
            attribute are used.
        """

        _filepath = os.path.abspath(filepath or '{}.html'.format(os.path.join(self.path,self.name)))
        _Validator('general_filepath','HTML-path',_filepath)

        conv = Converter()
        name, path, disp, cont, meta, mode = conv.html_to_report_attributes(_filepath)
        self.name = name
        self.path = path
        self.disp = disp
        self.cont = cont
        self.meta = meta
        self.mode = mode


    def compare_to(self,rep2):
        """
        Compares this Report instance to the the instance rep2. An HTML is
        generated, which have the same layout as the usual HTML report, but
        uses different colors:
        If a result of this Report instance is better than the one of of rep2,
        the corresponding cell's background color is set to green.
        If the result is worse, the cell's background color is set to red.
        If there is no change, cell's background color remains white.

        The new report has an additonal information, to which instance it has
        been compared.

        ARGUMENTS:
        rep2 (Report):
            A Report instance, which is compare to the self instance

        RETURNS:
        A HTML file is generated which displays the results of the comparison.
        The filename is '[self.name]_compare.html'
        """

        #ensure, that rep2 is a valid report instance
        _Validator('report',rep2)
        _Validator('report_compare',self,rep2)

        rep1 = self
        for dic1 in rep1.cont:
            pck = dic1['Pck']
            dic2 = next((item for item in rep2.cont if item['Pck'] == pck),None)

            if dic2 == None:
                #pck does not exist in rep2
                continue

            if not dic1['Res']==dic2['Res']:
                if dic1['Res']=='True':
                    dic1['colRes']='green'
                elif dic1['Res']=='False':
                    dic1['colRes']='red'
                else:
                    dic1['colRes']='yellow'
            else:
                dic1['colRes']='white'


            if rep1.mode=='full':
                nWrn1 = int(dic1['Wrn'])
                nWrn2 = int(dic2['Wrn'])
                nErr1 = int(dic1['Err'])
                nErr2 = int(dic2['Err'])

                if nWrn1>nWrn2:
                    dic1['colWrn']='red'
                elif nWrn1<nWrn2:
                    dic1['colWrn']='green'
                else:
                    dic1['colWrn']='white'

                if nErr1>nErr2:
                    dic1['colErr']='red'
                elif nErr1<nErr2:
                    dic1['colErr']='green'
                else:
                    dic1['colErr']='white'

        if rep1.meta['git'] == rep2.meta['git']:
            rep1.disp.append({'Key':'Compared to', 'Val': rep2.name})
        else:
             rep1.disp.append({'Key':'Compared to', 'Val': rep2.meta['git']})

        rep1.name = '{}_compare'.format(rep1.name)
        rep1.generate_html()


    ###########################################################################
    #PYTHON-LIKE GETTER AND SETTER METHODS
    ###########################################################################
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self,s):
        _Validator('report_name',s)
        self.__name = s

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self,s):
        _Validator('report_path',s)
        self.__path = s

    @property
    def disp(self):
        return self.__disp

    @disp.setter
    def disp(self,lst):
        _Validator('report_disp',lst)
        self.__disp = lst

    @property
    def cont(self):
        return self.__cont

    @cont.setter
    def cont(self,lst):
        _Validator('report_cont',lst)
        self.__cont = lst

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self,s):
        _Validator('report_mode',s)
        self.__mode = s

    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self,dic):
        _Validator('report_meta',dic)
        self.__meta = dic


class Converter(object):
    """
    Returns a new Converter instance.

    Instance converts content of Report instances to different file formats.

    API:
    report_to_html(report):
        Generates a HTML file based on Report instance 'report'

    html_to_report(html):
        Transfers content of the HTML-file 'html' into a Report instance.

    html_to_report_attributes(html):
        Same as html_to_report, but does not return a Report instance but its
        attributes

    For more details take a look at the module itsself
    """

    def __init__(self):
        pass


    #PUBLIC API
    ###########################################################################
    def report_to_html(self,report):
        """
        Based on contents of a report instance, an HTML file is generated.
        Files location is given by reports name and path.

        ARGUMENTS:
        report (Report):
            instance, that is converted into an HTML file.

        RETURNS:
        If generation was successfull, TRUE is returned.
        """

        _Validator('report',report)
        self._generate_html(report)
        return True


    def html_to_report(self,html):
        """
        Contents of a HTLM file are converted into a report instance.

        ARGUMENTS:
        html (string):
            path to a report-html, which is converted into a report instance.

        RETURNS:
        report (Report):
            resulting instance of the conversion.
        """
        name, path, disp, cont, meta, mode = self._read_html(html)

        report = Report()
        report.name = name
        report.path = path
        report.disp = disp
        report.cont = cont
        report.meta = meta

        return report


    def html_to_report_attributes(self,html):
        """
        Contents of a HTLM file are converted into a report instance attributes.

        ARGUMENTS:
        html (string):
            path to a report-html, which is converted into a report instance.

        RETURNS:
        name, path, disp, cont, meta, mode (Attributes of Report):
            resulting instance attributes of the conversion.
        """
        name, path, disp, cont, meta, mode = self._read_html(html)
        return name, path, disp, cont, meta, mode


    #PRIVATE API
    ###########################################################################
    def _generate_html(self,report):
        """
        Generates HTML file based on a report instance

        ARGUMENTS:
        report (Report):
            instance, that is converted into a HTML file.

        RETURNS:
        An HTML file is generated. Files location is given by reports name and
        path
        """
        sDocType = '<!doctype html>'
        sTag0 = '\n<html lang=\"de\">'
        sHead = self._generate_html_head(report)
        sBody = self._generate_html_body(report)
        sTag1 = '\n</html>'

        #full string
        sHtml = "{}{}{}{}{}".format(sDocType,sTag0,sHead,sBody,sTag1)

        with open('{}.html'.format(os.path.join(report.path,report.name)),'w') as file:
            file.write(sHtml)


    def _generate_html_head(self,report):
        """
        Generates HTML <head> code as a string

        ARGUMENTS:
        report (Report):
            instance, that is converted into a HTML file.

        RETURNS:
        sHead (string):
            the corresponding HTML-formatted string
        """

        sTag0 = '\n\t<head>'
        sMeta = self._generate_html_meta(report)
        sTag1 = '\n\t</head>'

        sHead = '{}{}{}'.format(sTag0,sMeta,sTag1)
        return sHead


    def _generate_html_body(self,report):
        """
        Generates HTML <body> code as a string

        ARGUMENTS:
        report (Report):
            instance, that is converted into a HTML file.

        RETURNS:
        sBody (string):
            the corresponding HTML-formatted string
        """

        sTag0 = '\n\t<body>'
        sTitle = '\n\t\t<h2>{}</h2>'.format(report.name)
        sTableDisp = self._generate_html_table_disp(report)
        sTableCont = self._generate_html_table_content(report)
        sTag1 = '\n\t</body>'

        sBody = '{}{}\n{}\n{}{}'.format(sTag0,sTitle,sTableDisp,sTableCont,sTag1)
        return sBody


    def _generate_html_meta(self,report):
        """
        Generates HTML <meta> code as a string

        ARGUMENTS:
        report (Report):
            instance, that is converted into a HTML file.

        RETURNS:
        sMeta (string):
            the corresponding HTML-formatted string
        """

        sTemplate = '\n\t\t<meta name=\"{}\" content=\"{}\">'

        sChar = '\n\t\t<meta charset = \"utf8\">'
        sRows = ''.join(sTemplate.format(key, value) for key,value in sorted(report.meta.items()))

        sMeta = '{}{}'.format(sChar,sRows)
        return sMeta


    def _generate_html_table_disp(self,report):
        """
        Generates HTML <table> code as a string, which contains the reports
        disp information

        ARGUMENTS:
        report (Report):
            instance, that is converted into a HTML file.

        RETURNS:
        sDisp (string):
            the corresponding HTML-formatted string
        """

        sTag0 = '\n\t\t<table style=\"margin-bottom: 2em; margin-left: 2em\">'
        sHead = self._generate_html_table_disp_header()
        sRows = ''.join(self._generate_html_table_disp_rows(dic) for dic in report.disp)
        sTag1 = '\n\t\t</table>'

        sDisp = '{}{}{}{}'.format(sTag0,sHead,sRows,sTag1)
        return sDisp


    def _generate_html_table_disp_header(self):
        """
        Generates an HTML string for the header of the table, which contains
        the reports disp information

        RETURNS:
        srow (string):
            the corresponding HTML-formatted string
        """

        row = ['\n\t\t\t<tr>',
               '\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\"></th>',
               '\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\"></th>',
               '\n\t\t\t</tr>']

        srow = ''.join('{}'.format(r) for r in row)
        return srow


    def _generate_html_table_disp_rows(self,dic):
        """
        Generates an HTML string for one row of the table, which contains
        the reports disp information

        ARGUMENT:
        dic (dictionary):
            values gives the option and the corresponding setting

        RETURNS:
        srow (string):
            the corresponding HTML-formatted string
        """

        row = ["\n\t\t\t<tr>",
               "\n\t\t\t\t<td id=\"Key\" style=\"padding-left: 1em; text-align: right\">{}:</td>".format(dic['Key']),
               "\n\t\t\t\t<td id=\"Val\" style=\"padding-left: 1em\">{}</td>".format(dic['Val']),
               "\n\t\t\t</tr>"]

        srow = ''.join('{}'.format(r) for r in row)
        return srow


    def _generate_html_table_content(self,report):
        """
        Generates HTML <table> code for report.cont as a string

        ARGUMENTS:
        report (Report):
            instance, that is converted into a HTML file.

        RETURNS:
        sCont (string):
            the corresponding HTML-formatted string
        """

        sTag0 = '\n\t\t<table style=\"margin-left: 2em\" border=\"1\" frame=\"box\">'
        sHead = self._generate_html_table_content_header(report.mode)
        sRows = ''.join(self._generate_html_table_content_rows(dic,report.mode) for dic in report.cont)
        sTag1 = '\n\t\t</table>'

        sCont = '{}{}{}{}'.format(sTag0,sHead,sRows,sTag1)
        return sCont


    def _generate_html_table_content_header(self,mode):
        """
        Generates an HTML string for the header of the table for the test
        results

        ARGUMENTS:
        mode (string):
            if mode = 'full', additional columns for errors and warnings are
            generated

        RETURNS:
        srow (string):
            the corresponding HTML-formatted string
        """

        row = ['\n\t\t\t<tr>',
               '\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\">Package/Model</th>',
               '\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\">Result</th>',
               '{}'.format('\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\">Errors</th>' if mode=='full' else ''),
               '{}'.format('\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\">Warnings</th>' if mode=='full' else ''),
               '{}'.format('\n\t\t\t\t<th style=\"padding-right: 1em; padding-left: 1em; text-align: center\">Notes</th>' if mode=='full' else ''),
               '\n\t\t\t</tr>']

        srow = ''.join('{}'.format(r) for r in row)
        return srow


    def _generate_html_table_content_rows(self,dic,mode):
        """
        Generates an HTML string for one row of the table for the test results

        ARGUMENT:
        dic (dictionary):
            values gives the result for a package/model

         mode (string):
            if mode = 'full', additional columns for errors and warnings are
            generated

        RETURNS:
        srow (string):
            the corresponding HTML-formatted string
        """

        style ='\"padding-right: 1em; padding-left: 1em; text-align: {}; background-color: {}\"'

        row = ['\n\t\t\t<tr>',
               '\n\t\t\t\t<td id=\"Pck\" style={}>{}</td>'.format(style.format('left',dic['colPck']), dic['Pck']),
               '\n\t\t\t\t<td id=\"Res\" style={}>{}</td>'.format(style.format('center','{}'.format(dic['colRes'])), dic['Res']),
               '{}'.format('\n\t\t\t\t<td id=\"Err\" style={}>{}</td>'.format(style.format('center','{}'.format(dic['colErr'])), dic['Err']) if mode=='full' else ''),
               '{}'.format('\n\t\t\t\t<td id=\"Wrn\" style={}>{}</td>'.format(style.format('center','{}'.format(dic['colWrn'])), dic['Wrn']) if mode=='full' else ''),
               '{}'.format('\n\t\t\t\t<td id=\"Wrn\" style={}>{}</td>'.format(style.format('left','{}'.format('white')), dic['Notes']) if mode=='full' else ''),
               '\n\t\t\t</tr>']

        srow = ''.join('{}'.format(r) for r in row)
        return srow


    def _read_html(self,html):
        """
        Parses a given HTML file (based on name and path) and stores available
        information within the report instance.

        ARGUMENTS:
        html (string):
            path to a report-html, which is converted into a report instance.

        RETURNS:
        name, path, disp, cont, meta, mode (Report attributes):
            resulting instance attributes of the conversion.
        """

        #TODO: Check for valid Report HTML

        with open(html) as file:
            lst = file.readlines()

        path, name = os.path.split(html)
        name = name.replace('.html','')
        meta = self._parse_html_meta(lst)
        disp,cont = self._parse_html_tables(lst)
        mode = self._get_mode(cont[0])

        return name, path, disp, cont, meta, mode


    def _parse_html_meta(self,lst):
        """
        Parses given list instance for Reports meta information.

        ARGUMENTS:
        lst (list):
            each entry is a row of the HTML code.

        RETURNS:
        dic (dictionary):
            key-value pairs of meta information.
        """
        #Parse Meta
        ind = [i for i, j in enumerate(lst) if j.strip().startswith('<meta')]

        dic = {}
        for i in ind:
            s = lst[i]
            if s.strip()=='<meta charset = "utf8">':
                continue

            else:
                #search for name-value
                sKey = self._parse_keyvalue_pair(s,'name')
                #search for content-value
                sVal = self._parse_keyvalue_pair(s,'content')

                dic[sKey]=sVal

        return dic


    def _parse_html_tables(self, lst):
        """
        Parses given list instance for Reports disp and meta information.

        ARGUMENTS:
        lst (list):
            each entry is a row of the HTML code.

        RETURNS:
        disp, cont (list of dictionaries):
            Report attributes disp and cont
        """
        #Parse Tables
        start = [i for i, j in enumerate(lst) if j.strip().startswith('<table')]
        stop = [i for i, j in enumerate(lst) if j.strip().startswith('</table')]

        disp = self._parse_html_table(lst[start[0]+1:stop[0]])
        cont = self._parse_html_table(lst[start[1]+1:stop[1]])

        return disp, cont


    def _parse_html_table(self,lst):
        """
        Extracts values of 'td' rows of a given list.

        ARGUMENT:
        lst (list of strings):
           each item is a row of an HTML table

        RETURN:
        res (list of dictionaries):
            converted information.
        """
        #get each HTML row as a list item
        rows = list(self._parse_splitted_lst(lst,"\t\t\t<tr>\n"))
        #ignore first item, as it is the header line and an empty entry
        rows.pop(0)
        rows.pop(0)
        #ignore the last entry of each row, as it is the closure of a row "</tr>"
        [row.pop() for row in rows]

        res = []
        for row in rows:
            dic={}
            for column in row:

                #get the id
                sid = self._parse_keyvalue_pair(column,'id')
                #get the value
                sval = self._parse_keyvalue_pair(column,'<',['>','<'])

                if sval[-1]==':':
                    sval=sval[:-1]

                dic[sid]=sval
                if sid in ('Pck', 'Res', 'Err', 'Wrn'):
                    col = self._parse_keyvalue_pair(column,'background-color',[': ','"'])
                    dic['col{}'.format(sid)]=col.strip()

            res.append(dic)

        return res

    def _get_mode(self,dic):
        """
        Based on entrys in report.cont, the report.mode is determined.

        ARGUMENTS:
        dic (dictionary):
            Entry of report.cont. If it has 8 entries, the corresponding mode
            is 'full', if there are only 4 entries, mode is 'compact'

        RETURNS:
        mode (string):
            Either 'full' or 'compact'
        """

        if len(dic)==8:
            mode = 'full'
        elif len(dic)==4:
            mode = 'compact'

        return mode

    def _parse_keyvalue_pair(self,s,key,sep=['"','"']):
        """
        Parses a given string for substring key and extract the substring,
        which is included by the next seperators.
        Used to get the value of key-value pairs of a string.

        ARGUMENTS:
        s (string):
            string, that is parsed for substrings
        key (string):
            substrings, which must be followed by sep

        OPTIONAL:
        sep (list of strings, default: ['"','"']):
            seperators of the searched value. First entry is the left
            seperator, second the right one.
             Default:

        RETURN:
        sVal (string)
            corresponding value for key
        """

        try:
            ind = s.index(key)
            indKey0 = s.index(sep[0],ind)
            indKey1 = s.index(sep[1],indKey0+1)
            sVal = s[indKey0+1:indKey1]

        except ValueError:
            raise ValueError('\n\nSubstring not found in given string {}'.format(s)) from None
        except TypeError:
            raise TypeError('\n\n Input \'s\' must be a string but is a \'{}\''.format(s.__class__)) from None
        return sVal


    def _parse_splitted_lst(self, lst, sep):
        """
        Splits a list of strings into several sublist, where sep is the
        seperator string.

        Example: lst = ['A','B','C'], sep='B'
                 list(_parse_splitted_lst(lst,sep)) will return [['A'],['C']]

        ARGUMENTS:
        lst (list of strings):
            list that should be splitted into several lists.

        sep (string):
            an entry of lst, which is interpreted as a separator

        RETUNRS:
        sublists of lst.
        """
        ind1 = 0
        while ind1 < len(lst):
            try:
               ind2 = ind1 + lst[ind1:].index(sep)
               yield lst[ind1:ind2]
               ind1 = ind2 + 1
            except ValueError:
               yield lst[ind1:]
               break


###############################################################################
#VALIDATION OF OPTIONS
###############################################################################
class _Validator(object):
    """
    Returns a new _Validator instance to validate user inputs

    USAGE:
        _Validator(option,value)

    EXAMPLE:
        _Validator('report_name','report')
    """

    def __init__(self, key, val, val2=None):

        if key in 'report':
            self._validate_report(val)

        elif key in 'report_name':
            self._validate_report_name(val)

        elif key in 'report_path':
            self._validate_report_path(val)

        elif key in 'report_disp':
            self._validate_report_disp(val)

        elif key in 'report_cont':
            self._validate_report_cont(val)

        elif key in 'report_meta':
            self._validate_report_meta(val)

        elif key in 'report_mode':
            self._validate_report_mode(val)

        elif key in 'report_colors':
            self._validate_report_colors(val)

        elif key in 'report_compare':
            self._validate_report_compare(val,val2)

        elif key in 'dymola_path':
            self._validate_dymola_path(val)

        elif key in 'dymola_pedantic':
            self._validate_dymola_pedantic(val)

        elif key in 'modelica_lib_path':
            self._validate_modelica_lib_path(val)

        elif key in 'modelica_lib_firstlevel':
            self._validate_modelica_lib_firstlevel(val)

        elif key in 'modelica_lib_depth':
            self._validate_modelica_lib_depth(val)

        elif key in 'general_filepath':
            self._validate_general_filepath(val, val2)

        elif key in 'general_kwargs':
            self._validate_general_kwargs(val,val2)


    #PRIVATE API
    ###########################################################################
    def _validate_report_name(self,val):
        if val:
            self._validate_general_instance('name',val,str,'string')
            fname, fext = os.path.splitext(val)
            assert len(fname)>0 , '\n\n => Value of \'name\' must be an acutal non-zero sized string! <='
            assert len(fext)==0, '\n\n => Value of \'name\' must not have a file extension, but has \'{}\'! <='.format(fext)


    def _validate_report_path(self,val):
        if val:
            self._validate_general_instance('path',val,str,'string')
            self._validate_general_dirpath('path',val)


    def _validate_report_disp(self,val):
        if val:
            self._validate_general_instance('disp',val,list,'list')
            for elem in val:
                assert isinstance(elem,dict), '\n\n => Each entry in \'disp\' must be a dictionary itself, but entry [{}] is \'{}\'! <='.format(elem,elem.__class__)
                self._validate_general_key_in_dict('disp', elem, ['Key','Val'])


    def _validate_report_cont(self,val):
        if val:
            self._validate_general_instance('cont',val,list,'list')
            for elem in val:
                assert isinstance(elem,dict), '\n\n => Each entry in \'cont\' must be a dictionary, but entry [{}] is \'{}\'! <='.format(elem,elem.__class__)
                self._validate_general_key_in_dict('cont', elem, ['Pck', 'Res', 'Err', 'Wrn', 'Notes', 'colPck', 'colRes', 'colWrn', 'colErr'])


    def _validate_report_meta(self,val):
        if val:
            self._validate_general_instance('meta',val,dict,'dictionary')
            assert len(val)==5, '\n\n => \'meta\' must have only four keys (\'pck\', \'ped\', \'lod\', \'git\' and \'viewport\') but not \'{}\'! <='.format(len(val))
            self._validate_general_key_in_dict('meta', val, ['pck','lod','ped','git','viewport'])


    def _validate_report_mode(self,val):
        if val:
            self._validate_general_instance('mode',val,str,'string')
            assert val in('full','compact'), '\n\n => Value of \'mode\' must be either \'full\' or \'compact\', but is \'{}\'! <='.format(val)


    def _validate_report_colors(self,val):
        if val:
            self._validate_general_instance('colors',val,dict,'dictionary')
            self._validate_general_key_in_dict('colors', val, ['cTrue','cFalse', 'cNF','cErr','cWrn'])


    def _validate_report(self,val):
        self._validate_general_instance('Report',val, Report ,'Report')
        self._validate_report_name(val.name)
        self._validate_report_path(val.path)
        self._validate_report_disp(val.disp)
        self._validate_report_meta(val.meta)
        self._validate_report_mode(val.mode)
        self._validate_report_colors(val.colors)


    def _validate_report_compare(self,rep1,rep2):
        assert rep1.meta['pck'] == rep2.meta['pck'], '\n\n => Reports corresponds to different Modelica libraries! <='
        assert rep1.meta['lod'] == rep2.meta['lod'], '\n\n => Reports have different level of detail! <='
        assert rep1.meta['ped'] == rep2.meta['ped'], '\n\n => Reports correspond to different Dymola checkModel() mode! <='


    def _validate_dymola_path(self,val):
        self._validate_general_instance('dymola_path',val,str,'string')
        self._validate_general_filepath('dymola_path',val)


    def _validate_dymola_pedantic(self,val):
        self._validate_general_instance('dymola_pedantic',val,bool,'boolean')


    def _validate_modelica_lib_path(self,val):
        self._validate_general_instance('modelica_lib_path',val,str,'string')
        self._validate_general_dirpath('modelica_lib_path',val)
        self._validate_general_packageorder('modelica_lib_path',val)


    def _validate_modelica_lib_firstlevel(self,val):
        self._validate_general_instance('modelica_lib_firstlevel',val,str,'string')
        self._validate_general_dirpath('modelica_lib_firstlevel',val)
        self._validate_general_packageorder('modelica_lib_firstlevel',val)


    def _validate_modelica_lib_depth(self,val):
        self._validate_general_instance('modelica_lib_depth',val,int,'inetger')
        assert val>0 or val==-1, '\n\n => Value of \'modelica_lib_depth\' must be greater than zero or -1 , but is \'{}\'! <='.format(val)


    def _validate_general_filepath(self, opt, val):
        self._validate_general_instance('filepath',val,str,'string')
        assert os.path.exists(val), '\n\n => Value of \'{}\' is not a valid file path: \n\t\'{}\'! <='.format(opt, val)


    def _validate_general_dirpath(self,opt,val):
        assert os.path.isdir(val), '\n\n => Value of \'{}\' is not a valid directory path: \n\t{}\n! <='.format(opt, val)


    def _validate_general_instance(self,opt,val,cls,scls):
        assert isinstance(val,cls),'\n\n => Value of \'{}\' must be a {}, but is\'{}\'! <='.format(opt, scls, val.__class__)


    def _validate_general_key_in_dict(self,opt,val,keys):
        for key in val:
            assert key in keys, '\n\n => Keys of \'{}\' must be in ({}), and not \'{}\'! <='.format(opt,keys,key)

    def _validate_general_packageorder(self,opt,val):
        assert os.path.exists(os.path.join(val,'package.order')), '\n Directory of input \'{}\' does not contain a \'package.order\':\n\t\'{}\'! <='.format(opt, val)


    def _validate_general_kwargs(self,val,options):
        for opt in val:
            assert opt in options, '\n\n => Given attribute \'{}\' is not recognized! <='.format(opt)
