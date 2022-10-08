# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 07:33:16 2022
 
 
# TODO:: Extend treatment to electrodes within pixel
# TODO:: Extend for other operating modes
 
 
@author: IREAD
"""
import os
import geometries
import numpy as np

# Create a pattern of numbers
rowStarts = np.linspace(1, 50, 50)%3
colStarts = np.linspace(1, 50, 50)%6
# Convert to boolean according to some rule
rowStarts = rowStarts > 0
colStarts = colStarts > 4
# Convert to int for 1s and 0s
rowStarts = rowStarts.astype(int)
colStarts = colStarts.astype(int)

# Choose a save folder
savePathBase = r"C:\Users\iainj\Documents\Python Outputs\Hitomezashi"

# Set up for accumulation mode
modeName = "First Pattern"
savePath = os.path.join(savePathBase, modeName)

# Create image directory
if os.path.isdir(savePath) is False:
    os.mkdir(savePath)

square = geometries.squareCloth('myFirst', savePathBase=savePathBase)

square.defineMode(logic='rand', rowStarts=rowStarts, colStarts=colStarts, modeName='First Pattern', thresh=[34, 46])
  
# Create aliases for the detector blocks for ease of use
A = square.blocks['A']