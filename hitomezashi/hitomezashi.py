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

TODO:: Update standard draw methods to use just one loop, like the triangle
method does

@author: IREAD
"""
 
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
 
###############################################################################
 
###############################################################################
class hitomezashi(object):
    """
    Hitomezashi stitching patterns are generated using a periodic grid of
    points. The grid can take various shapes (square, triangular, hexagonal,
    some other form of isometric set of points). Along any line of points, we
    draw dashed lines (e.g. connect points 1 and 2, 3 and 4, 5 and 6 etc.)
    These build up into a pattern.
    This class contains methods to draw such patterns.
    """
    
    
    def __init__(self,
                 hName,
                 logic='rand',
                 **kwargs):
        """
        

        Parameters
        ----------
        hName : string
            A name for this instance.
        logic : string, optional
            How the starting states of each line are to be determined. This can
            be pattern, rand or alternate.
            pattern: User defines a sequence of 1s and 0s to specify starting
                'on' or 'off' for a given line.
            rand: Randomly assign starting states based on some threshold and a
                set of random numbers
            alternate: Alternate starting 'on' and 'off' line by line
            The default is 'rand'.
        **kwargs : keyword arguments
            Set of optional arguments for lower level functions to be called
            via the hitomezashi object instance

        Returns
        -------
        None.

        """

        
        # Attach attributes
        self.hName = hName
        self.logic = logic
        
        # Set up default drawing offsets
        self.setOffsets()
        
    def setOffsets(self,
                      wOffset=0,
                      hOffset=0,
                      lwOffset=0,
                      lhOffset=0,
                      mwOffset=0,
                      mhOffset=0):
           """
           Sets up default offset values for various drawing elements.
           TODO::
           This was more relevant in the code's original application. Not sure
           that it really gets used anywhere meaningfully now
    
           Parameters
           ----------
           wOffset : int, optional
               Additional canvas width on right hand side in pixels. The default
               is 200.
           hOffset : int, optional
               Additional canvas height on bottom in pixels. The default is 100.
           lwOffset : int, optional
               Offset x direction in pixels from grid edge to label. The
               default is 10.
           lhOffset : int, optional
               Offset y direction in pixels from stitch_block top to label. The
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
        bName : string or hitomezashi.stitch_block object
            Name of the hitomezashi.stitch_block object to be created.
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
                'leftStarts':None,
                'rightStarts':None,
                'baseStarts':None,
                }
            # Scan through kwargs and populate any missing arguments
            for key, value in defaultDict.items():
                if key not in kwargs.keys():
                    kwargs[key] = value
            
            print(f'kwargs is {kwargs}')
            
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
                                            leftStarts=kwargs['leftStarts'],
                                            rightStarts=kwargs['rightStarts'],
                                            baseStarts=kwargs['baseStarts'],
                                            )
            # create a new drawing canvas based on the new selection of
            # stitch_blocks
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
        
        # attach dimensions to self
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
        
        # draw the canvas
        self.canvas = Image.new('RGB', (int(np.ceil(self.drawWidth)), int(np.ceil(self.drawHeight))), self.background)
        self.draw = ImageDraw.Draw(self.canvas)
            
    def addMode(self,
                mName,
                **kwargs):
        """
        Attaches the passed operating mode to the modes dictionary, or creates
        one from the passed kwargs
        TODO:: This should probably be renamed to something more relevant to 
        stitching patterns. Mode is another relic from the code's original life
 
        Parameters
        ----------
        mName : hitomezashi.operatingMode object, or string
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
        Draws retangular points on the canvas according to the attributes of
        the passed stitch_block
 
        Parameters
        ----------
        block : hitomezashi.stitch_block object
            One of the blocks associated with the detector, to be drawn.
 
        Returns
        -------
        None.
 
        """
        
        # Loop over the number of columns
        for col in range(block.grid[0]):
            # get x coordinate of top left point
            x = block.start[0] + col*(1+block.skip[0])*block.size[0]+2*block.lineWidth
            
            # Loop over the number of rows
            for row in range(block.grid[1]):
                # get y coordinate of top left point
                y = block.start[1] + row*(1+block.skip[1])*block.size[1]+2*block.lineWidth
                # draw the rectangle
                self.draw.rectangle([(x, y), (x+block.size[0]-2*block.lineWidth, y+block.size[1]-2*block.lineWidth)],
                                    fill = block.mask[col][row],
                                    outline = block.linergb)
                    
    def drawTrapezoid(self, block):
        """
         Draws trapezoids on the canvas according to the attributes of
         the passed stitch_block. Only allows sloping of the left and right
         sides of the trapezoid
         
         TODO:: Not used in stitching patterns. Draws an irregular polygon
 
        Parameters
        ----------
        block : hitomezashi.stitch_block object
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
        
        # Lines are drawn for one stitch width, alternating on and off
        
        # We will pass either set patterns of start states, or randomisations
        # with different probabilities of starting on or off

        
        # Sweep through all columns, avoiding drawing on the canvas edge
        for col in range(block.grid[0] - 1):
            # Generate leftmost coordinate of pixel
            x = block.start[0] + (col+1)*(1+block.skip[0])*block.size[0]+block.lineWidth     
            # Sweep through all rows, avoiding drawing on the canvas edge
            for row in range(block.grid[1]-1):
                y = block.start[1] + (row+1)*(1+block.skip[1])*block.size[1]+block.lineWidth
                
                # define the start and end positions of the line and then draw it
                startLoc = (x, y)
                endLoc = (x, y + block.size[1])
                startCond = block.colStarts[col] + row
                
                self.drawLine(block, startCond, startLoc, endLoc)
        
        # Sweep through all rows, avoiding drawing on the canvas edge
        for row in range(block.grid[1] - 1):
            # Generate leftmost coordinate of pixel
            y = block.start[1] + (row+1)*(1+block.skip[1])*block.size[1]+block.lineWidth           
            # Sweep through all columns, avoiding drawing on the canvas edge
            for col in range(block.grid[0]-1):
                x = block.start[0] + (col+1)*(1+block.skip[0])*block.size[0]+block.lineWidth
                
                # define the start and end positions of the line and then draw it
                startLoc = (x, y)
                endLoc = (x + block.size[0], y)
                startCond = block.rowStarts[row] + col
                
                self.drawLine(block, startCond, startLoc, endLoc)

        
    def drawBlock(self, block):
        """
        Draws the stitch array of the passed block, detecting the shape.
 
        Parameters
        ----------
        block : hitomezashi.stitch_block object or list thereof
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
        Clears all masks in the block to refresh for a new sequence
        TODO:: Not really relevant for this implementation, but was for
        handling having blocks coloured differently, generating several
        different drawings, and then animating them into a gif
        Might still have interesting applications with this, if a colouring 
        scheme is defined to colour in enclosed sections
 
        Returns
        -------
        None.
 
        """
        
        # Call the clearmask method on each block
        for key, value in self.blocks.items():
            value.clearMask()
        
    def saveFrame(self, mode):
        """
        Save a snapshot of the canvas
 
        Parameters
        ----------
        mode : hitomezashi.operatingMode object
            The operating mode of which the frame is a part.
 
        Returns
        -------
        None.
 
        """
        # Increment frame counter within the operatingMode and save the frame
        # TODO:: This counter was only used for creating gifs, so not currently
        # used in this implementation
        mode.ct = mode.ct + 1
        saveName = os.path.join(mode.saveFolder, f'Frame {mode.ct}.jpg')
        self.canvas.save(saveName, quality=100)
        
    def drawLine(self, block, startCond, startLoc, endLoc):
        """
        

        Parameters
        ----------
        block : stitch_block object
            The block of stitches, i.e. the grid, to have lines drawn
        startCond : int
            1 or 0, defining the starting state of the line
        startLoc : tuple
            x and y coordinates of the line start
        endLoc : tuple
            x and y coordinates of the line end

        Returns
        -------
        None.

        """
        
        
        # State will be 1 or 0, depending on row number and start state
        state = (startCond)%2
        # Only draw a line if it starts 'on'
        if state == 1:
            self.draw.line((startLoc, endLoc), fill=block.linergb*state, width = 1)
###############################################################################
 
###############################################################################    
class operatingMode(object):
 
    def __init__(self,
                 mName,
                 basePath):
        """
        Object to describe an operating mode, i.e. sequence of frames in which 
        the drawing changes over time, for animation purposes
        TODO:: Not really used at the moment, but could be interesting to make
        some animated patterns, changing from frame to frame according to some
        set of rules
 
        Parameters
        ----------
        mName : string
            The name of the operating mode.
        basePath : string
            Filepath into which to save the frames.
 
        Returns
        -------
        None.
 
        """
        
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
        Object to describe a grid of points. Could tile a few grids together
        
        The self-created mask array contains an rgb colour value per grid section.
        This mask is used during the drawBlock method to colour in sectiond of
        the grid.
 
        Parameters
        ----------
        bName : string
            The name of the stitch block
        size : tuple
            The x and y dimensions of the grid elements
        start : tuple
            The x and y coordinates of the top left of the block.
        grid : tuple
            The number of rows and number of columns
        linergb : tuple, optional
            RGB colour of the line.
            The default is (0, 0, 0).
        skip : tuple, optional
            Number of rows and columns to skip for interleaved blocks.
            The default is (0, 0).
        shape : string, 'rectangle' or 'trapezoid' optional
            The shape of the pixel. The default is 'rectangle'.
        slope : tuple, optional
            Gradient of the left and right hand sides of the grid. Sloping up
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
        
        if shape =='rectangle':
            # Rectangular grids have 2 sides: rows and columns
            self.startList = ['rowStarts', 'colStarts']

        elif shape =='triangle':
            # Triangular grids have 3 sides: base, left and right
            self.startList = ['baseStarts', 'leftStarts', 'rightStarts']
        
        
        # Defaults
        defaultDict = {
            'thresh': None,
            }
            
            
        # Scan through kwargs and populate any missing arguments
        for key, value in defaultDict.items():
            if key not in kwargs.keys():
                kwargs[key] = value
                
        for key in self.startList:
            if key not in kwargs.keys():
                kwargs[key] = None
        
        # Debug
        # print(f'kwargs is {kwargs}')
                
        self.startList = [kwargs[val] for val in self.startList]
        
        # Start with an empty array of pixels
        self.clearMask()
        
        self.__dict__.update((k, v) for k, v in kwargs.items())
        
        self._setStartStates_()
        
    def clearMask(self):
        """
        Sets the grid to be colourless
 
        Returns
        -------
        None.
 
        """
        # Loop through each dimension and make each grid section (0, 0 ,0) colour
        self.mask = [[] for i in range(self.grid[0])]
        for i in range(self.grid[0]):
            self.mask[i] = [(0, 0, 0) for i in range(self.grid[1])]
    
    def _setStartStates_(self):
        
        # Debug
        # print(f'logic is {self.logic}')
        # print(f'startList is {self.startList}')
                
        if self.logic == 'pattern':
            # Not very pythonic. Should really be try and except here
            if all(start is not None for start in self.startList):
                pass
            else:
                raise ValueError('No pattern provided')
        elif self.logic == 'alternate':
            if self.firstStates is not None:
                if self.shape == 'rectangle':
                    self.colStarts = [(i + self.firstStates[0])%2 for i in range(self.grid[0])]
                    self.rowStarts = [(i + self.firstStates[1])%2 for i in range(self.grid[1])]
                elif self.shape == 'triangle':
                    self.baseStarts = [(i + self.firstStates[0])%2 for i in range(self.grid[1])]
                    self.leftStarts = [(i + self.firstStates[1])%2 for i in range(self.grid[1])]
                    self.rightStarts = [(i + self.firstStates[2])%2 for i in range(self.grid[1])]
                    
            else:
                raise ValueError('No first states provided')
        elif self.logic == 'rand':
            if self.thresh is not None:
                if self.shape == 'rectangle':
                    randomNums = np.random.uniform(low=0, high=100, size=self.grid[0])
                    self.colStarts = [math.floor(elem/self.thresh[0]) for elem in randomNums]
                    randomNums = np.random.uniform(low=0, high=100, size=self.grid[1])
                    self.rowStarts = [math.floor(elem/self.thresh[1]) for elem in randomNums]
                elif self.shape == 'triangle':
                    randomNums = np.random.uniform(low=0, high=100, size=self.grid[0])
                    self.baseStarts = [math.floor(elem/self.thresh[0]) for elem in randomNums]
                    randomNums = np.random.uniform(low=0, high=100, size=self.grid[0])
                    self.leftStarts = [math.floor(elem/self.thresh[1]) for elem in randomNums]
                    randomNums = np.random.uniform(low=0, high=100, size=self.grid[0])
                    self.rightStarts = [math.floor(elem/self.thresh[2]) for elem in randomNums]
            else:
                raise ValueError('No thresholds provided')
            

###############################################################################
 
############################################################################### 
class hitomezashi_tri(hitomezashi):
    """
    A child class of hitomezashi with methods for creating a triangular grid
    """
    
    
    def drawStitches(self, block):
        """
        

        Parameters
        ----------
        block : hitomezashi.stitch_block instance
            the block in which to draw stitches

        Returns
        -------
        None.

        """
        
        
        # The pattern defines the starting state of the line of stitches. 1 is
        # on and 0 is off
        
        # Loop through each pixel of the block and draw the lines in the given
        # axis
        
        # Lines are drawn for one pixel width, alternating on and off
        
        # We will pass either set patterns of start states, or randomisations
        # with different probabilities
        
        # Unpack gradients
        lgrad, rgrad = block.slope
        meangrad = (lgrad+rgrad)/2
        
        # We draw by running along horizontal lines of points and adding up to
        # three lines from each one. Work out how many horizontal lines
        # (layers) we have in the grid
        layers = block.grid[0] - 1
        
        # # Need to shift the start (LHS) of first line in row 2 onwards.
        # # Depending on the slope of the sides, this will have a variable period or
        # # no period at all. Create a list of initial position offsets to apply.
        # shift_vals = [0]
        # first_shift = self.shift
        # while 1 - first_shift/block.size[0] > 1E-6 and len(shift_vals) < block.grid[1]:
        #     shift_vals.append(first_shift)
        #     first_shift = first_shift + self.shift
        #     # Check for values that would 'skip' the first point
        #     if first_shift > block.size[0] and first_shift < 2*block.size[0]:
        #         first_shift = first_shift - block.size[0]
           
        # period = len(shift_vals)
                
        # Sweep through all rows, avoiding drawing on the canvas edge
        for row in range(layers):
            # Generate leftmost coordinate of pixel.
            y = block.start[1] + (row+1)*(1+block.skip[1])*block.size[1] + block.lineWidth
            # Calculate number of columns in this row
            # Sweep through all columns, avoiding drawing on the canvas edge
            for col in range(row):
                # x = block.start[0] + \
                x = 0.25*block.grid[0]*block.size[0] + \
                    (col+1)*(1+block.skip[0])*block.size[0] + \
                        block.lineWidth + \
                            (np.floor(block.grid[0]/2)-row)*meangrad*block.size[0] #\
                                # + shift_vals[row%period]
                # Debug
                # if row == 1 and col == 0:
                #     print(f'x is {x}')
                #     print(f'grid size is {block.grid[0]*block.size[0]}')
                
                # Generate a 3-pt co-ordinate system for identifying each point
                # on the lattice. This will call the appropriate state
                
                # (B, L, R)
                # B = Base, L = Left, R = Right
                # B = row numer
                # L is numRows --> numRows - row number
                # R is numRows - row number --> numRows
                
                # block.grid[1] - 1 = t
                
                # Top is 0, t, t
                # Next row down is (1, t, t-1) ; (1, t-1, t)
                # (2, t, t-2) ; (2, t-1, t-1) ; (2, t - 2, t)
                # etc.
                
                tot = 2*(layers-1)
                L_R_min = layers - row
                R_idx = L_R_min + col
                L_idx = tot - row - R_idx
                
                # Lines are drawn 'upwards' from points for L/R and rightwards
                # for base.
                
                # Right lines
                startLoc = (x, y)
                endLoc = (x + block.size[0]*rgrad, y + block.size[1])
                startCond = block.rightStarts[L_idx] + col
                
                
                self.drawLine(block, startCond, startLoc, endLoc)
                
                if col < row and row >= 1:
                    # Left lines
                    endLoc = (x - block.size[0]*lgrad, y + block.size[1])
                    startCond = block.leftStarts[R_idx] + col
                    
                    self.drawLine(block, startCond, startLoc, endLoc)
                    
                if col < row-1 and row >=1:
                    # Base lines
                    endLoc = (x + block.size[0], y)
                    startCond = block.baseStarts[row] + col
                    
                    
                    self.drawLine(block, startCond, startLoc, endLoc)

