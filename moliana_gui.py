# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 08:51:04 2017

@author: jmoeckel
"""

import os
import sys
import tkinter
import moliana
import webbrowser

import logger

from tkinter import filedialog
from tkinter import ttk
from tkinter import INSERT

from json import dump as jsondump
from json import load as jsonload


log = logger.configure('GUI','logs')
       
class WidgetLogger(logger.logging.Handler):
    def __init__(self, widget):
        logger.logging.Handler.__init__(self)   
        formatter = logger.logging.Formatter(fmt ='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        self.setLevel(logger.logging.INFO)
        self.setFormatter(formatter)
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self, record):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        self.widget.insert(tkinter.END, self.format(record) + '\n')
        self.widget.see(tkinter.END)  # Scroll to the bottom
        self.widget.config(state='disabled')
        

      
class Moliana_Gui(tkinter.Tk):
    
    def __init__(self, master):
        
        # Initialize Frame
        tkinter.Tk.__init__(self, master)
                        
        self.master = master  
        self.frame = tkinter.Frame(self, padx=10, pady=10, bg="white")

        self.INITIAL = self._load_configs()
        
        self.OPTIONS = {'check_modes': ('execute checkModel()', 'execute checkModel() + generate html-report', 'execute checkModel() + generate html-report + open html-report'),
                        'report_modes': ('full', 'compact')
                        }

        
        self.create_widgets()  

        log.addHandler(WidgetLogger(self.WIDGETS['tf_logger']))
        log.info('Welcome to Moliana')        
        self.arrange_widgets()
        
        
    def create_widgets(self): 
        
        self.VAR = {'dirpath_library': tkinter.StringVar(self, self.INITIAL['init_dirpath_library']),
                    'dirpath_dymola': tkinter.StringVar(self, self.INITIAL['init_dirpath_dymola']),
                    'dirpath_firstlevel':  tkinter.StringVar(self, self.INITIAL['init_dirpath_firstlevel']),
                    'dirpath_htmlreport':  tkinter.StringVar(self, self.INITIAL['init_dirpath_htmlreport']),
                    'dirpath_dependencies': tkinter.StringVar(self, self.INITIAL['init_dirpath_dependencies']),
                    'filename_htmlreport':  tkinter.StringVar(self, self.INITIAL['init_filename_htmlreport']),
                    'box_pedantic': tkinter.BooleanVar (self, self.INITIAL['init_box_pedantic']),
                    'box_firstlevel': tkinter.BooleanVar (self, self.INITIAL['init_box_firstlevel']),
                    'box_dependencies': tkinter.BooleanVar (self, self.INITIAL['init_box_dependencies']),
                    'box_htmlreport': tkinter.BooleanVar (self, self.INITIAL['init_box_htmlreport']),
                    'box_reportmode': tkinter.BooleanVar (self, self.INITIAL['init_box_reportmode']),
                    'report_mode': tkinter.StringVar(self, self.INITIAL['init_report_mode']),
                    'check_mode': tkinter.StringVar(self, self.INITIAL['init_check_mode']),
                    }
                      
        self.WIDGETS = {'in_dirpath_library': tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_library']),
                        'in_dirpath_dependencies': tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_dependencies']),
                        'in_dirpath_dymola':  tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_dymola']),
                        'in_dirpath_firstlevel': tkinter.Entry(self, width=48, borderwidth=3, textvariable=self.VAR['dirpath_firstlevel']),
                        'in_dirpath_htmlreport': tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_htmlreport']),
                        'in_filename_htmlreport':  tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['filename_htmlreport']),
                        'bt_opendir_dymola': tkinter.Button(self, text='...', command=self.browse_dir_dymola),
                        'bt_opendir_library': tkinter.Button(self, text='...', command=self.browse_dir_library),
                        'bt_opendir_firstlevel': tkinter.Button(self, text='...', command=self.browse_dir_firstlevel),
                        'bt_opendir_dependencies': tkinter.Button(self, text='...', command=self.browse_dir_dependencies),
                        'bt_opendir_htmlreport': tkinter.Button(self, text='...', command=self.browse_dir_report),
                        'bt_run': tkinter.Button(self, text='Run check mode', command=self.run_checks),
                        'bt_open_report': tkinter.Button(self, text='Open Report', command=self.open_report),
                        'bt_show_report': tkinter.Button(self, text='Show Report', command=self.show_report),
                        'bt_export_report': tkinter.Button(self, text='Export Report to html', command=self.export_report),
                        'bt_save_config': tkinter.Button(self, text='Save Settings', command=self.save_config),
                        'bt_restore_config': tkinter.Button(self, text='Restore Settings', command=self.restore_config),    
                        'lb_log': tkinter.Label(self, bg='white', text='Log (extended log available on console and in \'./logs\')'),                    
                        'lb_dirpath_dymola': tkinter.Label(self, bg='white', text='Path to Dymola installation'),
                        'lb_dirpath_library': tkinter.Label(self, bg='white', text='Path to Modelica library'),
                        'lb_dirpath_firstlevel': tkinter.Label(self, bg='white', text='Select Subpackage'),
                        'lb_dirpath_dependencies': tkinter.Label(self, bg='white', text='Dependencies for considered library (if more than one, enter as list)'),
                        'lb_dirpath_htmlreport': tkinter.Label(self, bg='white', text='Path to Report directory'),
                        'lb_filename_htmlreport': tkinter.Label(self, bg='white', text='Name of the report'),
                        'lb_report_mode': tkinter.Label(self, bg='white', text='Choose the appearance of the report:'),
                        'lb_checkmode_option': tkinter.Label(self, bg='white', text='Choose check mode:'),
                        'lb_emptyline1': tkinter.Label(self, bg='white', text=' '),
                        'lb_emptyline2': tkinter.Label(self, bg='white', text=' '),
                        'lb_emptyline3': tkinter.Label(self, bg='white', text=' '),     
                        'lb_report': tkinter.Label(self, bg='white', text='Report'),     
                        'lb_emptycol1': tkinter.Label(self, bg='white', text=' ', width=5),                          
                        'lb_emptycol2': tkinter.Label(self, bg='white', text=' ', width=5),                          
                        'lb_emptycol3': tkinter.Label(self, bg='white', text=' '),                          
                        'cb_pedantic': tkinter.Checkbutton(self, bg='white', text='Execute checkModel() in pedantic mode', variable=self.VAR['box_pedantic']),
                        'cb_dependencies': tkinter.Checkbutton(self, bg='white', text='Preload libraries before loading considered library', variable=self.VAR['box_dependencies'], command=self._show_dependencies),
                        'cb_firstlevel': tkinter.Checkbutton(self, bg='white', text='Only check subpackage of considered library', variable=self.VAR['box_firstlevel'], command=self._show_firstlevel),
                        'cb_htmlreport': tkinter.Checkbutton(self, bg='white', text='Export report to html', variable=self.VAR['box_htmlreport'], command=self._show_htmlreport),
                        'cb_report_mode': tkinter.Checkbutton(self, bg='white', text='Show only failed and warnings in report', variable=self.VAR['box_reportmode']),
                        'om_check_mode': tkinter.OptionMenu(self, self.VAR['check_mode'], *self.OPTIONS['check_modes']),
                        'tf_logger': tkinter.Text(self, width=60, height=15, wrap=tkinter.WORD, borderwidth=3, relief="sunken"),
                        'sb_loggery': tkinter.Scrollbar(self),
                        'sb_reporty': tkinter.Scrollbar(self),
                        'tv_report': ttk.Treeview(self),
                        'sl_sep1': ttk.Separator(self, orient=tkinter.HORIZONTAL)                     
                        }
                        
        self.LabelFrame = tkinter.LabelFrame(self, text='Test')
        self.NeuLabel = tkinter.Label(self.LabelFrame, text = 'ich bin ein label')

        #Adaptions               
        self.WIDGETS['om_check_mode'].config(bg = 'white', width=8)
        self.WIDGETS['om_check_mode']['menu'].config(bg = 'white')
        
        self.WIDGETS['sb_loggery'].config(command=self.WIDGETS['tf_logger'].yview)
        self.WIDGETS['sb_reporty'].config(command=self.WIDGETS['tv_report'].yview)
        
        self.WIDGETS['tf_logger']["yscrollcommand"] = self.WIDGETS['sb_loggery'].set
        self.WIDGETS['tf_logger'].tag_config(tkinter.SEL, lmargin1 = 10, lmargin2 = 10, rmargin = 10)
        self.WIDGETS['tf_logger'].insert(0.0, '')
        
                

        tv = self.WIDGETS['tv_report']
        tv['columns'] = ('Result', 'Errors', 'Warnings', 'Notes')
        tv.heading("#0", text='Model', anchor='w')
        tv.column("#0", anchor="w", width=350)
        tv.heading('Result', text='Result')
        tv.column('Result', anchor='center',  width=100)
        tv.heading('Errors', text='Errors')
        tv.column('Errors', anchor='center',width=100)
        tv.heading('Warnings', text='Warnings')
        tv.column('Warnings', anchor='center',  width=100)
        tv.heading('Notes', text='Notes')
        tv.column('Notes', anchor='w', width=470)   
        
        self.WIDGETS['tv_report'] = tv
        self.WIDGETS['tv_report']["yscrollcommand"] = self.WIDGETS['sb_reporty'].set

    def arrange_widgets(self):
        
        common_options = {'in_': self.frame,
                          'ipady': 2,
                          'sticky': 'W'}
        
        # Empty Cols
        self.WIDGETS['lb_emptycol1'].grid(row = 0, column = 6, columnspan = 1, **common_options) 
        self.WIDGETS['lb_emptycol2'].grid(row = 0, column = 13, columnspan = 1, **common_options)   
        
        n = 0
        self.WIDGETS['lb_dirpath_dymola'].grid(row = n, column = 0, columnspan = 5, **common_options)  
        self.WIDGETS['lb_dirpath_library'].grid(row = n, column = 7, columnspan = 5, **common_options) 
        self.WIDGETS['lb_log'].grid(row = n, column = 14, columnspan = 5, **common_options)
        
        n = n+1
        self.WIDGETS['in_dirpath_dymola'].grid(row = n, column = 0, columnspan = 5, **common_options)
        self.WIDGETS['bt_opendir_dymola'].grid(row = n, column = 5, columnspan = 1, **common_options)        
        self.WIDGETS['in_dirpath_library'].grid(row = n, column = 7, columnspan = 5, **common_options)     
        self.WIDGETS['bt_opendir_library'].grid(row = n, column = 12, columnspan = 1, **common_options)  
        self.WIDGETS['tf_logger'].grid(row = n, column = 14, columnspan = 5, rowspan = 11, sticky = "WENS", in_ =self.frame)
        self.WIDGETS['sb_loggery'].grid(row = n,column = 19, rowspan = 11, sticky = "ns", in_ =self.frame)
       
        n=n+1
        self.WIDGETS['cb_firstlevel'].grid(row = n, column = 0, columnspan = 5, **common_options)
        self.WIDGETS['lb_dirpath_firstlevel'].grid(row = n+1, column = 1, columnspan = 3, **common_options) 
        self.WIDGETS['in_dirpath_firstlevel'].grid(row = n+1, column = 4, columnspan = 1, **common_options)     
        self.WIDGETS['bt_opendir_firstlevel'].grid(row = n+1, column = 5, columnspan = 1,**common_options)
        self._show_firstlevel()
                       
        n=n+3
        self.WIDGETS['cb_dependencies'].grid(row = n, column = 0, columnspan = 5, **common_options)
        self.WIDGETS['lb_dirpath_dependencies'].grid(row = n, column = 7, columnspan = 5, **common_options) 
        self.WIDGETS['in_dirpath_dependencies'].grid(row = n+1, column = 7, columnspan = 5, **common_options)     
        self.WIDGETS['bt_opendir_dependencies'].grid(row = n+1, column = 12, columnspan = 1, **common_options)
        self._show_dependencies()
        
        n=n+2
        self.WIDGETS['cb_htmlreport'].grid(row = n, column = 0, columnspan = 5, **common_options)
        self.WIDGETS['lb_dirpath_htmlreport'].grid(row = n, column = 7, columnspan = 5, **common_options)
        self.WIDGETS['in_dirpath_htmlreport'].grid(row = n+1, column = 7, columnspan = 5, **common_options)   
        self.WIDGETS['bt_opendir_htmlreport'].grid(row = n+1, column = 12, columnspan = 1, **common_options)
        self.WIDGETS['lb_filename_htmlreport'].grid(row = n+2, column = 7, columnspan = 5, **common_options)
        self.WIDGETS['in_filename_htmlreport'].grid(row = n+3, column = 7, columnspan = 5, **common_options)        
        self._show_htmlreport()
        

        n=n+4
        self.WIDGETS['cb_report_mode'].grid(row = n, column = 0, columnspan = 5, **common_options) 

        n=n+1
        self.WIDGETS['cb_pedantic'].grid(row = n, column = 0, columnspan = 5, **common_options) 

        n=n+1
        self.LabelFrame.grid(row=n, column=0, **common_options)
        self.NeuLabel.grid(row=0, column=0)
        
        n=n+1
        self.WIDGETS['sl_sep1'].grid(row=n, column=0, columnspan=13, sticky='ew', pady = 15, in_=self.frame)        
       
        n=n+1
        self.WIDGETS['tv_report'].grid(row=n, column=0, columnspan = 19, sticky='WENS', in_=self.frame)
        self.WIDGETS['sb_reporty'].grid(row = n,column = 19, sticky = "ns", in_ =self.frame)
        
       
        
#        self.WIDGETS['bt_export_report'].grid(row = n, column = 7, columnspan = 1, sticky = "W")       
#        self.WIDGETS['bt_open_report'].grid(row = n, column = 9, columnspan = 1, sticky = "W") 
#        self.WIDGETS['bt_show_report'].grid(row = n, column = 10, columnspan = 1, sticky = "W")               
#        
#        n=n+1
#        self.WIDGETS['lb_emptyline3'].grid(row = n, column = 0, columnspan = 1, sticky = "W",ipady = 2)  
#        

#        

#        
#        n=n+1
#        self.WIDGETS['bt_run'].grid(row = n, column = 0, columnspan = 1, sticky = "W")
#    
#        
#        n=n+1
#        self.WIDGETS['lb_emptyline1'].grid(row = n, column = 0, columnspan = 1, sticky = "W",ipady = 2)  
#        
#        n=n+1
#        self.WIDGETS['bt_save_config'].grid(row = n, column = 17, columnspan = 1, sticky = "E")
#        self.WIDGETS['bt_restore_config'].grid(row = n, column = 18, columnspan = 1, sticky = "E")
#

        
        self.frame.grid()

    def run_checks(self):
        log.info('Executing checkModel() ...')
        
        pDym = self.VAR['dirpath_dymola'].get()
        pLib = self.VAR['dirpath_library'].get()
        
        options = {'modelica_lib_firstlevel': self.VAR['dirpath_firstlevel'].get(),
                   'dymola_pedantic': self.VAR['box_pedantic'].get(),
                   'report_path': self.VAR['dirpath_report'].get(),
                   'report_name': self.VAR['filename_report'].get(),
                   'report_mode': self.VAR['report_mode'].get()
                   }
        
        if self.VAR['dirpaths_dependencies'].get():
            options.update({'modelica_lib_dependencies': [self.VAR['dirpaths_dependencies'].get()]})
                  
        dm = moliana.DymolaMode(pLib, pDym, **options)
        
        self.Report = dm.execute_check()    
        log.info('... done')
        
        
    def generate_treeview(self):
        tv = self.WIDGETS['tv_report']
        
        tv.insert('','end',text='Zeile1',values = (True,0,0,''), tags=('line1','line2'))
        tv.insert('','end',text='Zeile1',values = (False,1,0,''), tags=('line2'))
        tv.insert('','end',text='Zeile1',values = (True,0,1,'Bla'))
        
        ind = tv.insert('',0, 'new', text='New')
        tv.insert(ind,1, text = 'bla', values=(False),tags=('try'))
        tv.insert(ind,0,values = (1), tags=('nexttry'))
        tv.insert(ind,'end',values = (2))
        tv.insert(ind,'end',values = ('dubi'))
        
        tv.tag_configure('line1', background = 'green')
        tv.tag_configure('line2', background = 'yellow')
        tv.tag_configure('try', background = 'blue')
        tv.tag_configure('nexttry', background = 'red')
        
       

    def show_report(self):
        
        self.generate_treeview()
        
        
    def open_report(self):
        dirpath = self.VAR['dirpath_report'].get()
        
        if not dirpath:
            dirpath = self.VAR['dirpath_library'].get()
        
        filepath_report= os.path.join(dirpath, '{}.html'.format(self.VAR['filename_report'].get()))
        
        if os.path.exists(filepath_report):
            webbrowser.open_new(filepath_report)
        else:
            log.error('Report \'{}\' does not exist!'.format(filepath_report))
            
    def export_report(self):
        log.info('Generating html report ...')
        
        report_path = self._get_dirname('dirpath_report', 'dirpath_library')
        
        try:
            self.Report.mode = self.VAR['report_mode'].get()
            self.Report.path = report_path
            self.Report.name = self.VAR['filename_report'].get()
            
            self.Report.generate_html()
        except AttributeError:
            log.error('No Report instance available - you have to run checkModel() first')
        else:
            log.info('... done')
        
    
    def browse_dir_dymola(self):
        """Opens file browser such that the user could easily choose a directory"""
        dirname = filedialog.askdirectory(parent=self, initialdir =self.INITIAL['init_dirpath_dymola'], title='Please select a directory', mustexist = True)         
        self.VAR['dirpath_dymola'].set(dirname)   
    
    def browse_dir_library(self):
        """Opens file browser such that the user could easily choose a directory"""
        dirname = filedialog.askdirectory(parent=self, initialdir = self.INITIAL['init_dirpath_library'], title='Please select a directory', mustexist = True)         
        self.VAR['dirpath_library'].set(dirname)
        self.VAR['dirpath_report'].set(dirname)
        self.INITIAL['init_dirpath_firstlevel'] = dirname        
    
    def browse_dir_firstlevel(self):
        """Opens file browser such that the user could easily choose a directory"""
        initdir = self._get_dirname('init_dirpath_firstlevel', 'dirpath_library')
          
        dirpath = filedialog.askdirectory(parent=self, initialdir=initdir, title='Please select a directory', mustexist = True)         
        dirname = os.path.basename(dirpath)
        
        self.VAR['dirpath_firstlevel'].set(dirname)  
        
    def browse_dir_dependencies(self):
        """Opens file browser such that the user could easily choose a directory"""
        dirpath = filedialog.askdirectory(parent=self, initialdir =  self.INITIAL['init_dirpaths_dependencies'], title='Please select a directory', mustexist = True)                
        self.VAR['dirpaths_dependencies'].set(dirpath)  
        
    def browse_dir_report(self):
        """Opens file browser such that the user could easily choose a directory"""
        
        initdir = self._get_dirname('init_dirpath_report', 'dirpath_library')
                    
        dirname = filedialog.askdirectory(parent=self, initialdir = initdir, title='Please select a directory', mustexist = True)         
        self.VAR['dirpath_report'].set(dirname)  
    
    def save_config(self):
        for key in self.INITIAL:
            self.INITIAL[key] = self.VAR[key.replace('init_','')].get()
        

        with open('config.json', 'w') as jsonfile:
            jsondump(self.INITIAL, jsonfile, indent=4)
        log.info('Stored current settings to \'config.json\'')

            
    def restore_config(self):
        self.INITIAL = self._load_configs()
        
        for key in self.VAR:
            self.VAR[key].set(self.INITIAL['init_{}'.format(key)])
        
    
    def _load_configs(self):
        with open('config.json') as jsonfile:
            configs = jsonload(jsonfile)
            
        return configs
        
    def _get_dirname(self, firstchoice, scndchoice):
        dirname =  self.VAR[firstchoice].get()

        if not dirname:
            dirname = self.VAR[scndchoice].get()
            
        return dirname
        
    def _show_firstlevel(self, event = None):

        if self.VAR['box_firstlevel'].get():
            
            self.WIDGETS['lb_dirpath_firstlevel'].lift()
            self.WIDGETS['in_dirpath_firstlevel'].lift()
            self.WIDGETS['bt_opendir_firstlevel'].lift()
        else:
            self.WIDGETS['lb_dirpath_firstlevel'].lower()
            self.WIDGETS['in_dirpath_firstlevel'].lower()
            self.WIDGETS['bt_opendir_firstlevel'].lower()
            
    def _show_dependencies(self, event = None):

        if self.VAR['box_dependencies'].get():
            
            self.WIDGETS['lb_dirpath_dependencies'].lift()
            self.WIDGETS['in_dirpath_dependencies'].lift()
            self.WIDGETS['bt_opendir_dependencies'].lift()
        else:
            self.WIDGETS['lb_dirpath_dependencies'].lower()
            self.WIDGETS['in_dirpath_dependencies'].lower()
            self.WIDGETS['bt_opendir_dependencies'].lower()
            
    def _show_htmlreport(self, event = None):

        if self.VAR['box_htmlreport'].get():
            
            self.WIDGETS['lb_dirpath_htmlreport'].lift()
            self.WIDGETS['in_dirpath_htmlreport'].lift()
            self.WIDGETS['bt_opendir_htmlreport'].lift()
            self.WIDGETS['lb_filename_htmlreport'].lift()
            self.WIDGETS['in_filename_htmlreport'].lift()
        else:
            self.WIDGETS['lb_dirpath_htmlreport'].lower()
            self.WIDGETS['in_dirpath_htmlreport'].lower()
            self.WIDGETS['bt_opendir_htmlreport'].lower()
            self.WIDGETS['lb_filename_htmlreport'].lower()
            self.WIDGETS['in_filename_htmlreport'].lower()
            

#Top Level Code    
if __name__ == "__main__":    

    app = Moliana_Gui(None)
    app.title("Moliana")
    app.mainloop()