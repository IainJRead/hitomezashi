# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 12:04:04 2022
 
@author: IREAD
"""
import hitomezashi as hit
import math
import numpy as np
 
class squareCloth(hit.hitomezashi):
    
    def __init__(self,
                 hName,
                 blocks = {},
                 modes = {},
                 quant=20,
                 savePathBase=r"C:\Users\iainj\Documents\Python Outputs\Hitomezashi"):
        
        super().__init__(hName=hName, blocks=blocks, modes=modes, quant=quant)

        self.grids = {
            'A': (50, 50),
        }
 
        # Dictionary of pixel sizes per block in (w, h)
        self.sizes = {
            'A': (2*quant, 2*quant),
            }
 
        # Dictionary of starting positions for each stitch_block (x, y)
        # Built piece by piece since the dimensions of one block may affect the
        # starting location of the next
        self.starts = {}
 
        self.starts['A'] = (0, 0)
        self.quant= quant
        self.blocks = blocks
        self.modes = modes
        self.savePathBase = savePathBase
        
        
    def defineMode(self, logic, modeName, **kwargs):
        
        # Defaults
        defaultDict = {
            'rowStarts': None,
            'colStarts': None,
            'thresh': None,
            }
        # Scan through kwargs and populate any missing arguments
        for key, value in defaultDict.items():
            if key not in kwargs.keys():
                kwargs[key] = value
        
        self.__dict__.update((k, v) for k, v in kwargs.items())
        
        
        # Create a square grid. This is our 'perforated' cloth
        self.addBlock('A',
                      size=self.sizes['A'],
                      start=self.starts['A'],
                      grid=self.grids['A'],
                      linergb=(0, 0, 255),
                      logic=logic,
                      rowStarts=self.rowStarts,
                      colStarts=self.colStarts,
                      thresh=self.thresh,
                      )
        
        self.A = self.blocks['A']
        
        self.addMode(modeName, basePath=self.savePathBase)
            
        # Draw detector with all blocks empty
        self.drawStitches(self.blocks['A'])
 
        # Label each block
        self.drawLabels()
        
        self.saveFrame(self.modes['First Pattern'])