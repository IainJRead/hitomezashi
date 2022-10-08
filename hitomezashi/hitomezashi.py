# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 08:29:54 2022
 
Library to allow drawings of hitomezashi stitching patterns
 
Allows snapshots (frames) to be saved and collated into gifs, such that the 
sequence may be animated
 
stitch_block objects are created for each of the subpatterns to be created
From these blocks, a hitomezashi object is instantiated. When blocks are added
it calls the _createCanvas_ method to create the ImageDraw.draw object on which
all the lines will be drawn

@author: IREAD
"""
 
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
 
###############################################################################
 
###############################################################################
class hitomezashi(object):
    
    def __init__(self,
                 hName,
                 logic='rand',
                 **kwargs):

        
        # Attach attributes
        self.hName = hName
        self.logic = logic
        
        # Set up default drawing offsets
        self.setOffsets()
        
    def setOffsets(self,
                      wOffset=200,
                      hOffset=100,
                      lwOffset=10,
                      lhOffset=5,
                      mwOffset=10,
                      mhOffset=10):
           """
           Sets up default offset values for various drawing elements
    
           Parameters
           ----------
           wOffset : int, optional
               Additional canvas width on right hand side in pixels. The default
               is 200.
           hOffset : int, optional
               Additional canvas height on bottom in pixels. The default is 100.
           lwOffset : int, optional
               Offset x direction in pixels from detector edge to label. The
               default is 10.
           lhOffset : int, optional
               Offset y direction in pixels from pixel_block top to label. The
               default is 5.
           mwOffset : int, optional
               Offset x direction in pixels from left hand side of canvas for 
               message string. The default is 10.
           mhOffset : int, optional
               Offset y direction in pixels from bottom of canvas for message 
               string. The default is 10.
    
           Returns
           -------
           None.
    
           """
           # Attach attributes
           self.wOffset = wOffset
           self.hOffset = hOffset
           self.lwOffset = lwOffset
           self.lhOffset = lhOffset
           self.mwOffset = mwOffset
           self.mhOffset = mhOffset
           
           # If a canvas has already been created, then update it with the new
           # canvas width and height
           if 'draw' in dir(self):
               self._createCanvas_()

        
                
    def addBlock(self,
                 bName,
                 **kwargs):
        """
        Populates the blocks dictionary with the passed stitch_block, or creates
        one based on kwargs
        
        Parameters
        ----------
        bName : string or schematic_PIL.stitch_block object
            Name of the schematic_PIL.stitch_block object to be created.
        **kwargs : keyword arguments
            Keyword arguments to instantiate the stitch_block object. Any
            optional arguments left out will be defaulted
 
        Returns
        -------
        None.
 
        """
        
        # If bName is a stitch block then simply update dictionary of blocks.
        # Otherwise, create a stitch block
        if isinstance(bName, stitch_block):
            self.blocks[bName.name] = bName
        else:
            # Defaults
            defaultDict = {
                'linergb': (255, 255, 255),
                'skip': (0, 0),
                'shape':'rectangle',
                'slope': (0, 0),
                'lineWidth': 1,
                'rowStarts': None,
                'colStarts': None,
                'thresh': None,
                }
            # Scan through kwargs and populate any missing arguments
            for key, value in defaultDict.items():
                if key not in kwargs.keys():
                    kwargs[key] = value
            
            # Instantiate a stitch_block object
            self.blocks[bName] = stitch_block(bName,
                                            size = kwargs['size'],
                                            start = kwargs['start'],
                                            grid = kwargs['grid'],
                                            linergb = kwargs['linergb'],
                                            skip = kwargs['skip'],
                                            shape = kwargs['shape'],
                                            slope = kwargs['slope'],
                                            lineWidth = kwargs['lineWidth'],
                                            colStarts = kwargs['colStarts'],
                                            rowStarts = kwargs['rowStarts'],
                                            logic = kwargs['logic'],
                                            thresh = kwargs['thresh'],
                                            )
            self._createCanvas_()
        
    def _getDimensions_(self):
        """
        Internal method to extract the dimensions of the pattern from the
        stitch_blocks which have been appended to it.
 
        Returns
        -------
        None.
 
        """
        
        # Search through the blocks for the widest and tallest points
        xends = []
        yends = []
        for key, value in self.blocks.items():
            xends.append(value.start[0] + value.grid[0]*(1+value.skip[0])*value.size[0])
            yends.append(value.start[1] + value.grid[1]*(1+value.skip[1])*value.size[1])
            
        self.detWidth = max(xends)
        self.detHeight = max(yends)
    
    def _createCanvas_(self):
        """
        Internal method to generate a canvas on which to draw the detector,
        based on the dimensions detected from the stitch_blocks
 
        Returns
        -------
        None.
 
        """
        
        # Detect the dimensions of the stitch_blocks
        self._getDimensions_()
        
        # Offset the detector dimenions and create a canvas
        self.drawWidth = self.detWidth + self.wOffset
        self.drawHeight = self.detHeight + self.hOffset
        self.font = ImageFont.truetype("arial.ttf", 30)
        self.fontColour = (0, 0, 0)
        self.background = (255, 255, 255)
        
        self.canvas = Image.new('RGB', (self.drawWidth, self.drawHeight), self.background)
        self.draw = ImageDraw.Draw(self.canvas)
            
    def addMode(self,
                mName,
                **kwargs):
        """
        Attaches the passed operating mode to the modes dictionary, or creates
        one from the passed kwargs
 
        Parameters
        ----------
        mName : schematic_PIL.operatingMode object, or string
            name of the operatingMode to be appended or created.
        **kwargs : keyword arguments
            arguments to instantiate an operatingMode object. Missing optional
            arguments will be defaulted
 
        Returns
        -------
        None.
 
        """
        # Check if mName is already and object and simply add it to the 
        # dictionar if so. Otherwise, create one from the passed kwargs
        if isinstance(mName, operatingMode):
            self.modes[mName] = mName
        else:
            # Create defaults
            defaultDict = {
                'basePath': None
                }
            # Populate  missing defaults
            for key, value in defaultDict.items():
                if key not in kwargs.keys():
                    kwargs[key] = value
            # Instantiate operatingMode
            self.modes[mName] = operatingMode(mName,
                                              basePath = kwargs['basePath'],
                                              )
        
    def drawRect(self, block):
        """
        Draws retangular pixels on the canvas according to the attributes of
        the passed stitch_block
 
        Parameters
        ----------
        block : schematic_PIL.stitch_block object
            One of the blocks associated with the detector, to be drawn.
 
        Returns
        -------
        None.
 
        """
        
        for col in range(block.grid[0]):
            x = block.start[0] + col*(1+block.skip[0])*block.size[0]+2*block.lineWidth
            
            for row in range(block.grid[1]):
                y = block.start[1] + row*(1+block.skip[1])*block.size[1]+2*block.lineWidth
                self.draw.rectangle([(x, y), (x+block.size[0]-2*block.lineWidth, y+block.size[1]-2*block.lineWidth)],
                                    fill = block.mask[col][row],
                                    outline = block.linergb)
                    
    def drawTrapezoid(self, block):
        """
         Draws trapezoidal pixels on the canvas according to the attributes of
         the passed stitch_block. Only allows sloping of the left and right
         sides of the pixel.
 
        Parameters
        ----------
        block : schematic_PIL.stitch_block object
            One of the blocks associated with the detector, to be drawn.
 
        Returns
        -------
        None.
 
        """
        # Unpack gradients of left and right edges
        lgrad, rgrad = block.slope
        
        # Sweep through all columns
        for col in range(block.grid[0]):
            # Generate leftmost coordinate of pixel
            x = block.start[0] + col*(1+block.skip[0])*block.size[0]+block.lineWidth
            # Sweep through all rows
            for row in range(block.grid[1]):
                # Calculate uppermost coordinate of pixel
                y = block.start[1] + row*(1+block.skip[1])*block.size[1]+block.lineWidth
                # Generate the four vertices of the pixel, based on the passed
                # gradients
                v1x = x + block.size[1]*row*lgrad
                v1y = y
                
                v2x = x + block.size[0] - block.size[1]*row*rgrad
                v2y = y
                
                v3x = x + block.size[0] - block.size[1]*(row+1)*rgrad
                v3y = y + block.size[1]
                
                v4x = x + block.size[1]*(row + 1)*lgrad
                v4y = y + block.size[1]
                
                # Draw the resultant trapezoid
                self.draw.polygon([(v1x, v1y), (v2x, v2y), (v3x, v3y), (v4x, v4y)],
                                  fill = block.mask[col][row],
                                  outline = block.linergb)
    
    def drawStitches(self, block):
        
        # The pattern defines the starting state of the line of stitches. 1 is
        # on and 0 is off
        
        # Loop through each pixel of the block and draw the lines in the given
        # axis
        
        # Lines are drawn for one pixel width, alternating on and off
        
        # We will pass either set patterns of start states, or randomisations
        # with different probabilities

        
        # Sweep through all columns, avoiding drawing on the canvas edge
        for col in range(block.grid[0] - 1):
            # Generate leftmost coordinate of pixel
            x = block.start[0] + (col+1)*(1+block.skip[0])*block.size[0]+block.lineWidth     
            # Sweep through all rows, avoiding drawing on the canvas edge
            for row in range(block.grid[1]-1):
                y = block.start[1] + (row+1)*(1+block.skip[1])*block.size[1]+block.lineWidth
                
                startloc = (x, y)
                endloc = (x, y + block.size[1])
                
                # State will be 1 or 0, depending on row number and start state
                state = (block.colStarts[col] + row)%2
                
                if state == 1:
                    self.draw.line((startloc, endloc), fill=block.linergb*state, width = 1)
        
        # Sweep through all columns, avoiding drawing on the canvas edge
        for row in range(block.grid[1] - 1):
            # Generate leftmost coordinate of pixel
            y = block.start[1] + (row+1)*(1+block.skip[1])*block.size[1]+block.lineWidth           
            # Sweep through all rows, avoiding drawing on the canvas edge
            for col in range(block.grid[0]-1):
                x = block.start[0] + (col+1)*(1+block.skip[0])*block.size[0]+block.lineWidth
                
                startloc = (x, y)
                endloc = (x + block.size[0], y)
                
                # State will be 1 or 0, depending on row number and start state
                state = (block.rowStarts[row] + col)%2
                
                if state == 1:
                    self.draw.line((startloc, endloc), fill=block.linergb*state, width = 1)
        
    def drawBlock(self, block):
        """
        Draws the pixel array of the passed block, detecting the shape.
 
        Parameters
        ----------
        block : schematic_PIL.stitch_block object or list thereof
            One of the blocks associated with the detector, to be drawn.
 
        Returns
        -------
        None.
 
        """
        # If the argument is a stitch_block then call the relevant draw method
        if isinstance(block, stitch_block):
            if block.shape.lower() == 'trapezoid':
                self.drawTrapezoid(block)
            else:
                self.drawRect(block)
       # If the argument is a list then recursively call drawBlock on the items         
        elif isinstance(block, list) or isinstance(block, tuple):
            for i, entry in enumerate(block):
                self.drawBlock(block[i])
    
    def drawPattern(self):
        """
        Draws all stitch blocks in the pattern
 
        Returns
        -------
        None.
 
        """
        # Loop through all blocks and draw them
        for key, value in self.blocks.items():
            self.drawBlock(self.blocks[key])
    
    def drawLabels(self):
        """
        Adds labels for each structure on the right hand side of the canvas in 
        the offset space
 
        Returns
        -------
        None.
 
        """
        # If two blocks start at the same height we want to offset the y coord 
        # of one of them.
        lastLabel = None
        for key, value in self.blocks.items():
            if value.start[1] == lastLabel and lastLabel is not None:
                lheight = value.start[1] + value.grid[1]*value.size[1]/2
                lastLabel = lheight
            else:
                lheight = value.start[1]
                lastLabel = lheight
            
            # Draw the label at (x, y). Each label is the name of the relevant
            # stitch_block
            self.draw.text((self.detWidth + self.lwOffset,
                            lheight + self.lhOffset),
                           value.bName,
                           value.linergb,
                           font=self.font)
            
    def drawMessage(self,
                   lString):
        """
        Adds a message string on the bottom of the canvas in the offset space
 
        Parameters
        ----------
        lString : string
            Message to be added.
 
        Returns
        -------
        None.
 
        """
        # Draw a background colour rectangle to cover up the previous message
        self.draw.rectangle([(self.mwOffset, self.detHeight + self.mhOffset),
                             (self.drawWidth, self.drawHeight)],
                            fill = self.background,
                            outline = self.background)
        # Draw the new message
        self.draw.text((self.mwOffset, self.detHeight + self.mhOffset),
                       lString,
                       self.fontColour,
                       font=self.font)
        
    def clearMasks(self):
        """
        Clears all masks in the detector to refresh for a new sequence
 
        Returns
        -------
        None.
 
        """
        
        for key, value in self.blocks.items():
            value.clearMask()
        
    def saveFrame(self, mode):
        """
        Save a snapshot of the canvas
 
        Parameters
        ----------
        mode : schematic_PIL.operatingMode object
            The operating mode of which the frame is a part.
 
        Returns
        -------
        None.
 
        """
        # Increment frame counter within the operatingMode and save the frame
        mode.ct = mode.ct + 1
        saveName = os.path.join(mode.saveFolder, f'Frame {mode.ct}.jpg')
        self.canvas.save(saveName, quality=100)
###############################################################################
 
###############################################################################    
class operatingMode(object):
 
    def __init__(self,
                 mName,
                 basePath = None):
        """
        Object to describe an operating mode of the detector, defining the
        sequence of charge transfers and integrations
 
        Parameters
        ----------
        mName : string
            The name of the operating mode.
        basePath : string, optional
            Filepath into which to save the frames. The default is None.
 
        Returns
        -------
        None.
 
        """
        # If no argument is provided then use the default
        if basePath is None:
            basePath = r'C:\Users\IREAD\Documents\Jupyter 3_10'
        
        # Attach attributes
        self.mName = mName
        self.ct = 0
        self.saveFolder = os.path.join(basePath, self.mName)
           
    def makeGif(self,
                duration=100):
        """
        Collate saved frames into an animated gif
 
        Returns
        -------
        None.
 
        """
        # Create list of saved files in the directory
        filenames = [f'Frame {i+1}.jpg' for i in range(self.ct-1)]
        filePaths = [os.path.join(self.saveFolder, filenames[i]) for i, _ in enumerate(filenames)]
        
        # Open each frame and save them into a gif
        frames = [Image.open(image) for image in filePaths]
        frame_one = frames[0]
        saveName = f'{self.saveFolder}\\{self.mName}_sequence.gif'
        frame_one.save(saveName, format="GIF", append_images=frames,
                   save_all=True, duration=duration, loop=0)
        
        print('Done')
        
        
###############################################################################
 
###############################################################################
class stitch_block(object):
    
    def __init__(self,
                 bName,
                 size,
                 start,
                 grid,
                 linergb=(0, 0, 0),
                 skip=(0, 0),
                 shape='rectangle',
                 slope=(0, 0),
                 lineWidth=1,
                 logic='pattern',
                 **kwargs):
        """
        Object to describe a functional block of identical pixels, forming a
        region of the detector.
        
        The self-created mask array contains an rgb colour value per pixel.
        This mask is used during the schematic_PIL.detector.drawBlock method
        to colour in the pixels which contain charge
 
        Parameters
        ----------
        bName : string
            The name of the pixel block.
        size : tuple
            The x and y dimensions of the pixels.
        start : tuple
            The x and y coordinates of the top left pixel in the block.
        grid : tuple
            The number of rows and number of columns of the block.
        linergb : tuple, optional
            RGB colour of the line with which to draw the pixel block.
            The default is (0, 0, 0).
        skip : tuple, optional
            Number of rows and columns to skip for interleaved blocks.
            The default is (0, 0).
        shape : string, 'rectangle' or 'trapezoid' optional
            The shape of the pixel. The default is 'rectangle'.
        slope : tuple, optional
            Gradient of the left and right hand sides of the pixel. Sloping up
            from left to right is considered positive. The default is (0, 0).
        lineWidth : int, optional
            Width of the line in pixels. The default is 1.
 
        Returns
        -------
        None.
 
        """
        # Attach attributes
        self.bName = bName
        self.size = size
        self.start = start
        self.grid = grid
        self.linergb = linergb
        self.skip = skip
        self.shape = shape
        self.slope = slope
        self.lineWidth = lineWidth
        self.logic = logic
        
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
        
        # Start with an empty array of pixels
        self.clearMask()
        
        self.__dict__.update((k, v) for k, v in kwargs.items())
        
        self._setStartStates_()
        
    def clearMask(self):
        """
        Sets the pixels in the array to appear empty
 
        Returns
        -------
        None.
 
        """
        # Loop through each dimension and make each pixel (0, 0 ,0) colour
        self.mask = [[] for i in range(self.grid[0])]
        for i in range(self.grid[0]):
            self.mask[i] = [(0, 0, 0) for i in range(self.grid[1])]
    
    def _setStartStates_(self):
        
        print(f'logic is {self.logic}')
                
        if self.logic == 'pattern':
            if self.rowStarts is not None and self.colStarts is not None:
                pass
            else:
                raise ValueError('No pattern provided')
        elif self.logic == 'alternate':
            if self.firstStates is not None:
                self.colStarts = [(i + self.firstStates[0])%2 for i in range(self.grid[0])]
                self.rowStarts = [(i + self.firstStates[1])%2 for i in range(self.grid[1])]
            else:
                raise ValueError('No first states provided')
        elif self.logic == 'rand':
            if self.thresh is not None:
                randomNums = np.random.uniform(low=0, high=100, size=self.grid[0])
                self.colStarts = [math.floor(elem/self.thresh[0]) for elem in randomNums]
                randomNums = np.random.uniform(low=0, high=100, size=self.grid[1])
                self.rowStarts = [math.floor(elem/self.thresh[1]) for elem in randomNums]
            else:
                raise ValueError('No thresholds provided')
            
            
        
###############################################################################
 
############################################################################### 
 

