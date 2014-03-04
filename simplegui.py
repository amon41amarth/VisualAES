#!/usr/bin/env python

import slowaes
import sys
import os
import entropy


#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygameui as ui
from pygame.locals import *
"""
import logging
log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
"""

LIST_WIDTH = 100
MARGIN = 20
SMALL_MARGIN = 10
VSMALL_MARGIN = 1

class MainScene(ui.Scene):
    aes = slowaes.AES()
    aesmoo = slowaes.AESModeOfOperation()
    def convertStates(self):
        if(type(self.lbEntry) == type("") ):
            self.lbEntry = self.aesmoo.convertString(self.lbEntry, 0,  len(self.lbEntry), self.aesmoo.modeOfOperation[self.operationMode])

        if(type(self.ltEntry) == type("") ):
            print "Converting the First state " + str(self.ltEntry)
            self.ltEntry = self.aesmoo.convertString(self.ltEntry, 0,  len(self.ltEntry), self.aesmoo.modeOfOperation[self.operationMode])

    def editSBox(self):
        print "Edit s box"
    def runRoundKeys(self):
        self.convertStates()
        #self.currentOne.one.addRoundKey(self.currentOne.one.createRoundKey())
    def runSubBytes(self):
        self.convertStates()
        self.aes.state = self.ltEntry
        self.aes.isInv = False
        self.ltEntry = self.aes.subBytes()
        self.aes.state = self.lbEntry
        self.aes.isInv = False
        self.lbEntry = self.aes.subBytes()
        self.updateMiddleColumn()
    def runShiftRows(self):
        self.convertStates()
        self.aes.state = self.ltEntry
        self.aes.isInv = False
        self.ltEntry = self.aes.shiftRows()
        self.aes.state = self.lbEntry
        self.aes.isInv = False
        self.lbEntry = self.aes.shiftRows()
        self.updateMiddleColumn()
        self.convertStates()
    def runMixColumns(self):
        self.convertStates()
        self.aes.state = self.ltEntry
        self.aes.isInv = False
        self.ltEntry = self.aes.mixColumns()
        self.aes.state = self.lbEntry
        self.aes.isInv = False
        self.lbEntry = self.aes.mixColumns()
        self.updateMiddleColumn()
    def runRound(self):
        print "Run round"
    def switchKeyPlaintextMode(self, btn):
        top = self.lefttop_textfield.label.text
        bottom = self.leftbottom_textfield.label.text
        middle = self.leftmiddle_textfield.label.text
        if("2 Key" in btn.text):
            btn.text = "2 Plaintexts 1 Key"
        else:
            btn.text = "1 Plaintext 2 Keys"
        self.leftbottom_textfield.label.text = ""
        self.lefttop_textfield.label.text = middle
        self.leftmiddle_textfield.label.text = top
        self.leftbottom_textfield.text = ""
        self.lefttop_textfield.text = middle
        self.leftmiddle_textfield.text = top
        self.ptkMode = btn.text #This is to hold if we're doign 2 keys or 1 key
        self.updateColumns()
    def showEntropy(self):
        e = entropy.Entropy()
        original = e.getAllEntropies(self.lefttop_textfield.text, self.leftbottom_textfield.text)
        states = e.getAllEntropies(self.ltEntry, self.lbEntry)
        crypts = e.getAllEntropies(self.ptoEncrypted, self.pttEncrypted)
        if( self.originalEntropy != None):
            self.originalEntropy._dismiss(None, None)
            self.originalEntropy = None
        if( self.statesEntropy != None):
            self.statesEntropy._dismiss(None, None)
            self.statesEntropy = None
        if( self.cryptsEntropy != None):
            self.cryptsEntropy._dismiss(None, None)
            self.cryptsEntropy = None
        self.originalEntropy = ui.show_alert_test(title='', message=original, position='Left')
        self.statesEntropy = ui.show_alert_test(title='', message=states, position='Center')
        self.cryptsEntropy = ui.show_alert_test(title='', message=crypts, position='Right')

    def historyForward(self):
        print "Forward"
    def historyBackward(self):
        print "Backward"
    def onButtonClick(self, btn, mbtn):
        if "SBox" in btn.text:
            self.editSBox()
        elif "Round" in btn.text:
            self.runRoundKeys()
        elif "Sub" in btn.text:
            self.runSubBytes()
        elif "Shift" in btn.text:
            self.runShiftRows()
        elif "Mix" in btn.text:
            self.runMixColumns()
        elif "Run Round" in btn.text:
            self.runRound()
        elif "Plaintext" in btn.text:
            self.switchKeyPlaintextMode(btn)
        elif "<--" in btn.text:
            self.historyBackward()
        elif "-->" in btn.text:
            self.historyForward()
        elif "Entropy" in btn.text:
            self.showEntropy()
        else:
            print "Don't know what to do"
        # We don't always have to update the middle column. But just so it's easy to read and less bull crap lines,
        # we'll be updating it everytime this method is called.
        self.updateMiddleColumn()

        self.cleartext = self.cleartext + " J"
        self.mode, self.orig_len, self.ciph = self.moo.encrypt(self.cleartext, self.moo.modeOfOperation[self.operationMode],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
    def updateView(self, text, view, size):
        """
            This method accepts a string, cipher/plain text (text), and updates the view (view) given.
            The size is a tuple (#,#) that is the resulting size.
        """
        if(len(text) == 0):
            return
        #surf = pygame.Surface((len(text), 1))
        surf = pygame.Surface((4, 4))
        surf = surf.convert()
        # Alter surf according to the string.
        col = 0
        row = 0
        for pix in text:
            if(isinstance(text, str)):
                num = ord(pix)
            else:
                num = pix
            if(self.visualization == "Color" ):
                argb = self.getRGB(num)
            else:
                argb = (num,num,num,num)
            surf.set_at((col, row), (Color(argb[1],argb[2],argb[3],argb[0])))
            col = col + 1
            if(col == 4):
                col = 0
                row = row + 1
        view.image = pygame.transform.scale(surf,(self.columnWidth, self.middleBarY -  self.buttonBarBottom - MARGIN))
    def histogramOnView(self, text, view):
        nums = []
        for x in range(0,256):
            nums.append(0)
        for x in text:
            if(type(x) == type(0)):
                nums[x] = nums[x] + 1
            else:
                nums[ord(x)] = nums[ord(x)] + 1
        height = 0
        for x in range(0, len(nums)):
            if(nums[x] > height):
                height = nums[x]
        surf = pygame.Surface((255, height+1))
        surf = surf.convert()
        for x in range(0, 255):
            for y in range(0,nums[x]):
                surf.set_at((x,y), (Color(255,0,0)))
        view.image = pygame.transform.rotate(pygame.transform.scale(surf,(self.columnWidth, self.middleBarY -  self.buttonBarBottom - MARGIN)), 180)


    def updateMiddleColumn(self):
        if(self.visualization == "Greyscale" or self.visualization == "Color" ):
            self.updateView(self.ltEntry, self.currentone_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
            self.updateView(self.lbEntry, self.currenttwo_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
        elif(self.visualization == "Histogram"):
            self.convertStates()
            self.histogramOnView(self.ltEntry, self.currentone_imageview)
            self.histogramOnView(self.lbEntry, self.currenttwo_imageview)

    def updateLeftColumn(self):
        """ This should update the left column """
        # Left column doesn't need to be encrypted, we're using the plaintext.
        if(self.visualization == "Greyscale" or self.visualization == "Color" ):
            self.updateView(self.lefttop_textfield.text, self.plaintextone_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
            self.updateView(self.leftbottom_textfield.text, self.plaintexttwo_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
        elif(self.visualization == "Histogram"):
            self.histogramOnView(self.lefttop_textfield.text, self.plaintextone_imageview)
            self.histogramOnView(self.leftbottom_textfield.text, self.plaintexttwo_imageview)
    def updateRightColumn(self):
        """ This should update the right column """
        # Right column needs to be encrypted.
        if(self.visualization == "Greyscale" or self.visualization == "Color" ):
            self.mode, self.orig_len, self.ptoEncrypted = self.moo.encrypt(self.lefttop_textfield.text, self.moo.modeOfOperation[self.operationMode],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
            self.updateView(self.ptoEncrypted, self.cipherone_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
            self.mode, self.orig_len, self.pttEncrypted = self.moo.encrypt(self.leftbottom_textfield.text, self.moo.modeOfOperation[self.operationMode],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
            self.updateView(self.pttEncrypted, self.ciphertwo_imageview,  ( self.columnWidth, self.middleBarY + MARGIN) )
        elif(self.visualization == "Histogram"):
            self.mode, self.orig_len, self.ptoEncrypted = self.moo.encrypt(self.lefttop_textfield.text, self.moo.modeOfOperation[self.operationMode],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
            self.histogramOnView(self.ptoEncrypted, self.cipherone_imageview)
            self.mode, self.orig_len, self.pttEncrypted = self.moo.encrypt(self.leftbottom_textfield.text, self.moo.modeOfOperation[self.operationMode],
                self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
            self.histogramOnView(self.pttEncrypted, self.ciphertwo_imageview)

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
            self.ltEntry = self.pto
        elif tf.placeholder == "Plain Text Two":
            self.ptt = text # Plain Text Two
            self.lbEntry = self.ptt
        else:
            print "Don't know what to do..."

        self.updateColumns()
    def moo_changed(self, selection_view, item, index):
        self.operationMode = str(item)
        self.updateColumns()
    def round_number_changed(self, selection_view, item, index):
        print "Round number changed."
        self.updateColumns()
    def expanded_key_size_changed(self, selection_view, item, index):
        print "Expanded key size changed"
        self.updateColumns()
    def visualization_changed(self, selection_view, item, index):
        print "Visual changed " + str(item)
        self.visualization = str(item)
        self.updateColumns()
    def drawTopBar(self):
        topButtonNames = ["Run Round","Round Keys", "RoundNumber", "EKeySize", "Sub Bytes", "Shift Rows", "Mix Columns", "MOO" ]
        numButtons = len(topButtonNames)
        buttonWidth = self.frame.w / numButtons
        buttonX = (buttonWidth + VSMALL_MARGIN)
        view = None
        for i in range (0, len(topButtonNames)):
            if(topButtonNames[i] == "RoundNumber"):
                # Draw the spinner for modes of operation
                modes = ["1","2","3","4","5","6","7","8","9","10","11","12",
                        "13","14","15","16","17","18","19","20","21","22",
                        "23","24","25","26","27","28","29","30","31","32"]
                labels2 = [ui.Label(
                    ui.Rect(0, 0, LIST_WIDTH, self.label_height),
                    modes[j]) for j in range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(
                    ui.Rect(i * buttonWidth, 0, LIST_WIDTH, self.label_height),
                    labels2)
                view.on_selection_changed.connect(self.round_number_changed)
            elif (topButtonNames[i] == "EKeySize"):
                # Draw the spinner for modes of operation
                modes = ["128","192","256"]
                labels2 = [ui.Label(
                    ui.Rect(0, 0, LIST_WIDTH, self.label_height),
                    modes[j]) for j in range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(
                    ui.Rect(i * buttonWidth, 0, LIST_WIDTH, self.label_height),
                    labels2)
                view.on_selection_changed.connect(self.expanded_key_size_changed)
            elif (topButtonNames[i] == "MOO"):
                # Draw the spinner for modes of operation
                modes = ["OFB","CFB","CBC"]
                labels2 = [ui.Label(
                    ui.Rect(0, 0, LIST_WIDTH, self.label_height),
                    modes[j]) for j in range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(
                    ui.Rect(i * buttonWidth, 0, LIST_WIDTH, self.label_height),
                    labels2)
                view.on_selection_changed.connect(self.moo_changed)
            else:
                if(view == None):
                    view = ui.Button(
                        ui.Rect(VSMALL_MARGIN, 10, buttonWidth, 20),
                        topButtonNames[i])
                else:
                    view = ui.Button(
                        ui.Rect(i * buttonWidth, 10, buttonWidth, 20),
                        topButtonNames[i])
                view.on_clicked.connect(self.onButtonClick)
            self.add_child(view)
    def drawBottomBar(self):
        bottomButtonNames = ["2 Plaintexts 1 Key","Edit SBox", "<--", "-->", "Entropy", "Visualization"]
        numButtons = len(bottomButtonNames)
        buttonWidth = self.frame.w / numButtons
        buttonX = (buttonWidth + VSMALL_MARGIN)
        view = None
        for i in range (0, len(bottomButtonNames)):
            if(bottomButtonNames[i] == "Visualization"):
                # Draw the spinner for modes of operation
                modes = ["Greyscale", "Color", "Sound", "Histogram" , "Punchcard", "Bit Compare"]
                labels2 = [ui.Label(
                    ui.Rect(0, 0, LIST_WIDTH, self.label_height),
                    modes[j]) for j in range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(
                    ui.Rect(i * buttonWidth, self.frame.h-self.label_height, LIST_WIDTH, self.label_height),
                    labels2, False)
                view.on_selection_changed.connect(self.visualization_changed)
            else:
                if(view == None):
                    view = ui.Button(
                        ui.Rect(VSMALL_MARGIN, self.frame.h-self.label_height, buttonWidth, 20),
                        bottomButtonNames[i])
                else:
                    view = ui.Button(
                        ui.Rect(i * buttonWidth, self.frame.h-self.label_height, buttonWidth, 20),
                        bottomButtonNames[i])
                view.on_clicked.connect(self.onButtonClick)
            self.add_child(view)
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
    def load_image(self, file_name, colorkey=False, image_directory=''):
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
        self.plaintextone_imageview = ui.ImageView(
            ui.Rect(0, self.buttonBarBottom+  MARGIN, self.columnWidth,self.middleBarY + MARGIN),
            self.empty)
        self.add_child(self.plaintextone_imageview)

        self.plaintexttwo_imageview = ui.ImageView(ui.Rect(0, self.middleBarY + MARGIN, self.columnWidth,self.frame.h),
            self.empty)
        self.add_child(self.plaintexttwo_imageview)

        # Draw these text fields at end so they're on top of the pictures.
        self.lefttop_textfield = ui.TextField(
            ui.Rect(0, self.middleBarY-15, self.columnWidth/2, self.label_height),
            placeholder='Plain Text One')
        self.lefttop_textfield.centerx = self.frame.centerx
        self.lefttop_textfield.text = self.ltEntry = "Hello"
        self.lefttop_textfield.on_text_change.connect(self.onTextChanged)
        self.add_child(self.lefttop_textfield)

        self.leftbottom_textfield = ui.TextField(
            ui.Rect(0, self.middleBarY+15, self.columnWidth/2, self.label_height),
            placeholder='Plain Text Two')
        self.leftbottom_textfield.centerx = self.frame.centerx
        self.leftbottom_textfield.text = self.lbEntry = "World"
        self.leftbottom_textfield.on_text_change.connect(self.onTextChanged)
        self.add_child(self.leftbottom_textfield)

        self.leftmiddle_textfield = ui.TextField(
            ui.Rect(self.leftbottom_textfield.frame.right, self.middleBarY, self.columnWidth/2, self.label_height),
            placeholder='LM')
        self.leftmiddle_textfield.centerx = self.frame.centerx
        self.leftmiddle_textfield.text = self.lmEntry = "Password"
        self.leftmiddle_textfield.on_text_change.connect(self.onTextChanged)
        self.leftmiddle_textfield.bring_to_front()
        self.add_child(self.leftmiddle_textfield)

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
        self.currentone_imageview = ui.ImageView(ui.Rect(self.columnWidth, self.buttonBarBottom +  MARGIN, self.columnWidth,self.middleBarY + MARGIN),
            self.empty)
        self.add_child(self.currentone_imageview)

        self.currenttwo_imageview = ui.ImageView(ui.Rect(self.columnWidth, self.middleBarY + MARGIN, self.columnWidth,self.frame.h),
            self.empty)
        self.add_child(self.currenttwo_imageview)

        # Draw history slider
        #self.history = ui.SliderView(
        #    ui.Rect(self.columnWidth + SMALL_MARGIN, self.frame.h-MARGIN, self.columnWidth-MARGIN, SMALL_MARGIN),
        #    ui.HORIZONTAL, 0, 1, True)
        #self.history.value = 1
        #self.history.on_value_changed.connect(self.historyChanged)
        #self.add_child(self.history)

    def addPointInHistory(self):
        # To do.
        self.history.high = self.history.high + 1
        self.history.value = self.history.high

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
        self.originalEntropy = None
        self.statesEntropy = None
        self.cryptsEntropy = None
        self.operationMode = "CBC"
        self.visualization = "Greyscale"
        self.cypherkey = [143,194,34,208,145,203,230,143,177,246,97,206,145,92,255,84]
        self.iv = [103,35,148,239,76,213,47,118,255,222,123,176,106,134,98,92]
        self.mode, self.orig_len, self.ciph = self.moo.encrypt(self.cleartext, self.moo.modeOfOperation[self.operationMode],
                    self.cypherkey, self.moo.aes.keySize["SIZE_128"], self.iv)
        self.label_height = ui.theme.current.label_height
        infoObject = pygame.display.Info()
        size = width, height = int(infoObject.current_w), int(infoObject.current_h)

        frame = ui.Rect(MARGIN, MARGIN, width, height)
        self.buttonBarBottom = self.label_height+VSMALL_MARGIN
        self.columnWidth = self.frame.w/3
        self.middleBarY = (self.frame.h - self.buttonBarBottom) / 2
        import os
        print os.getcwd() # Keep this in. You may need to put an empty image at this location.
        self.empty = self.load_image("empty.png")

        self.drawTopBar()
        self.drawBottomBar()

        self.drawRightColumn()
        self.drawCenterColumn()
        self.drawLinesForGrid()
        self.drawLeftColumn()
        self.updateColumns()
    def layout(self):
        ui.Scene.layout(self)
    def update(self, dt):
        ui.Scene.update(self, dt)
        self.updateColumns()
    def getRGB(self, num):
        a = 255
        r = ((num >> 5) & 0x7) * 36
        g = ((num >> 2) & 0x7) * 36
        b = ((num >> 0) & 0x3) * 85
        return (a,r,g,b)
if __name__ == '__main__':
    import pygame
    pygame.init()
    infoObject = pygame.display.Info()
    size = width, height = int(infoObject.current_w/2), int(infoObject.current_h/2)
    ui.init('AES Encryption Viewer',size)
    ui.scene.push(MainScene())
    ui.run()
