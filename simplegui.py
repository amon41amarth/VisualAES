#!/usr/bin/env python

import slowaes
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygameui as ui
from pygame.locals import *

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
    def editSBox(self):
        self.addPointInHistory()
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

    def onButtonClick(self, btn, mbtn):
        if btn.text == "Edit SBox":
            self.editSBox()
        elif btn.text == "RoundKeys":
            self.runRoundKeys()
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
        self.updateMiddleColumn()

        self.cleartext = self.cleartext + " J"
        self.mode, self.orig_len, self.ciph = self.moo.encrypt(self.cleartext, self.moo.modeOfOperation["CBC"],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
        print self.ciph

    def updateView(self, text, view, size):
        """
            This method accepts a string, cipher/plain text (text), and updates the view (view) given.
            The size is a tuple (#,#) that is the resulting size.
        """
        if(len(text) == 0):
            return
        surf = pygame.Surface((len(text), 1))
        surf = surf.convert()
        # Alter surf according to the string.
        run = 0
        for pix in text:

            if(isinstance(text, str)):
                num = ord(pix)
            else:
                num = pix
            #argb = self.getRGB(num)
            argb = (num,num,num,num)
            surf.set_at((run, 0), (Color(argb[1],argb[2],argb[3],argb[0])))
            run+=1

        view.image = pygame.transform.scale(surf,size)

    def updateLeftColumn(self):
        """ This should update the left column """
        print "ULC"
        # Left column doesn't need to be encrypted, we're using the plaintext.

        self.updateView(self.plaintextone_textfield.text, self.plaintextone_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
        self.updateView(self.plaintexttwo_textfield.text, self.plaintexttwo_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )

    def updateRightColumn(self):
        """ This should update the right column """
        # Right column needs to be encrypted.
        print "URC"
        self.mode, self.orig_len, ptoEncrypted = self.moo.encrypt(self.plaintextone_textfield.text, self.moo.modeOfOperation["CBC"],
            self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
        self.updateView(ptoEncrypted, self.cipherone_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
        self.mode, self.orig_len, pttEncrypted = self.moo.encrypt(self.plaintexttwo_textfield.text, self.moo.modeOfOperation["CBC"],
            self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
        self.updateView(pttEncrypted, self.ciphertwo_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )

    def updateCenterColumn(self):
        """ This should update the center column """
        print "Update center"


    def updateColumns(self):
        """ This updates all the columns.  Redraws the left, right, and center. """
        self.updateLeftColumn()
        self.updateMiddleColumn()
        self.updateRightColumn()


    def onTextChanged(self, tf, text):
        """  tf is the TextField object.
            Text is the text the TextField was changed to.
        """
        if tf.placeholder == "Plain Text One":
            self.pto = text; # Plain Text One
        elif tf.placeholder == "Plain Text Two":
            self.ptt = text # Plain Text Two
        else:
            print "Don't know what to do..."

        self.updateColumns()

    def drawTopButtons(self):
        topButtonNames = ["Edit SBox","RoundKeys","SubBytes", "ShiftRows","MixColumns","Run Round","Operation Modes"]
        numButtons = len(topButtonNames)
        buttonWidth = self.frame.w / numButtons
        buttonX = (buttonWidth + VSMALL_MARGIN)
        self.buttons = []
        for i in range (0, numButtons):
            btn = ui.Button(
                ui.Rect(i * buttonX, 10, 0, 20),
                topButtonNames[i])
            btn.on_clicked.connect(self.onButtonClick)
            self.add_child(btn)

    def drawLinesForGrid(self):
        """
            This draws the grid lines.
            This includes the two lines going top to bottom for each column.
            This also includes the bar below the buttons at the top and the
            middle horizontal line separating the two plain texts, cipher texts
            and current progress.
        """

        # Draw bottom of top button bar.
        slider = ui.SliderView(
            ui.Rect(0, self.buttonBarBottom-2, self.frame.w, self.buttonBarBottom+2),
            ui.HORIZONTAL, 0, 1, False)
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
            ui.Rect(0, self.middleBarY+(self.label_height/2), self.frame.w, 4),
            ui.HORIZONTAL, 0, 1, False)
        slider.value = 1
        self.add_child(slider)
    def load_image(self, file_name, colorkey=False, image_directory='data'):
        file = os.path.join(image_directory, file_name)
        _image = pygame.image.load(file)
        if colorkey:
            if colorkey == -1:
            # If the color key is -1, set it to color of upper left corner
                colorkey = _image.get_at((0, 0))
            _image.set_colorkey(colorkey)
            _image = _image.convert()
        else: # If there is no colorkey, preserve the image's alpha per pixel.
            _image = _image.convert_alpha()
        return _image
    def drawLeftColumn(self):
        """
            This draws the left column.
            This column consists of two surfaces showing the initial string,
            along input text boxes for the strings.
        """
        import os
        print os.getcwd() # Keep this in. You may need to put an empty image at this location.
        self.empty = self.load_image("empty.png")
        self.plaintextone_imageview = ui.ImageView(
            ui.Rect(0, self.buttonBarBottom+  MARGIN, self.columnWidth,self.middleBarY + MARGIN),
            self.empty)
        self.add_child(self.plaintextone_imageview)

        self.plaintexttwo_imageview = ui.ImageView(ui.Rect(0, self.middleBarY + MARGIN, self.columnWidth,self.frame.h),
            self.empty)
        self.add_child(self.plaintexttwo_imageview)

        # Draw these text fields at end so they're on top of the pictures.
        self.plaintextone_textfield = ui.TextField(
            ui.Rect(0, self.middleBarY-15, 200, self.label_height),
            placeholder='Plain Text One')
        self.plaintextone_textfield.centerx = self.frame.centerx
        self.plaintextone_textfield.text = "Hello"
        self.plaintextone_textfield.on_text_change.connect(self.onTextChanged)
        self.add_child(self.plaintextone_textfield)

        self.plaintexttwo_textfield = ui.TextField(
            ui.Rect(0, self.middleBarY+15, 200, self.label_height),
            placeholder='Plain Text Two')
        self.plaintexttwo_textfield.centerx = self.frame.centerx
        self.plaintexttwo_textfield.text = "World"
        self.plaintexttwo_textfield.on_text_change.connect(self.onTextChanged)
        self.add_child(self.plaintexttwo_textfield)

    def drawRightColumn(self):
        """
            This draws the right column.
            This will be the normal result of the plain texts if ran normally
            through AES.
        """
        self.cipherone_imageview = ui.ImageView(ui.Rect(self.columnWidth*2, self.buttonBarBottom+  MARGIN, self.columnWidth,self.middleBarY + MARGIN),
            self.empty)
        self.add_child(self.cipherone_imageview)

        self.ciphertwo_imageview = ui.ImageView(ui.Rect(self.columnWidth*2, self.middleBarY + MARGIN, self.columnWidth,self.frame.h),
            self.empty)
        self.add_child(self.ciphertwo_imageview)


    def drawCenterColumn(self):
        """
            This draws the center column.
            This will be the current cipher keys and a slider at the bottom
            for history.
        """
        self.currentone_imageview = ui.View(ui.Rect(self.columnWidth, self.buttonBarBottom +  MARGIN, self.columnWidth,self.middleBarY + MARGIN))
        self.add_child(self.currentone_imageview)

        self.currenttwo_imageview = ui.View(ui.Rect(self.columnWidth, self.middleBarY + MARGIN, self.columnWidth,self.frame.h))
        self.add_child(self.currenttwo_imageview)

        # Draw history slider
        self.history = ui.SliderView(
            ui.Rect(self.columnWidth + SMALL_MARGIN, self.frame.h-MARGIN, self.columnWidth-MARGIN, SMALL_MARGIN),
            ui.HORIZONTAL, 0, 1, True)
        self.history.value = 1
        self.history.on_value_changed.connect(self.historyChanged)
        self.add_child(self.history)

    def addPointInHistory(self):
        # To do.
        self.history.high = self.history.high + 1
        self.history.value = self.history.high
        print "Adding point in history"

    def resetHistory(self):
        print "History reset"

    def historyChanged(self, slider_view, value):
        # To do.
        print "We're in history change mode! Now at: " + str(value)

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
        self.buttonBarBottom = self.label_height+VSMALL_MARGIN
        self.columnWidth = self.frame.w/3
        self.middleBarY = (self.frame.h - self.buttonBarBottom) / 2

        self.drawTopButtons()
        self.drawLeftColumn()
        self.drawRightColumn()
        self.drawCenterColumn()

        self.drawLinesForGrid() # Always call last so that they're on top.

    def layout(self):
        ui.Scene.layout(self)

    def update(self, dt):
        ui.Scene.update(self, dt)

    def getRGB(self, num):
        a = (num >> 6) & 0xff
        r = (num >> 4) & 0xff
        g = (num >> 2) & 0xff
        b = (num >> 0) & 0xff
        isGoing = True
        while(isGoing):
            print str(num) + ": " + str(a) +","+str(r)+","+str(g)+","+str(b)

            isGoing = False
            if(a * 2 < 256):
                if(a != 0):
                    isGoing = True
                a = a * 2
            if(r * 2 < 256):
                if(r != 0):
                    isGoing = True
                r = r * 2
            if(g * 2 < 256):
                if(g != 0):
                    isGoing = True
                g = g * 2
            if(b * 2 < 256):
                if(b != 0):
                    isGoing = True
                b = b * 2

        print str(num) + ": " + str(a) +","+str(r)+","+str(g)+","+str(b)
        return (a,r,g,b)


if __name__ == '__main__':
    import pygame
    pygame.init()
    infoObject = pygame.display.Info()
    size = width, height = int(infoObject.current_w/2), int(infoObject.current_h/2)
    ui.init('pygameui - Kitchen Sink',size)
#    pygame.display.set_mode((width*2, height*2))

    ui.scene.push(KitchenSinkScene())
    ui.run()
