# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 12:33:23 2017

@author: jmoeckel
"""

import os
from datetime import datetime

import logging
import logging.config


def configure(name, log_path):
    
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}
        },
        
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.path.join(log_path, datetime.now().strftime('%Y_%m_%d_%H_%M_%S.log')),
            }
        },        
        'loggers': {
            'CORE': {
                'level': 'INFO',
                'handlers': ['console', 'file']
            },
            'GUI': {
                'level': 'INFO',
                'handlers': ['console', 'file']                    
            }
        },
        'disable_existing_loggers': False
    })
    return logging.getLogger(name)