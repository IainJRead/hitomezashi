# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 12:04:04 2022
 
@author: IREAD
"""

import hitomezashi as hit
import math
import numpy as np

###############################################################################
 
############################################################################### 
 
class squareCloth(hit.hitomezashi):
    

    def __init__(self,
                 hName,
                 blocks = {},
                 modes = {},
                 quant=20,
                 savePathBase=r"C:\Users\iainj\Documents\Python Outputs\Hitomezashi"):
        
        """
        A square 'cloth' onto which a pattern is to be stitched

        Parameters
        ----------
        hName : String
            Name of this instance
        blocks : dictionary, optional
            Dict of hitomezashi.stitch_blocks. The default is {}.
        modes : dictionary, optional
            Dict of hitomezashi.operatingModes. The default is {}.
        quant : int, optional
            Unit size of grid element. The default is 20.
        savePathBase : String, optional
            Base save location for output files

        Returns
        -------
        None.

        """
        
        # Inherit the rest of the init method from hitomezashi.hitomezashi
        super().__init__(hName=hName, blocks=blocks, modes=modes, quant=quant)
        
        # Define the inputs for however many blocks to be included on the cloth
        self.grids = {
            'A': (50, 50),
        }
 
        # Dictionary of pixel sizes per block in (w, h)
        self.sizes = {
            'A': (quant, quant),
            }
 
        # Dictionary of starting positions for each stitch_block (x, y)
        # Build piece by piece since the dimensions of one block may affect the
        # starting location of the next
        self.starts = {}
 
        self.starts['A'] = (0, 0)
        self.quant= quant
        self.blocks = blocks
        self.modes = modes
        self.savePathBase = savePathBase
        
        
    def defineMode(self, logic, modeName, **kwargs):
        """
        Method to define a 'mode' for this cloth
        TODO:: Revise use of 'mode' to something more appropriate

        Parameters
        ----------
        logic : string
            pattern, rand or alternate
        modeName : string
            The name for this mode
        **kwargs : keyword arguments
            Keyword args to instantiate other classes and call lower level
            methods

        Returns
        -------
        None.

        """
        
        
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
 
        # Label each block for debug
        # self.drawLabels()
        
        self.saveFrame(self.modes['First Pattern'])
        
class triangleCloth(hit.hitomezashi_tri):
    
    def __init__(self,
                 hName,
                 blocks={},
                 modes={},
                 quant=20,
                 grid = (100, 90),
                 slope = 0.5,
                 savePathBase=r"C:\Users\iainj\Documents\Python Outputs\Hitomezashi"):
        """
        

        Parameters
        ----------
        hName : String
            Name of this instance
        blocks : dictionary, optional
            Dict of hitomezashi.stitch_blocks. The default is {}.
        modes : dictionary, optional
            Dict of hitomezashi.operatingModes. The default is {}.
        quant : int, optional
            Unit size of grid element. The default is 20.
        savePathBase : String, optional
            Base save location for output files
        grid : tuple, optional
            The height and width of the triangle. The default is (100, 90).
        slope : int, optional
            gradient of the edges. The default is 0.5.
        savePathBase : string, optional
            Directory into which to save images

        Returns
        -------
        None.

        """
        
        # inherit the rest of the init method from the parent class
        super().__init__(hName=hName, blocks=blocks, modes=modes, quant=quant)
        self.quant= quant
        self.blocks = blocks
        self.modes = modes
        self.savePathBase = savePathBase
        self.slope = slope
        
        self.grids = {
            'A': grid
            }
        
        # Extract the angle from the gradient
        angle = np.arctan(self.slope)
        qheight = quant*np.cos(angle)
        
        # Dictionary of pixel sizes per block in (w, h)
        self.sizes = {
            'A': (quant, qheight),
            }
        
        # Dictionary of starting positions for each stitch_block (x, y)
        # Built piece by piece since the dimensions of one block may affect the
        # starting location of the next
        
        self.starts = {}

        self.starts['A'] = (0, 0)
        
        # TODO:: Specify a row by row shift for a triangular grid
        self.shift = slope*quant
        # Will need to modify/create a new drawStitches method to incorporate
        # angles and shifts
        
    def defineMode(self, logic, modeName, **kwargs):
        """
        

        Parameters
        ----------
        logic : string
            Pattern, rand or alternate
        modeName : string
            The name for this mode
        **kwargs : keyword arguments
            Keyword args to instantiate other classes and call lower level
            methods

        Returns
        -------
        None.

        """
        
        
        # Defaults
        defaultDict = {
            'baseStarts': None,
            'leftStarts': None,
            'rightStarts': None,
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
                      slope = (self.slope, self.slope),
                      logic=logic,
                      shape='triangle',
                      baseStarts=self.baseStarts,
                      leftStarts=self.leftStarts,
                      rightStarts=self.rightStarts,
                      thresh=self.thresh,
                      )
        
        self.A = self.blocks['A']
        
        self.addMode(modeName, basePath=self.savePathBase)
            
        # Draw detector with all blocks empty
        self.drawStitches(self.blocks['A'])
 
        # Label each block for debug
        # self.drawLabels()
        
        self.saveFrame(self.modes['First Tri Pattern'])