#!/usr/bin/env python

import random, slowaes
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygameui as ui

import logging
log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


LIST_WIDTH = 180
MARGIN = 20
SMALL_MARGIN = 10
VSMALL_MARGIN = 1


class KitchenSinkScene(ui.Scene):

    def drawTopButtons(self):
        topButtonNames = ["Edit SBox","RoundKeys","SubBytes", "ShiftRows","MixColumns","Run Round","Operation Modes"]
        numButtons = len(topButtonNames)
        buttonHeight = 20
        self.buttonBarBottom = buttonHeight + MARGIN
        buttonWidth = self.frame.w / numButtons
        buttonX = (buttonWidth + VSMALL_MARGIN)
        self.buttons = []
        for i in range (0, numButtons):
            btn = ui.Button(
                ui.Rect(i * buttonX, 10, 0, buttonHeight),
                topButtonNames[i])
            btn.on_clicked.connect(self.processButtonClick)
            self.add_child(btn)
            
    def editSBox(self):
        print "Edit S Box"
    
    def runRoundKeys(self):
        print "Run round keys"
        
    def runSubBytes(self):
        print "Run sub bytes"
        
    def runShiftRows(self):
        print "Run shift rows"
    
    def runMixColumns(self):
        print "Run mix columns"
    
    def runRound(self):
        print "Run round"
    
    def changeOperationMode(self):
        print "Change operation mode"
    
    def updateMiddleColumn(self):
        print "Updating middle column"
    
    def processButtonClick(self, btn, mbtn):
        if btn.text == "Edit SBox":
            self.editSBox()
        elif btn.text == "RoundKeys":
            self.runROundKeys()
        elif btn.text == "SubBytes":
            self.runSubBytes()
        elif btn.text == "ShiftRows":
            self.runShiftRows()
        elif btn.text == "MixColumns":
            self.runMixColumns()
        elif btn.text == "Run Round":
            self.runRound()
        elif btn.text == "Operation Modes":
            self.changeOperationMode()
        else:
            print "Don't know what to do"
        # We don't always have to update the middle column. But just so it's easy to read and less bull crap lines, 
        # we'll bbe updating it everytime this method is called.
        updateMiddleColumn()
        
        self.cleartext = self.cleartext + " J"
        self.mode, self.orig_len, self.ciph = self.moo.encrypt(self.cleartext, self.moo.modeOfOperation["CBC"],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
        print self.ciph
        
    def drawLinesForGrid(self):
        """
            This draws the grid lines.
            This includes the two lines going top to bottom for each column.
            This also includes the bar below the buttons at the top and the 
            middle horizontal line separating the two plain texts, cipher texts
            and current progress.
        """
    
        self.columnWidth = self.frame.w/3
        self.verticalBarY = (self.frame.h - self.buttonBarBottom) / 2
        
        # Draw bottom of top button bar.
        slider = ui.SliderView(ui.Rect(
            0, self.buttonBarBottom-2, self.frame.w, self.buttonBarBottom+2), ui.HORIZONTAL, 0, 1, False)
        slider.value = 1
        self.add_child(slider)
        
        # Draw columns
        for x in range(1,4):
            slider = ui.SliderView(
                ui.Rect(self.columnWidth * x, self.buttonBarBottom, 4, self.frame.h), 
                ui.VERTICAL, 0, 1, False)
            slider.value = 1
            self.add_child(slider)
        
        # Draw center bar.
        slider = ui.SliderView(
            ui.Rect(0, self.verticalBarY-2, self.frame.w, 4), 
            ui.HORIZONTAL, 0, 1, False)
        slider.value = 1
        self.add_child(slider)
        
    def drawLeftColumn(self):
        """ 
            This draws the left column. 
            This column consists of two surfaces showing the initial string, 
            along input text boxes for the strings.
        """
        
        frame = ui.Rect(10, self.buttonBarBottom, 200, self.label_height)
        self.plaintextone_textfield = ui.TextField(frame, placeholder='Plain Text One')
        self.plaintextone_textfield.centerx = self.frame.centerx
        self.add_child(self.plaintextone_textfield)
        frame = ui.Rect(10, self.buttonBarBottom, 200, self.label_height)
        self.plaintexttwo_textfield = ui.TextField(frame, placeholder='Plain Text Two')
        self.plaintexttwo_textfield.centerx = self.frame.centerx
        self.add_child(self.plaintexttwo_textfield)
        
    def drawRightColumn(self):
        """ 
            This draws the right column.  
            This will be the normal result of the plain texts if ran normally 
            through AES. 
        """
        print "Drawing right"
        
    def drawCenterColumn(self):
        """ 
            This draws the center column. 
            This will be the current cipher keys and a slider at the bottom 
            for history. 
        """
        print "Drawing center"
        
    def __init__(self):
        ui.Scene.__init__(self)
        self.cleartext = ""
        self.moo = slowaes.AESModeOfOperation()
        self.cleartext = ""
        self.cypherkey = [143,194,34,208,145,203,230,143,177,246,97,206,145,92,255,84]
        self.iv = [103,35,148,239,76,213,47,118,255,222,123,176,106,134,98,92]
        self.mode, self.orig_len, self.ciph = self.moo.encrypt(self.cleartext, self.moo.modeOfOperation["CBC"],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
        self.label_height = ui.theme.current.label_height
        scrollbar_size = ui.SCROLLBAR_SIZE
        infoObject = pygame.display.Info()
        size = width, height = int(infoObject.current_w), int(infoObject.current_h)

        frame = ui.Rect(MARGIN, MARGIN, width, height)

        self.drawTopButtons()
        self.drawLeftColumn()
        self.drawRightColumn()
        self.drawCenterColumn()
        
        self.drawLinesForGrid() # Always call last so that they're on top.

    def layout(self):
        ui.Scene.layout(self)

    def update(self, dt):
        ui.Scene.update(self, dt)

if __name__ == '__main__':
    import pygame
    pygame.init()
    infoObject = pygame.display.Info()
    size = width, height = int(infoObject.current_w/2), int(infoObject.current_h/2)
    ui.init('pygameui - Kitchen Sink',size)
#    pygame.display.set_mode((width*2, height*2))
    
    ui.scene.push(KitchenSinkScene())
    ui.run()
