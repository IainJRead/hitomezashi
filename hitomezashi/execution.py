# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 07:33:16 2022

Execution of some hitzomezashi patterns
 
 
@author: IREAD
"""
import os
import geometries
import numpy as np

# TODO:: Make a utils directory and add genStarts to it

def genStarts(sideLen=50, modulo=7, cutOff=4):
    """
    

    Parameters
    ----------
    sideLen : int, optional
        The number of points per side. The default is 50.
    modulo : int, optional
        Numerical base. The default is 7.
    cutOff : int, optional
        Threshold to choose 1 or 0.
        If cutOff >= modulo then none will be set to 1
        The default is 4.

    Returns
    -------
    None.

    """
    
    # Create a pattern of numbers
    starts = np.linspace(1, sideLen, sideLen)%modulo

    # Convert to boolean according to some rule
    starts = starts > cutOff

    # Convert to int for 1s and 0s
    return(starts.astype(int))

choice = 'triangle'

if choice == 'square':
    
    # Create patterns of starts according to some numerical rules
    rowStarts = genStarts(50, 3, 0)
    colStarts = genStarts(50, 6, 4)
    
    # Choose a save folder
    savePathBase = r"C:\Users\iainj\Documents\Python Outputs\Hitomezashi"
    
    # Name the patterna and define a save path
    modeName = "First Pattern"
    savePath = os.path.join(savePathBase, modeName)
    
    # Create image directory
    if os.path.isdir(savePath) is False:
        os.mkdir(savePath)
    
    # Instantiate a cloth, then do some drawing
    square = geometries.squareCloth('myFirst', savePathBase=savePathBase)
    
    square.defineMode(logic='rand', rowStarts=rowStarts, colStarts=colStarts, modeName='First Pattern', thresh=[34, 46])

elif choice == 'triangle':
    
    num_rows = 50
    # Generate patterns of starts
    baseStarts = genStarts(num_rows, 6, 2)
    leftStarts = genStarts(num_rows, 17, 6)
    rightStarts = genStarts(num_rows, 19, 9)
    
    
    # Choose a save folder
    savePathBase = r"C:\Users\iainj\Documents\Python Outputs\Hitomezashi"
    
    # Name the pattern and define a save path
    modeName = "First Tri Pattern"
    savePath = os.path.join(savePathBase, modeName)
    
    # Create image directory
    if os.path.isdir(savePath) is False:
        os.mkdir(savePath)
    
    # Instantiate a cloth, then do some drawing
    tri = geometries.triangleCloth('myFirst', grid = (num_rows, int(np.ceil(num_rows*(17.885/20)))), slope = 0.5, savePathBase=savePathBase)
    
    tri.defineMode(logic='rand', baseStarts=baseStarts, leftStarts=leftStarts, rightStarts=rightStarts, modeName='First Tri Pattern', thresh=[17, 67, 50])