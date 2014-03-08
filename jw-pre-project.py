#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      justinwarner
#
# Created:     22/01/2014
# Copyright:   (c) justinwarner 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pygame, slowaes, sys, time, array
from pygame.locals import *
def gui():
	moo = slowaes.AESModeOfOperation()
	cleartext = ""
	cypherkey = [143,194,34,208,145,203,230,143,177,246,97,206,145,92,255,84]
	iv = [103,35,148,239,76,213,47,118,255,222,123,176,106,134,98,92]
	mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"],
			cypherkey, moo.aes.keySize["SIZE_128"], iv)
	pygame.init()

	black = 0, 0, 0
	infoObject = pygame.display.Info()
	size = width, height = int(infoObject.current_w/2), int(infoObject.current_h/2)
	screen = pygame.display.set_mode((width, height))

	pygame.display.set_caption( 'AES Encrypt Mini Project' )
	plainText = "";
	imageSize = (width, int(height/2))
	while True:
		screen.fill(black)
		didChange = False
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				didChange = True
				if event.key == pygame.K_BACKSPACE:
					plainText = plainText[:-1]
				else:
					plainText += event.unicode
			elif event.type == pygame.QUIT:
				sys.exit()
			if didChange:
				mode, orig_len, ciph = moo.encrypt(plainText, moo.modeOfOperation["CBC"], cypherkey, moo.aes.keySize["SIZE_128"], iv)
		
		cipherDraw = pygame.Surface((len(ciph), 1))
		cipherDraw = cipherDraw.convert()
		# Alter cipherDraw
		run = 0
		for pix in ciph:
			cipherDraw.set_at((run, 0), (Color((pix),(pix),(pix),255)))
			run+=1
		for x in range (0, 4):
			cipherDraw = pygame.transform.scale2x(cipherDraw)
		screen.blit(cipherDraw, (0, height/2))
		
		plainDraw = pygame.Surface((len(plainText), 1))
		plainDraw = plainDraw.convert()
		# Alter plainDraw.
		run = 0
		plainText.rjust(len(ciph), '0') # Pad 0's for same length/look.
		for pix in plainText:
			plainDraw.set_at((run, 0), (Color(ord(pix),ord(pix),ord(pix),255)))
			run+=1
		for x in range (0, 4):
			plainDraw = pygame.transform.scale2x(plainDraw)
		screen.blit(plainDraw, (0, 0))
		pygame.display.flip()
		time.sleep(.1)
		
if __name__ == '__main__':
	gui()