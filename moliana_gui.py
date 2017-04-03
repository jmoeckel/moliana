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

from tkinter import filedialog
from tkinter import INSERT

        
class WidgetLogger(moliana.logging.Handler):
    def __init__(self, widget):
        moliana.logging.Handler.__init__(self)
        self.setLevel(moliana.logging.INFO)
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
        tkinter.Tk.config(self, padx=10, pady=10, bg="white")

                
        self.INITIAL = {'init_dirpath_dymola': 'C:\Program Files (x86)\Dymola 2017 FD01',
                        'init_dirpath_library': 'Q:/Git/AMSUN/HumanBehaviour',                        
                        'init_dirpath_firstlevel': '',
                        'init_dirpath_report': '',
                        'init_filename_report': 'report'
                        }        
        
        self.master = master    
        self.create_widgets()  

        moliana.logger.addHandler(WidgetLogger(self.WIDGETS['tf_logger']))         
        self.arrange_widgets()
        
        
    def create_widgets(self):
        self.VAR = {'dirpath_library': tkinter.StringVar(self, self.INITIAL['init_dirpath_library']),
                    'dirpath_dymola': tkinter.StringVar(self, self.INITIAL['init_dirpath_dymola']),
                    'dirpath_firstlevel':  tkinter.StringVar(self, self.INITIAL['init_dirpath_firstlevel']),
                    'dirpath_report':  tkinter.StringVar(self, self.INITIAL['init_dirpath_report']),
                    'filename_report':  tkinter.StringVar(self, self.INITIAL['init_filename_report']),
                    'pedantic_mode': tkinter.BooleanVar (self, False)
                    }
        
        self.WIDGETS = {'in_dirpath_library': tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_library']),
                        'in_dirpath_dymola':  tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_dymola']),
                        'in_dirpath_firstlevel': tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_firstlevel']),
                        'in_dirpath_report': tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['dirpath_report']),
                        'in_filename_report':  tkinter.Entry(self, width=60, borderwidth=3, textvariable=self.VAR['filename_report']),
                        'bt_opendir_dymola': tkinter.Button(self, text='...', command=self.browse_dir_dymola),
                        'bt_opendir_library': tkinter.Button(self, text='...', command=self.browse_dir_library),
                        'bt_opendir_firstlevel': tkinter.Button(self, text='...', command=self.browse_dir_firstlevel),
                        'bt_opendir_report': tkinter.Button(self, text='...', command=self.browse_dir_report),
                        'bt_run': tkinter.Button(self, text='Run checks', command=self.run_checks),
                        'bt_open_report': tkinter.Button(self, text='Open Report', command=self.open_report),
                        'lb_dirpath_dymola': tkinter.Label(self, bg='white', text='Path to Dymola installation'),
                        'lb_dirpath_library': tkinter.Label(self, bg='white', text='Path to Modelica library'),
                        'lb_dirpath_firstlevel': tkinter.Label(self, bg='white', text='Considered first level'),
                        'lb_dirpath_report': tkinter.Label(self, bg='white', text='Path to Report directory'),
                        'lb_filename_report': tkinter.Label(self, bg='white', text='Name of the report'),
                        'lb_emptyline1': tkinter.Label(self, bg='white', text=' '),
                        'lb_emptyline2': tkinter.Label(self, bg='white', text=' '),
                        'lb_emptyline3': tkinter.Label(self, bg='white', text=' '),                        
                        'cb_pedantic': tkinter.Checkbutton(self, bg='white', text='Execute checkModel() in pedantic mode', variable=self.VAR['pedantic_mode']),
                        'tf_logger': tkinter.Text(self, width=100, height=15, wrap=tkinter.WORD, borderwidth=3, relief="sunken"),
                        'sb_scroll': tkinter.Scrollbar(self)
                        }

        #Adaptions
        self.WIDGETS['sb_scroll'].config(command=self.WIDGETS['tf_logger'].yview)
        
        self.WIDGETS['tf_logger']["yscrollcommand"] = self.WIDGETS['sb_scroll'].set
        self.WIDGETS['tf_logger'].tag_config(tkinter.SEL, lmargin1 = 10, lmargin2 = 10, rmargin = 10)
       

        self.WIDGETS['tf_logger'].insert(0.0, 'Moliana - INFO - Welcome to Moliana')
        

        

    def arrange_widgets(self):
        self.grid()
        
        n = 0 
        self.WIDGETS['lb_dirpath_dymola'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2)  
        self.WIDGETS['lb_dirpath_report'].grid(row = n, column = 10, columnspan = 5, sticky = "W",ipady = 2)
        
        n=n+1
        self.WIDGETS['in_dirpath_dymola'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2)     
        self.WIDGETS['bt_opendir_dymola'].grid(row = n, column = 5, columnspan = 1, sticky = "W",ipady = 2)
        self.WIDGETS['in_dirpath_report'].grid(row = n, column = 10, columnspan = 5, sticky = "W",ipady = 2)     
        self.WIDGETS['bt_opendir_report'].grid(row = n, column = 15, columnspan = 1, sticky = "W",ipady = 2)
        
        n=n+1
        self.WIDGETS['lb_dirpath_library'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2) 
        self.WIDGETS['lb_filename_report'].grid(row = n, column = 10, columnspan = 5, sticky = "W",ipady = 2)
        
        n=n+1   
        self.WIDGETS['in_dirpath_library'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2)     
        self.WIDGETS['bt_opendir_library'].grid(row = n, column = 5, columnspan = 1, sticky = "W",ipady = 2)      
        self.WIDGETS['in_filename_report'].grid(row = n, column = 10, columnspan = 5, sticky = "W",ipady = 2)         
        
        n=n+1
        self.WIDGETS['lb_dirpath_firstlevel'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2) 
        
        n=n+1   
        self.WIDGETS['in_dirpath_firstlevel'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2)     
        self.WIDGETS['bt_opendir_firstlevel'].grid(row = n, column = 5, columnspan = 1, sticky = "W",ipady = 2)   
                
        n=n+1
        self.WIDGETS['lb_emptyline3'].grid(row = n, column = 0, columnspan = 1, sticky = "W",ipady = 2)  
        
        n=n+1
        self.WIDGETS['cb_pedantic'].grid(row = n, column = 0, columnspan = 5, sticky = "W",ipady = 2) 

        n=n+1
        self.WIDGETS['lb_emptyline2'].grid(row = n, column = 0, columnspan = 1, sticky = "W",ipady = 2)  
        
        n=n+1
        self.WIDGETS['bt_run'].grid(row = n, column = 0, columnspan = 1, sticky = "W")
        self.WIDGETS['bt_open_report'].grid(row = n, column = 3, columnspan = 1, sticky = "W")       
        
        n=n+1
        self.WIDGETS['lb_emptyline1'].grid(row = n, column = 0, columnspan = 1, sticky = "W",ipady = 2)  
        
        n=n+1
        self.WIDGETS['tf_logger'].grid(row = n, column = 0, columnspan = 15, sticky = "WENS")
        self.WIDGETS['sb_scroll'].grid(row = n,column = 15, sticky = "ns") 
        
    def run_checks(self):
        pDym = self.VAR['dirpath_dymola'].get()
        pLib = self.VAR['dirpath_library'].get()
        
        options = {'modelica_lib_firstlevel': self.VAR['dirpath_firstlevel'].get(),
                   'dymola_pedantic': self.VAR['pedantic_mode'].get(),
                   'report_path': self.VAR['dirpath_report'].get(),
                   'report_name': self.VAR['filename_report'].get()
                   }
                   
        dm = moliana.DymolaMode(pLib, pDym, **options)
        self.Report = dm.execute_check('html')
        
    def open_report(self):
        filepath_report= os.path.join(self.VAR['dirpath_report'].get(), '.html'.format(self.VAR['filename_report'].get()))
        webbrowser.open(filepath_report)
        
    
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
        dirpath = filedialog.askdirectory(parent=self, initialdir =  self.INITIAL['init_dirpath_firstlevel'], title='Please select a directory', mustexist = True)         
        dirname = os.path.basename(dirpath)
        
        self.VAR['dirpath_firstlevel'].set(dirname)  
        
    def browse_dir_report(self):
        """Opens file browser such that the user could easily choose a directory"""
        dirname = filedialog.askdirectory(parent=self, initialdir =self.INITIAL['init_dirpath_report'], title='Please select a directory', mustexist = True)         
        self.VAR['dirpath_report'].set(dirname)  
    
        
        
#Top Level Code    
if __name__ == "__main__":    

    app = Moliana_Gui(None)
    app.title("Moliana")
    app.mainloop()