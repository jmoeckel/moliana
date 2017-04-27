# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 09:53:17 2017

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

from json import dump as jsondump
from json import load as jsonload

log = logger.configure('GUI','logs')

#Global GUI Variables
cb_check_pedantic_mode = 'check_pedantic_mode'
cb_check_first_package = 'check_first_package'
cb_molib_preload_molib = 'molib_preload_molib'
cb_report_export_2html = 'report_export_2html'
cb_report_compact_mode = 'report_compact_mode'

dp_library_tobechecked = 'dirpath_modelica_library'
dp_dymola_installation = 'dirpath_dymola_installation'
dp_molib_preload_molib = 'dirpath_molib_preload_molib'
dp_check_first_package = 'dirpath_first_package'
fp_report_export_2html = 'filepath_html_report'

      
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

        self.set_initials()
        
        self.create_variables()
        
        self.create_widgets()  

        log.addHandler(WidgetLogger(self.WIDGETS_LOGGING['LOG']))
        log.info('Welcome to Moliana')        
        
        self.arrange_widgets()

       
        
    def set_initials(self):
        self.INITIAL = self._load_configs()
        

    def create_variables(self):
        self.VAR = {cb_check_pedantic_mode: tkinter.BooleanVar(self, self.INITIAL[cb_check_pedantic_mode]),
                    cb_check_first_package: tkinter.BooleanVar(self, self.INITIAL[cb_check_first_package]),
                    cb_molib_preload_molib: tkinter.BooleanVar(self, self.INITIAL[cb_molib_preload_molib]),
                    cb_report_export_2html: tkinter.BooleanVar(self, self.INITIAL[cb_report_export_2html]),
                    cb_report_compact_mode: tkinter.BooleanVar(self, self.INITIAL[cb_report_compact_mode]),
                    dp_library_tobechecked: tkinter.StringVar(self, self.INITIAL[dp_library_tobechecked]),                                           
                    dp_dymola_installation: tkinter.StringVar(self, self.INITIAL[dp_dymola_installation]),
                    dp_molib_preload_molib: tkinter.StringVar(self, self.INITIAL[dp_molib_preload_molib]),
                    dp_check_first_package: tkinter.StringVar(self, self.INITIAL[dp_check_first_package]),
                    fp_report_export_2html: tkinter.StringVar(self, self.INITIAL[fp_report_export_2html])
                    }
        
        
    def create_widgets(self):
        options = {'frame': {'padx': 10, 'pady': 10, 'bg': 'white'},
                   'section': {'padx': 10, 'pady': 10, 'bg': 'white'},
                }

                                        
        self.FRAME =  tkinter.Frame(self, **options['frame'])
                         
         
        # All Sections               
        self.SECTIONS = {'session': tkinter.LabelFrame(self.FRAME, text='Session', **options['section']),
                         'logging': tkinter.LabelFrame(self.FRAME, text='Log', **options['section']),
                         'results': tkinter.LabelFrame(self.FRAME, text='Report', **options['section'])
                         }
           
        self.create_widgets_session()
        self.create_widgets_results()
        self.create_widgets_logging()
        
    def create_widgets_logging(self):
        logging = self.SECTIONS['logging']
        
        tf_logger = tkinter.Text(logging, width=70, height=24, wrap=tkinter.WORD, borderwidth=3)
        sb_loggery = tkinter.Scrollbar(logging)

        sb_loggery.config(command=tf_logger.yview)
        
        tf_logger["yscrollcommand"] = sb_loggery.set
        tf_logger.tag_config(tkinter.SEL, lmargin1 = 10, lmargin2 = 10, rmargin = 10)
        tf_logger.insert(0.0, '')
        
        self.WIDGETS_LOGGING = {'LOG': tf_logger, 'SCB': sb_loggery}
        
    
    def create_widgets_results(self):
        options = {'bts': {'width': 12}
                  }
                  
        results = self.SECTIONS['results']

        BTS = {'report_open': tkinter.Button(results, text='Open html', command=self.report_open, **options['bts']),
               'report_exprt': tkinter.Button(results, text='Export to html', command=self.report_exprt, **options['bts'])              
               }
               
        sb_reporty = tkinter.Scrollbar(results)
        tv_report = ttk.Treeview(results)
       
        
        
        sb_reporty.config(command=tv_report.yview)
        tv_report["yscrollcommand"] = sb_reporty.set
        
        tv_report['columns'] = ('Result', 'Errors', 'Warnings', 'Notes')
        tv_report.heading("#0", text='Model', anchor='w')
        tv_report.column("#0", anchor="w", width=300)
        tv_report.heading('Result', text='Result')
        tv_report.column('Result', anchor='center',  width=100)
        tv_report.heading('Errors', text='Errors')
        tv_report.column('Errors', anchor='center',width=100)
        tv_report.heading('Warnings', text='Warnings')
        tv_report.column('Warnings', anchor='center',  width=100)
        tv_report.heading('Notes', text='Notes')
        tv_report.column('Notes', anchor='w', width=430)   

        self.WIDGETS_RESULTS = {'BTS': BTS, 'TVS': tv_report, 'SCB': sb_reporty}
        
    def create_widgets_session(self):
        
        options = {'entry': {'width': 40, 'borderwidth': 3},
                   'label': {'bg': 'white'},
                   'cbox': {'bg': 'white'},
                   'bts1': {'width': 5},
                   'bts2': {'width': 15, 'height':2},
            }
        
        session = self.SECTIONS['session']
        VAR = self.VAR
        
        # All Checkbuttons
        CBS = {cb_check_pedantic_mode: tkinter.Checkbutton(session, variable=VAR[cb_check_pedantic_mode], text='Execute checkModel() in pedantic mode', **options['cbox']),                    
               cb_check_first_package: tkinter.Checkbutton(session, variable=VAR[cb_check_first_package], text='Only check subpackage of considered library', **options['cbox']),
               cb_molib_preload_molib: tkinter.Checkbutton(session, variable=VAR[cb_molib_preload_molib], text='Preload dependencies for considered library', **options['cbox']),
               cb_report_export_2html: tkinter.Checkbutton(session, variable=VAR[cb_report_export_2html], text='Export report to html', **options['cbox']),
               cb_report_compact_mode: tkinter.Checkbutton(session, variable=VAR[cb_report_compact_mode], text='Show only results that are not passed', **options['cbox'])                              
              }
                    
        # All Entrys
        INS = {dp_library_tobechecked: tkinter.Entry(session, textvariable=VAR[dp_library_tobechecked], **options['entry']),
               dp_molib_preload_molib: tkinter.Entry(session, textvariable=VAR[dp_molib_preload_molib], **options['entry']),
               dp_dymola_installation: tkinter.Entry(session, textvariable=VAR[dp_dymola_installation], **options['entry']),
               dp_check_first_package: tkinter.Entry(session, textvariable=VAR[dp_check_first_package], **options['entry']),
               fp_report_export_2html: tkinter.Entry(session, textvariable=VAR[fp_report_export_2html], **options['entry'])
              }
        
        # All Labels
        LBS = {dp_library_tobechecked: tkinter.Label(session, text='Path to modelica library', **options['label']),
               dp_dymola_installation: tkinter.Label(session, text='Path to dymola installation', **options['label']),                    
               dp_check_first_package: tkinter.Label(session, text='Path to subpackage: ', **options['label']),
               dp_molib_preload_molib: tkinter.Label(session, text='Pathes to libraries: ', **options['label']),
               fp_report_export_2html: tkinter.Label(session, text='Path to .html file:', **options['label']),
              }
                    
        BTS = {dp_library_tobechecked: tkinter.Button(session, text='...', command=self.browse_dir_library),
               dp_dymola_installation: tkinter.Button(session, text='...', command=self.browse_dir_dymola),
               dp_check_first_package: tkinter.Button(session, text='...', command=self.browse_dir_firstlevel),
               dp_molib_preload_molib: tkinter.Button(session, text='...', command=self.browse_dir_dependencies),
               'session_run': tkinter.Button(session, text='Run', command=self.session_run, **options['bts2']),
               'config_load': tkinter.Button(session, text='Load', command=self.config_load, **options['bts1']),
               'config_save': tkinter.Button(session, text='Save', command=self.config_save, **options['bts1']),
              }
                 
        
        #Adaptions
        CBS[cb_report_export_2html].configure(command = lambda var=VAR[cb_report_export_2html], lb=LBS[fp_report_export_2html], en=INS[fp_report_export_2html], bt=[]: self._disable_enable(var, lb, en, bt))
        CBS[cb_check_first_package].configure(command = lambda var=VAR[cb_check_first_package], lb=LBS[dp_check_first_package], en=INS[dp_check_first_package], bt=BTS[dp_check_first_package]: self._disable_enable(var, lb, en, bt))
        CBS[cb_molib_preload_molib].configure(command = lambda var=VAR[cb_molib_preload_molib], lb=LBS[dp_molib_preload_molib], en=INS[dp_molib_preload_molib], bt=BTS[dp_molib_preload_molib]: self._disable_enable(var, lb, en, bt))

        INS[dp_library_tobechecked].configure(validate='focusout', validatecommand=(self.register(self._validate_entry),'%P', dp_library_tobechecked))
        INS[dp_dymola_installation].configure(validate='focusout', validatecommand=(self.register(self._validate_entry),'%P', dp_dymola_installation))         
        INS[dp_check_first_package].configure(validate='focusout', validatecommand=(self.register(self._validate_entry),'%P', dp_check_first_package))               
        
        self.WIDGETS_SESSION = {'CBS': CBS, 'INS': INS, 'LBS': LBS, 'BTS': BTS}
        
    def arrange_widgets(self):
        
        grid = {'ipady': 2, 'padx': 10, 'pady': 8, 'sticky': 'W'}
        options = {'gen': grid}                   
    
        self.SECTIONS['session'].grid(row=0, column=0, **options['gen'])
        self.SECTIONS['logging'].grid(row=0, column=1, **options['gen'])    
        self.SECTIONS['results'].grid(row=1, column=0, columnspan=2, **options['gen'])   
        
        self.arrange_widgets_session()
        self.arrange_widgets_logging()
        self.arrange_widgets_results()
        
        self.FRAME.grid()
        
    def arrange_widgets_results(self):
        BTS = self.WIDGETS_RESULTS['BTS']
        tv_report = self.WIDGETS_RESULTS['TVS']
        scrbar = self.WIDGETS_RESULTS['SCB']

        grid = {'ipady': 2, 'sticky': 'W'}
        options = {'gen': grid,
                   'bts': {**grid, **{'pady': [0,10]}}
                   }
                   
        n=0
        BTS['report_exprt'].grid(row=n, column=0,  **options['bts'])
        BTS['report_open'].grid(row=n, column=0, padx=[120,0],  **options['bts'])
        
        n=n+1
        tv_report.grid(row=n, column=0, columnspan = 2, sticky='WENS')
        scrbar.grid(row = n,column = 2, sticky = "ns")
        
    def arrange_widgets_logging(self):
        grid = {'ipady': 1, 'pady': 4}
        logger = self.WIDGETS_LOGGING['LOG']
        scrbar = self.WIDGETS_LOGGING['SCB']

        n=0
        logger.grid(row = n, column = 0, sticky = "WENS", **grid)
        scrbar.grid(row = n,column = 1, sticky = "ns", **grid)
               

    def arrange_widgets_session(self):
        LBS = self.WIDGETS_SESSION['LBS']
        INS = self.WIDGETS_SESSION['INS']
        BTS = self.WIDGETS_SESSION['BTS']
        CBS = self.WIDGETS_SESSION['CBS']
        
        grid = {'ipady': 2, 'sticky': 'W'}
        options = {'gen': grid,
                   'cbs': {**grid, **{'columnspan': 3}},
                   'ins': {**grid, **{'columnspan': 2}},
                   'lbs': {**grid, **{'columnspan': 2}}
                   }
        
        n=0
        BTS['config_load'].grid(row=n, column=0, columnspan=2, pady=[0,10], **options['gen'])
        BTS['config_save'].grid(row=n, column=1, padx=[40,0], pady=[0,10], **options['gen'])
        
        n=n+1        
        LBS[dp_dymola_installation].grid(row=n, column=0, **options['lbs'])
        INS[dp_dymola_installation].grid(row=n, column=2, **options['ins'])
        BTS[dp_dymola_installation].grid(row=n, column=4, **options['gen'])
        
        n=n+1
        LBS[dp_library_tobechecked].grid(row=n, column=0, **options['lbs'])
        INS[dp_library_tobechecked].grid(row=n, column=2, **options['ins'])
        BTS[dp_library_tobechecked].grid(row=n, column=4, **options['gen'])
        
        n=n+1
        CBS[cb_check_pedantic_mode].grid(row=n, column=0, **options['cbs'])
        
        n=n+1
        CBS[cb_report_compact_mode].grid(row=n, column=0, **options['cbs'])
        
        n=n+1
        CBS[cb_molib_preload_molib].grid(row=n, column=0, **options['cbs'])
        
        n=n+1
        LBS[dp_molib_preload_molib].grid(row=n, column=1, **options['gen'])
        INS[dp_molib_preload_molib].grid(row=n, column=2, **options['ins'])
        BTS[dp_molib_preload_molib].grid(row=n, column=4, **options['gen'])
        
        n=n+1
        CBS[cb_check_first_package].grid(row=n, column=0, **options['cbs'])
        
        n=n+1
        LBS[dp_check_first_package].grid(row=n, column=1, **options['gen'])
        INS[dp_check_first_package].grid(row=n, column=2, **options['ins'])
        BTS[dp_check_first_package].grid(row=n, column=4, **options['gen'])
        
        n=n+1
        CBS[cb_report_export_2html].grid(row=n, column=0, **options['cbs'])
        
        n=n+1
        LBS[fp_report_export_2html].grid(row=n, column=1, **options['gen'])
        INS[fp_report_export_2html].grid(row=n, column=2, **options['ins'])
        
        n=n+1
        BTS['session_run'].grid(row=n, column=2, pady=[25,0], **options['gen'])
        
        # Initial enable/disable
        self._disable_enable(self.VAR[cb_report_export_2html], LBS[fp_report_export_2html], INS[fp_report_export_2html], [])
        self._disable_enable(self.VAR[cb_check_first_package], LBS[dp_check_first_package], INS[dp_check_first_package], BTS[dp_check_first_package])
        self._disable_enable(self.VAR[cb_molib_preload_molib], LBS[dp_molib_preload_molib], INS[dp_molib_preload_molib], BTS[dp_molib_preload_molib])
   
    def session_run(self):
        pass
    
    def config_load(self):
        pass
    
    def config_save(self):
        pass
        
    def report_open(self):
        pass
    
    def report_exprt(self):
        pass
        
       
    def browse_dir_dymola(self):
        initdir = self.VAR[dp_dymola_installation].get() or self.INITIAL[dp_dymola_installation].get()
        if not initdir:
            initdir = 'C:\Program Files (x86)'
     
        dirname = filedialog.askdirectory(parent=self, initialdir=initdir, title='Please select a directory', mustexist = True)         
        
        if dirname:
            self.VAR[dp_dymola_installation].set(dirname)   
    
    def browse_dir_library(self):
        initdir = self.VAR[dp_library_tobechecked].get() or self.INITIAL[dp_library_tobechecked].get()

        dirname = filedialog.askdirectory(parent=self, initialdir = initdir, title='Please select a directory', mustexist = True)         
        if dirname:
            self.VAR[dp_library_tobechecked].set(dirname)
            self.VAR[dp_check_first_package].set(dirname)       
    
    def browse_dir_firstlevel(self):
        initdir = self.VAR[dp_check_first_package].get() or self.VAR[dp_library_tobechecked].get()
          
        dirpath = filedialog.askdirectory(parent=self, initialdir=initdir, title='Please select a directory', mustexist = True)         
        dirname = os.path.basename(dirpath)

        if dirname:
            self.VAR[dp_check_first_package].set(dirname)  
        
    def browse_dir_dependencies(self):
        initdir = self.VAR[dp_molib_preload_molib].get()
        dirname = filedialog.askdirectory(parent=self, initialdir=initdir, title='Please select a directory', mustexist = True)                
        
        if dirname:
            self.VAR[dp_molib_preload_molib].set(dirname)  
        

    def _validate_entry(self, P, name):

        log.info('Changed input of \'{}\' to \'{}\''.format(name, P))
        if not os.path.isdir(P):
            log.warning('Bad Input: Input for {} is not a valid directory path'.format(name))
            return False
        else:
            return True
            
            
    def _disable_enable(self, var, label, entry, button):
        if var.get():
            label.configure(state='normal')
            entry.configure(state='normal')            
            if button:
                button.configure(state='normal')
        else:
            label.configure(state='disabled')
            entry.configure(state='disabled')
            if button:
                button.configure(state='disabled')
        
    def _load_configs(self):
        with open('config2.json') as jsonfile:
            configs = jsonload(jsonfile)
            
        return configs     
      
        
        
#Top Level Code    
if __name__ == "__main__":  

    app = Moliana_Gui(None)
    app.title("Moliana")
    app.mainloop()        