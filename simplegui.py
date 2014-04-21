#!/usr/bin/python
# -*- coding: utf-8 -*-

import slowaes
import sys
import os
import entropy
import collections
import numpy
import math

import pygameui as ui
from pygame.locals import *

## Used for UI, a drop down width.
LIST_WIDTH = 100
## Represents a normal margin in UI
MARGIN = 20
## A small margin for the UI.
SMALL_MARGIN = 10
## A very small margin for the UI.
VSMALL_MARGIN = 1

## This marks a point in history.
# mt is middle top.
# mb is middle bottom.
# Because we only track middle column, ignore everything else.
class HistoryPoint(object):

    def __init__(self, mt, mb):
        self.mt = mt
        self.mb = mb

    def __str__(self):
        return str(self.mt)

## A Scene object, from the pygameui library.
# Draws all our UI for the visualization.
class MainScene(ui.Scene):

    ## An aes object to use to encrypt strings and call subroutine methods.
    aes = slowaes.AES()
    # Also used with the aes object, for the OFB, CFB, etc.
    aesmoo = slowaes.AESModeOfOperation()
    curRound = 1


    # Not sure if this takes in an array.
    # Complained about "int[] numbers" (I know why)
    def setToProbDist(self, numbers):
        std = numpy.std(numbers) # 72
        mean = numpy.mean(numbers) # 116
        pi = 3.14159265359
        x = 256

        (1/(2 * pi * 72 * 72)) * ()

        # This is the formula for a PDF (according to multiple sources)
        # The ** is used for exponential calculations (0.5 for squareroots)
        # Also I have no idea was "x" is in the formula or what it should be
        return (1 / (2 * pi * std ** 0.5)) * (math.exp(-(((x - mean) ** 2) / (2 * (std ** 0.5)))))

    ## one and two are both probability distributions for the sets.
    def kl(self, one, two):
        #p = numpy.asarray(self.setToProbDist(one), dtype=numpy.int)
        #q = numpy.asarray(self.setToProbDist(two), dtype=numpy.int)
        #print p
        #print q
        p = 1
        q = 1
        return numpy.sum(numpy.where(p != 0, p * numpy.log(p / q), 0))

    ## Converts input to usable (With slowaes) int arrays.
    # Should take care of if it's 1 plaintext 2 keys or 2 plaintexts 1 key
    def convertStates(self):
        try:
            # Always do the IV.
            if type(self.lrbEntry) == type(''):
                self.lrbEntry = self.aesmoo.convertString(self.lrbEntry, 0, len(self.lrbEntry),
                            self.aesmoo.modeOfOperation[self.operationMode])

        except AttributeError:
            pass # Ignore error.

        try:
            # Always do the key.
            if type(self.lrtEntry) == type(''):
                self.lrtEntry = self.aesmoo.convertString(self.lrtEntry, 0, len(self.lrtEntry),
                            self.aesmoo.modeOfOperation[self.operationMode])

        except AttributeError:
            pass # Ignore error.
        try:
            if self.ptkMode == '2P1K':
                if type(self.llbEntry) == type(''):
                    self.llbEntry = self.aesmoo.convertString(self.llbEntry,
                            0, len(self.llbEntry),
                            self.aesmoo.modeOfOperation[self.operationMode])

                if type(self.lltEntry) == type(''):
                    self.lltEntry = self.aesmoo.convertString(self.lltEntry,
                            0, len(self.lltEntry),
                            self.aesmoo.modeOfOperation[self.operationMode])
            elif self.ptkMode == '1P2K':
                if type(self.lrtEntry) == type(''):
                    self.lrtEntry = self.aesmoo.convertString(self.lrtEntry,
                            0, len(self.lrtEntry),
                            self.aesmoo.modeOfOperation[self.operationMode])

        except AttributeError:
            pass # Ignore error.

    ## Change between the all 0s in the s box and just the normal s box.
    def editSBox(self, isZeros):
        print "Changing SBOX =/"
        # If oldSbox wasn't assigned yet, make it the current one (Must be the original)
        if(self.oldSBox == None):
            self.oldSBox = self.aes.sbox
            self.oldRSBox = self.aes.rsbox
        if(isZeros):
            zeros = self.oldSBox
            for x in range (0,len(zeros)):
                zeros[x] = 0
            self.aes.sbox = zeros
            self.aes.rsbox = zeros
        else:
            self.aes.sbox = self.oldSBox
            self.aes.rsbox = self.oldRSBox


    ##This method runs a round like normal using the 4 subroutines.
    # Sub Bytes
    # Shift Rows
    # Mix Columns
    # Run Round Key
    def runRound(self):
        self.runSubBytes()
        self.runShiftRows()
        self.runMixColumns()
        self.runAddRoundKey(self.generateAddRoundKey())
        self.updateMiddleColumn()

    ## Run the round key function on the information.
    def runAddRoundKey(self, expandedKey):
        self.convertStates()

        curRoundKey = self.aes.createRoundKey(expandedKey, self.curRound)

        if self.ptkMode == '2P1K':
            self.aes.state = self.lltEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.addRoundKey(curRoundKey)# todo
            self.aes.state = self.llbEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.addRoundKey(curRoundKey)# todo
        elif self.ptkMode == '1P2K':
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.addRoundKey(curRoundKey)# todo
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.addRoundKey(curRoundKey)# todo

        self.updateMiddleColumn()

        self.addPointInHistory()

    ## Runs the sub bytes on the current values.  Update smiddle column when done.
    def runSubBytes(self):
        self.convertStates()
        if self.ptkMode == '2P1K':
            self.aes.state = self.lltEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.subBytes()
            self.aes.state = self.llbEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.subBytes()
        elif self.ptkMode == '1P2K':
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.subBytes()
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.subBytes()
        self.updateMiddleColumn()
        self.addPointInHistory()

    ## Run shift row subroutine of AES and updates middle column
    def runShiftRows(self):
        self.convertStates()
        if self.ptkMode == '2P1K':
            self.aes.state = self.lltEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.shiftRows()
            self.aes.state = self.llbEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.shiftRows()
        elif self.ptkMode == '1P2K':
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.shiftRows()
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.shiftRows()
        self.updateMiddleColumn()
        self.addPointInHistory()

    ## Run mix column subroutine of AES and updates middle column
    def runMixColumns(self):
        self.convertStates()
        if self.ptkMode == '2P1K':
            self.aes.state = self.lltEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.mixColumns()
            self.aes.state = self.llbEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.mixColumns()
        elif self.ptkMode == '1P2K':
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.lltEntry = self.aes.mixColumns()
            self.aes.state = self.lrtEntry
            self.aes.isInv = False
            self.llbEntry = self.aes.mixColumns()
        self.updateMiddleColumn()
        self.addPointInHistory()

    ## Switches between 2 plain texts, 1 key and 1 plain text, 2 keys.
    def switchKeyPlaintextMode(self, btn):
        top = self.left_lefttop_textfield.label.text
        bottom = self.left_leftbottom_textfield.label.text
        middle = self.left_righttop_textfield.label.text
        if '2 Key' in btn.text:
            btn.text = '2 PTexts 1 Key'
            self.ptkMode = '2P1K'
        else:
            btn.text = '1 PText 2 Keys'
            self.ptkMode = '1P2K'
        self.left_leftbottom_textfield.label.text = ''
        self.left_lefttop_textfield.label.text = middle
        self.left_righttop_textfield.label.text = top
        self.left_leftbottom_textfield.text = top
        self.left_lefttop_textfield.text = middle
        self.left_righttop_textfield.text = top
        self.updateColumns()

    ## Ran when a button is clicked.
    def onButtonClick(self, btn, mbtn):
        if 'SBox' in btn.text:
            if '0s' in btn.text:
                # we're going TO default.
                btn.text = 'SBox Default'
            else:
                # we're going TO all 0s.
                btn.text = 'SBox All 0s'
            self.editSBox('0s' in btn.text)
        elif 'Add' in btn.text:
            self.runAddRoundKey(self.generateAddRoundKey())  #TODO : create expanded key
        elif 'Sub' in btn.text:
            self.runSubBytes()
        elif 'Shift' in btn.text:
            self.runShiftRows()
        elif 'Mix' in btn.text:
            self.runMixColumns()
        elif 'Run Round' in btn.text:
            self.runRound()
        elif 'PText' in btn.text:
            self.switchKeyPlaintextMode(btn)
        elif '<--' in btn.text:
            print 'Backward'
            self.historyBackward()
        elif '-->' in btn.text:
            self.historyForward()
        else:
            print "Don't know what to do"

        # We don't always have to update the middle column. But just so it's easy to read and less bull crap lines,
        # we'll be updating it everytime this method is called.

        self.updateMiddleColumn()
        # WHAT IS THIS DOING?
        self.cleartext = self.cleartext + ' J'
        (self.mode, self.orig_len, self.ciph) = \
            self.moo.encrypt(self.cleartext,
                             self.moo.modeOfOperation[self.operationMode],
                             self.cypherkey, int(self.keySize), self.lrbEntry)

    def generateAddRoundKey(self):
        nbrRounds = 0
        size = 0
        self.convertStates()
        if self.keySize == self.moo.aes.keySize['SIZE_128']:
            nbrRounds = 10
        elif self.keySize == self.moo.aes.keySize['SIZE_192']:
            nbrRounds = 12
        elif self.keySize == self.moo.aes.keySize['SIZE_256']:
            nbrRounds = 14
        expandedKeySize = 16*(nbrRounds+1)
        expandedKey = self.aes.expandKey(self.lrtEntry, self.keySize, expandedKeySize)
        return expandedKey

    ## Updates the view for greyscale and color scale types.
    def updateView(
        self,
        text,
        view,
        size,
        ):
        """
            This method accepts a string, cipher/plain text (text), and updates the view (view) given.
            The size is a tuple (#,#) that is the resulting size.
        """

        if len(text) == 0:
            return

        # surf = pygame.Surface((len(text), 1))

        surf = pygame.Surface((4, 4))
        surf = surf.convert()

        # Alter surf according to the string.

        col = 0
        row = 0
        for pix in text:
            if isinstance(text, str):
                num = ord(pix)
            else:
                num = pix
            if self.visualization == 'Color':
                argb = self.getRGB(num)
            else:
                argb = (num, num, num, num)
            surf.set_at((col, row), Color(argb[1], argb[2], argb[0x3],
                        argb[0]))
            col = col + 1
            if col == 4:
                col = 0
                row = row + 1
        view.image = pygame.transform.scale(surf, (self.columnWidth,
                self.middleBarY - self.buttonBarBottom - MARGIN))

    ## Creates the histogram on the surfaces.
    def histogramOnView(self, text, view):
        nums = []
        for x in range(0, 256):
            nums.append(0)
        for x in text:
            if type(x) == type(0):
                nums[x] = nums[x] + 1
            else:
                nums[ord(x)] = nums[ord(x)] + 1
        height = 0
        for x in range(0, len(nums)):
            if nums[x] > height:
                height = nums[x]
        surf = pygame.Surface((255, height + 1))
        surf = surf.convert()
        for x in range(0, 255):
            for y in range(0, nums[x]):
                surf.set_at((x, y), Color(255, 0, 0))
        view.image = \
            pygame.transform.rotate(pygame.transform.scale(surf,
                                    (self.columnWidth, self.middleBarY
                                    - self.buttonBarBottom - MARGIN)),
                                    180)

    ## Updates the surfaces to show the bit change visualization.
    def bitChangeOnView(
        self,
        first,
        second,
        view,
        isPrint=False,
        ):
        one = []
        for x in range(0, len(first)):
            one.append(0)
        if type(first) == type('string'):
            for x in range(0, len(first)):
                one[x] = ord(first[x])
        else:
            one = first

        two = []
        for x in range(0, len(second)):
            two.append(0)
        if type(second) == type('string'):
            for x in range(0, len(second)):
                two[x] = ord(second[x])
        else:
            two = second
        if isPrint:
            print str(one) + ' ' + str(two)

        # Fluff one or two.

        while len(one) > len(two):
            two.append(0)
        while len(one) < len(two):
            one.append(0)

        # Make our bit strings.

        oneBuff = ''
        for x in range(0, len(one)):
            add = '{0:08b}'.format(one[x])
            oneBuff += add
        twoBuff = ''
        for x in range(0, len(two)):
            add = '{0:08b}'.format(two[x])
            twoBuff += add
        surf = pygame.Surface((len(twoBuff), 1))
        for x in range(0, len(twoBuff)):
            if twoBuff[x] == oneBuff[x]:

                # White, they're the same.

                surf.set_at((x, 0), Color(255, 255, 255))
            else:

                # BLack, they're different.

                surf.set_at((x, 0), Color(0, 0, 0))
        surf = pygame.transform.scale(surf, (self.columnWidth,
                self.middleBarY - self.buttonBarBottom - MARGIN))
        view.image = surf

    ## Updates the middle column.  Figures out which visualization to run, and makes it work.
    def updateMiddleColumn(self):
        top = self.lltEntry
        bottom = self.llbEntry

        if self.visualization == 'Greyscale' or self.visualization \
            == 'Color':
            self.updateView(top, self.topcenter_imageview,
                            (self.columnWidth, self.middleBarY
                            + MARGIN))
            self.updateView(bottom, self.bottomcenter_imageview,
                            (self.columnWidth, self.middleBarY
                            + MARGIN))
        elif self.visualization == 'Histogram':
            self.convertStates()
            self.histogramOnView(top, self.topcenter_imageview)
            self.histogramOnView(bottom, self.bottomcenter_imageview)
        elif self.visualization == 'Punchcard':
            self.punchCardOnView(top, self.topcenter_imageview)
            self.punchCardOnView(bottom, self.bottomcenter_imageview)
        elif self.visualization == 'Bit Compare':
            if self.ptkMode == '2P1K':
                ptOne = self.left_lefttop_textfield.text
                ptTwo = self.left_leftbottom_textfield.text
            else:
                ptOne = self.left_righttop_textfield.text
                ptTwo = self.left_righttop_textfield.text
            self.bitChangeOnView(top, ptOne, self.topcenter_imageview)
            self.bitChangeOnView(bottom, ptTwo,
                                 self.bottomcenter_imageview)

        #self.textfield.text = str(self.kl([1],[1]))
        #self.rightbottom_textfield.text = str(self.kl([1],[1]))

    ## Updates the left column.  Figures out which visualization to run, and makes it work.
    def updateLeftColumn(self):
        """ This should update the left column """

        if self.ptkMode == '2P1K':
            top = self.left_lefttop_textfield.text
            bottom = self.left_leftbottom_textfield.text
        else:
            top = bottom = self.left_righttop_textfield.text

        # Left column doesn't need to be encrypted, we're using the plaintext.

        if self.visualization == 'Greyscale' or self.visualization \
            == 'Color':
            self.updateView(top, self.lefttop_imageview,
                            (self.columnWidth, self.middleBarY
                            + MARGIN))
            self.updateView(bottom, self.leftbottom_imageview,
                            (self.columnWidth, self.middleBarY
                            + MARGIN))
        elif self.visualization == 'Histogram':
            self.histogramOnView(top, self.lefttop_imageview)
            self.histogramOnView(bottom, self.leftbottom_imageview)
            print "Left Historgram"
            print top
            print bottom
        elif self.visualization == 'Punchcard':
            self.bitChangeOnView(top, top, self.lefttop_imageview)
            self.bitChangeOnView(bottom, bottom,
                                 self.leftbottom_imageview)
        elif self.visualization == 'Bit Compare':
            self.bitChangeOnView(top, top, self.lefttop_imageview)
            self.bitChangeOnView(bottom, bottom,
                                 self.leftbottom_imageview)

    ## Updates the right column.  Figures out which visualization to run, and makes it work.
    def updateRightColumn(self):
        """ This should update the right column """

        # Right column needs to be encrypted.

        ptOne = None
        ptTwo = None
        if self.ptkMode == '2P1K':
            (self.mode, self.orig_len, self.ptoEncrypted) = \
                self.moo.encrypt(self.left_lefttop_textfield.text,
                                 self.moo.modeOfOperation[self.operationMode],
                                 self.cypherkey, int(self.keySize),
                                 self.lrbEntry)
            (self.mode, self.orig_len, self.pttEncrypted) = \
                self.moo.encrypt(self.left_leftbottom_textfield.text,
                                 self.moo.modeOfOperation[self.operationMode],
                                 self.cypherkey, int(self.keySize),
                                 self.lrbEntry)
            ptOne = self.left_lefttop_textfield.text
            ptTwo = self.left_leftbottom_textfield.text
        elif self.ptkMode == '1P2K':
            key = []
            for x in range(0, len(self.left_lefttop_textfield.text)):
                key.append(ord(self.left_lefttop_textfield.text[x]))
            (self.mode, self.orig_len, self.ptoEncrypted) = \
                self.moo.encrypt(self.left_righttop_textfield.text,
                                 self.moo.modeOfOperation[self.operationMode],
                                 key, int(self.keySize), self.lrbEntry)
            (self.mode, self.orig_len, self.pttEncrypted) = \
                self.moo.encrypt(self.left_righttop_textfield.text,
                                 self.moo.modeOfOperation[self.operationMode],
                                 key, int(self.keySize), self.lrbEntry)
            ptOne = self.left_righttop_textfield.text
            ptTwo = self.left_righttop_textfield.text
        else:
            print "Poop, this doesn't work =/"

        if self.visualization == 'Greyscale' or self.visualization \
            == 'Color':
            self.updateView(self.ptoEncrypted, self.righttop_imageview,
                            (self.columnWidth, self.middleBarY
                            + MARGIN))
            self.updateView(self.pttEncrypted, self.rightbottom_imageview,
                            (self.columnWidth, self.middleBarY
                            + MARGIN))
        elif self.visualization == 'Histogram':
            print "Right Historgram"
            print self.ptoEncrypted
            print self.pttEncrypted
            self.histogramOnView(self.ptoEncrypted, self.righttop_imageview)
            self.histogramOnView(self.pttEncrypted, self.rightbottom_imageview)
        elif self.visualization == 'Punchcard':
            self.punchCardOnView(self.ptoEncrypted, self.righttop_imageview)
            self.punchCardOnView(self.pttEncrypted, self.rightbottom_imageview)
        elif self.visualization == 'Bit Compare':
            if self.ptkMode == '2P1K':
                ptOne = self.left_lefttop_textfield.text
                ptTwo = self.left_leftbottom_textfield.text
            else:
                ptOne = self.left_righttop_textfield.text
                ptTwo = self.left_righttop_textfield.text

            self.bitChangeOnView(self.ptoEncrypted, ptOne, self.righttop_imageview,
                                 True)
            self.bitChangeOnView(self.pttEncrypted, ptTwo,
                                 self.rightbottom_imageview)
        #print str(self.pttEncrypted) + " " + str(self.ptoEncrypted)
        self.rightbottom_textfield.text = str(self.kl(self.ptoEncrypted, self.pttEncrypted))
        self.righttop_textfield.text = str(self.kl([1],[1]))

    ## Easy way to update all columns.
    def updateColumns(self):
        """ This updates all the columns.  Redraws the left, right, and center. """
        self.convertStates()
        self.cypherkey = self.lrtEntry
        self.updateLeftColumn()
        self.updateMiddleColumn()
        self.updateRightColumn()

    ## Ran when text is changed in any of the input boxes.
    def onTextChanged(self, tf, text):
        """  tf is the TextField object.
            Text is the text the TextField was changed to.
        """

        if tf.placeholder == 'LLT':
            self.lltEntry = text
        elif tf.placeholder == 'LLB':
            self.llbEntry = text
        elif tf.placeholder == 'LRT':
            # Password.
            if(len(text) >= 16):
                # We don't support this, so substring 1-16.
                text = text[0:15]
            self.lrtEntry = text
            tf.text = text
        elif tf.placeholder == 'LRB':
            self.lrbEntry = text
        else:
            print "Don't know what to do..."
            return

        # Clear and add new stuff!
        self.convertStates()
        self.clearHistory()
        self.updateColumns()
        self.addPointInHistory()

    ## Ran when mode of operation is changed.  Updates the operationMode too.
    def moo_changed(
        self,
        selection_view,
        item,
        index,
        ):
        self.operationMode = str(item)
        self.updateColumns()

    ## Ran when round number is changed (Just updates the columns)
    def round_number_changed(
        self,
        selection_view,
        item,
        index,
        ):
        self.curRound = index
        self.updateColumns()

    ## Expanded key size (128/192/256) was changed.
    def expanded_key_size_changed(
        self,
        selection_view,
        item,
        index,
        ):
        if int(item.text) == 128:
            self.keySize = self.moo.aes.keySize['SIZE_128']
        elif int(item.text) == 192:
            self.keySize = self.moo.aes.keySize['SIZE_192']
        elif int(item.text) == 256:
            self.keySize = self.moo.aes.keySize['SIZE_256']
        else:
            self.keySize = self.moo.aes.keySize['SIZE_256']
        self.updateColumns()

    ## Visualizaiton changed, update views.
    def visualization_changed(
        self,
        selection_view,
        item,
        index,
        ):
        self.visualization = str(item)
        self.updateColumns()

    ## Draws the top bar UI elements.
    def drawTopBar(self):
        topButtonNames = [
            'Run Round',
            'Add Round Key',
            'RoundNumber',
            'EKeySize',
            'Sub Bytes',
            'Shift Rows',
            'Mix Columns',
            'MOO',
            ]
        numButtons = len(topButtonNames)
        buttonWidth = self.frame.w / numButtons
        buttonX = buttonWidth + VSMALL_MARGIN
        view = None
        for i in range(0, len(topButtonNames)):
            if topButtonNames[i] == 'RoundNumber':

                # Draw the spinner for modes of operation
                modes = ["1","2","3","4","5","6","7","8","9","10","11","12",
                        "13","14","15","16","17","18","19","20","21","22",
                        "23","24","25","26","27","28","29","30","31","32"]
                labels2 = [ui.Label(
                    ui.Rect(0, 0, buttonWidth - 16, self.label_height),
                    modes[j]) for j in range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(ui.Rect(i * buttonWidth, 0,
                        buttonWidth - 16, self.label_height), labels2)
                view.on_selection_changed.connect(self.round_number_changed)
            elif topButtonNames[i] == 'EKeySize':

                # Draw the spinner for modes of operation

                modes = ['128', '192', '256']
                labels2 = [ui.Label(ui.Rect(0, 0, buttonWidth - 16,
                           self.label_height), modes[j]) for j in
                           range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(ui.Rect(i * buttonWidth, 0,
                        buttonWidth - 16, self.label_height), labels2)
                view.on_selection_changed.connect(self.expanded_key_size_changed)
            elif topButtonNames[i] == 'MOO':

                # Draw the spinner for modes of operation

                modes = ['OFB', 'CFB', 'CBC']
                labels2 = [ui.Label(ui.Rect(0, 0, buttonWidth - 16,
                           self.label_height), modes[j]) for j in
                           range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(ui.Rect(i * buttonWidth, 0,
                        buttonWidth - 16, self.label_height), labels2)
                view.on_selection_changed.connect(self.moo_changed)
            else:
                if view == None:
                    view = ui.Button(ui.Rect(VSMALL_MARGIN, 0,
                            buttonWidth, self.label_height),
                            topButtonNames[i])
                else:
                    view = ui.Button(ui.Rect(i * buttonWidth, 0,
                            buttonWidth, self.label_height),
                            topButtonNames[i])
                view.on_clicked.connect(self.onButtonClick)
            self.add_child(view)

    ## Draws the bottom bar UI elements.
    def drawBottomBar(self):
        bottomButtonNames = [
            '2 PTexts 1 Key',
            'SBox Default',
            '<--',
            '-->',
            '', # This is a spacer button, ignore lolol.
            'Visualization',
            ]
        numButtons = len(bottomButtonNames)
        buttonWidth = self.frame.w / numButtons
        buttonX = buttonWidth + VSMALL_MARGIN
        view = None
        for i in range(0, len(bottomButtonNames)):
            if bottomButtonNames[i] == 'Visualization':

                # Draw the spinner for modes of operation

                modes = [
                    'Greyscale',
                    'Color',
                    'Histogram',
                    'Bit Compare',
                    ]
                labels2 = [ui.Label(ui.Rect(0, 0, LIST_WIDTH,
                           self.label_height), modes[j]) for j in
                           range(len(modes))]
                for l in labels2:
                    l.halign = ui.LEFT
                view = ui.SelectView(ui.Rect(i * buttonWidth,
                        self.frame.h - self.label_height, LIST_WIDTH,
                        self.label_height), labels2, False)
                view.on_selection_changed.connect(self.visualization_changed)
            else:
                if view == None:
                    view = ui.Button(ui.Rect(VSMALL_MARGIN,
                            self.frame.h - self.label_height,
                            buttonWidth, self.label_height),
                            bottomButtonNames[i])
                else:
                    view = ui.Button(ui.Rect(i * buttonWidth,
                            self.frame.h - self.label_height,
                            buttonWidth, self.label_height),
                            bottomButtonNames[i])

                view.on_clicked.connect(self.onButtonClick)
            self.add_child(view)

    ## Draws the lines separaring the bars and the columns for UI elements.
    def drawLinesForGrid(self):
        """
            This draws the grid lines.
            This includes the two lines going top to bottom for each column.
            This also includes the bar below the buttons at the top and the
            middle horizontal line separating the two plain texts, cipher texts
            and current progress.
        """

        # Draw bottom of top button bar.

        slider = ui.SliderView(ui.Rect(0, self.buttonBarBottom - 2,
                               self.frame.w, self.buttonBarBottom + 2),
                               ui.HORIZONTAL, 0, 1, False)
        slider.value = 1
        self.add_child(slider)

        # Draw columns

        for x in range(1, 4):
            slider = ui.SliderView(ui.Rect(self.columnWidth * x,
                                   self.buttonBarBottom, 4,
                                   self.frame.h), ui.VERTICAL, 0, 1,
                                   False)
            slider.value = 1
            self.add_child(slider)

        # Draw center bar.

        slider = ui.SliderView(ui.Rect(0, self.middleBarY
                               + self.label_height / 2, self.frame.w,
                               4), ui.HORIZONTAL, 0, 1, False)
        slider.value = 1
        self.add_child(slider)

    ## A stupid method needed to draw a surface in the columns.
    # This is also what uses the empty.png lol.
    def load_image(
        self,
        file_name,
        colorkey=False,
        image_directory='',
        ):
        file = os.path.join(image_directory, file_name)
        _image = pygame.image.load(file)
        if colorkey:
            if colorkey == -1:

            # If the color key is -1, set it to color of upper left corner

                colorkey = _image.get_at((0, 0))
            _image.set_colorkey(colorkey)
            _image = _image.convert()
        else:

              # If there is no colorkey, preserve the image's alpha per pixel.

            _image = _image.convert_alpha()
        return _image

    ## Draws the left column UI elements.
    def drawLeftColumn(self):
        """
            This draws the left column.
            This column consists of two surfaces showing the initial string,
            along input text boxes for the strings.
        """

        self.lefttop_imageview = ui.ImageView(ui.Rect(0,
                self.buttonBarBottom + MARGIN, self.columnWidth,
                self.middleBarY + MARGIN), self.empty)
        self.add_child(self.lefttop_imageview)

        self.leftbottom_imageview = ui.ImageView(ui.Rect(0,
                self.middleBarY + MARGIN, self.columnWidth,
                self.frame.h), self.empty)
        self.add_child(self.leftbottom_imageview)

        # Draw these text fields at end so they're on top of the pictures.

        self.left_lefttop_textfield = ui.TextField(ui.Rect(0,
                self.middleBarY - 15, self.columnWidth / 2,
                self.label_height), placeholder='LLT')
        self.left_lefttop_textfield.centerx = self.frame.centerx
        self.left_lefttop_textfield.text = self.lltEntry = 'Hello'
        self.left_lefttop_textfield.on_text_change.connect(self.onTextChanged)
        self.add_child(self.left_lefttop_textfield)

        self.left_leftbottom_textfield = ui.TextField(ui.Rect(0,
                self.middleBarY + 15, self.columnWidth / 2,
                self.label_height), placeholder='LLB')
        self.left_leftbottom_textfield.centerx = self.frame.centerx
        self.left_leftbottom_textfield.text = self.llbEntry = 'World'
        self.left_leftbottom_textfield.on_text_change.connect(self.onTextChanged)
        self.add_child(self.left_leftbottom_textfield)

        self.left_righttop_textfield = \
            ui.TextField(ui.Rect(self.left_leftbottom_textfield.frame.right,
                         self.left_lefttop_textfield.frame.top, self.columnWidth / 2,
                         self.label_height), placeholder='LRT')
        self.left_righttop_textfield.centerx = self.frame.centerx
        self.left_righttop_textfield.text = self.lrtEntry = 'Password'
        self.left_righttop_textfield.on_text_change.connect(self.onTextChanged)
        self.left_righttop_textfield.bring_to_front()
        self.add_child(self.left_righttop_textfield)

        self.left_rightbottom_textfield = \
            ui.TextField(ui.Rect(self.left_leftbottom_textfield.frame.right,
                         self.left_leftbottom_textfield.frame.top, self.columnWidth / 2,
                         self.label_height), placeholder='LRB')
        self.left_rightbottom_textfield.centerx = self.frame.centerx
        self.left_rightbottom_textfield.text = self.lrbEntry =  'IV'
        self.left_rightbottom_textfield.on_text_change.connect(self.onTextChanged)
        self.left_rightbottom_textfield.bring_to_front()
        self.add_child(self.left_rightbottom_textfield)


    ## Draws the right column UI elements.
    def drawRightColumn(self):
        """
            This draws the right column.
            This will be the normal result of the plain texts if ran normally
            through AES.
        """

        self.righttop_imageview = \
            ui.ImageView(ui.Rect(self.columnWidth * 2,
                         self.buttonBarBottom + MARGIN,
                         self.columnWidth, self.middleBarY + MARGIN),
                         self.empty)
        self.add_child(self.righttop_imageview)

        self.rightbottom_imageview = \
            ui.ImageView(ui.Rect(self.columnWidth * 2, self.middleBarY
                         + MARGIN, self.columnWidth, self.frame.h),
                         self.empty)
        self.add_child(self.rightbottom_imageview)

        self.righttop_textfield = ui.TextField(ui.Rect(self.columnWidth * 2,
                self.buttonBarBottom + MARGIN, MARGIN * 2,
                MARGIN), placeholder='RTT')
        self.righttop_textfield.centerx = self.frame.centerx
        self.righttop_textfield.text = '100'
        self.add_child(self.righttop_textfield)

        self.rightbottom_textfield = ui.TextField(ui.Rect(self.columnWidth * 2,
                self.middleBarY + MARGIN, MARGIN * 2,
                MARGIN), placeholder='RBT')
        self.rightbottom_textfield.centerx = self.frame.centerx
        self.rightbottom_textfield.text = '100'
        self.add_child(self.rightbottom_textfield)


    ## Draws the center column UI elements.
    def drawCenterColumn(self):
        """
            This draws the center column.
            This will be the current cipher keys and a slider at the bottom
            for history.
        """

        self.topcenter_imageview = \
            ui.ImageView(ui.Rect(self.columnWidth, self.buttonBarBottom
                         + MARGIN, self.columnWidth, self.middleBarY
                         + MARGIN), self.empty)
        self.add_child(self.topcenter_imageview)

        self.bottomcenter_imageview = \
            ui.ImageView(ui.Rect(self.columnWidth, self.middleBarY
                         + MARGIN, self.columnWidth, self.frame.h),
                         self.empty)
        self.add_child(self.bottomcenter_imageview)

    ## Called when we're moving forward in history.
    def historyForward(self):
        if len(self.future) != 0:
            self.printHistory()
            point = self.future.pop()
            self.history.append(point)
            self.lltEntry = point.mt
            self.llbEntry = point.mb
            self.updateMiddleColumn()

    ## Called when we're moving backward in history..
    def historyBackward(self):
        if len(self.history) != 0:
            point = self.history.pop()
            self.future.append(point)
            self.lltEntry = point.mt
            self.llbEntry = point.mb
            self.updateMiddleColumn()

    ## Debug method.
    def printHistory(self):
        for x in range(0, len(self.history)):
            print self.history[x]

    ## Adds a point to our history, resets the future.
    def addPointInHistory(self):
        # Clear anything from the current future.

        self.future = []

        # Add actual point.

        p = HistoryPoint(self.lltEntry[:], self.llbEntry[:])
        self.history.append(p)

    ## Clears all history, or resets the history.
    def clearHistory(self):
        self.history = []

    ## Initializes items, variables, etc..
    def __init__(self):
        ui.Scene.__init__(self)
        self.cleartext = ''
        self.moo = slowaes.AESModeOfOperation()
        self.cleartext = ''
        self.history = []
        self.future = []
        self.originalEntropy = None
        self.statesEntropy = None
        self.cryptsEntropy = None
        self.operationMode = 'CBC'
        self.ptkMode = '2P1K'
        self.keySize = self.moo.aes.keySize['SIZE_128']
        self.visualization = 'Greyscale'
        self.cypherkey = 'Password'
        self.lrbEntry = 'IV'
        self.oldSBox = None #Init it as none, will handle later.
        #self.convertStates()
        (self.mode, self.orig_len, self.ciph) = \
            self.moo.encrypt(self.cleartext,
                             self.moo.modeOfOperation[self.operationMode],
                             self.cypherkey, int(self.keySize), self.lrbEntry)
        self.label_height = ui.theme.current.label_height
        infoObject = pygame.display.Info()
        size = (width, height) = (int(infoObject.current_w),
                                  int(infoObject.current_h))

        frame = ui.Rect(MARGIN, MARGIN, width, height)
        self.buttonBarBottom = self.label_height + VSMALL_MARGIN
        self.columnWidth = self.frame.w / 0x3
        self.middleBarY = (self.frame.h - self.buttonBarBottom) / 2
        self.empty = self.load_image('empty.png')

        self.drawTopBar()
        self.drawBottomBar()

        self.drawRightColumn()
        self.drawCenterColumn()
        self.drawLinesForGrid()
        self.drawLeftColumn()
        self.updateColumns()
        self.addPointInHistory()

    ## Used by the pygameui library.
    def layout(self):
        ui.Scene.layout(self)

    ## Used by the pygameui library.
    def update(self, dt):
        ui.Scene.update(self, dt)
        self.updateColumns()

    ## Helper method to get color values (RGB) from an 8 bit number.  Uses 8 bit colors.
    def getRGB(self, num):
        a = 255
        r = (num >> 5 & 0x7) * 36
        g = (num >> 2 & 0x7) * 36
        b = (num >> 0 & 0x3) * 85
        return (a, r, g, b)


if __name__ == '__main__':
    import pygame
    pygame.init()
    infoObject = pygame.display.Info()

    # Center Screen.
    size = (width, height) = (int(infoObject.current_w / 2),
                              int(infoObject.current_h / 2))
    pos_x = width / 2 - width / 2
    pos_y = height - height
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
    os.environ['SDL_VIDEO_CENTERED'] = '0'

    # Init it and run.

    ui.init('AES Encryption Viewer', size)
    ui.scene.push(MainScene())
    ui.run()
