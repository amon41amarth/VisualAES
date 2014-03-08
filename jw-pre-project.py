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

import pygame, slowaes, sys, time, array, collections
import math
import numpy
from pygame.locals import *
def getBitChanges(one, two, w, h):
	# Fluff one or two.
	while(len(one) > len(two)):
		two.append(0)
	while(len(one) < len(two)):
		one.append(0)
	# Make our bit strings.
	oneBuff = ""
	for x in range (0, len(one)):
		add = "{0:08b}".format(one[x])
		oneBuff += add
	twoBuff = ""
	for x in range (0, len(two)):
		add = "{0:08b}".format(two[x])
		twoBuff += add
	surf = pygame.Surface((len(twoBuff), 1))
	for x in range (0, len(twoBuff)):
		if(twoBuff[x] == oneBuff[x]):
			# White, they're the same.
			surf.set_at((x, 0), (Color((255),(255),(255))))
		else:
			# BLack, they're different.
			surf.set_at((x, 0), (Color((0),(0),(0))))
	surf = pygame.transform.scale(surf, (w, h))
	return surf

def getPunchCard(text, w, h):
	one = []
	for x in range (0, len(text)):
		one.append(0)
	if(type(text) == type("string")):
		for x in range (0, len(text)):
			one[x] = ord(text[x])
	else:
		one = text

	cnt = collections.Counter()
	for x in one:
		cnt[x] += 1
	size = cnt.most_common(1)[0][1]
	surf = pygame.Surface((size*16, size*16))
	surf.fill((255,255,255))
	for x in range (0, 256):
		pygame.draw.circle(surf, (0, 0, 0), (x % 16 * size,size* int(x/16)), cnt[x])

	surf = pygame.transform.scale(surf, (w, h))
	return surf

def getSounds(one, two):
	# Fluff one or two.
	while(len(one) > len(two)):
		two.append(0)
	while(len(one) < len(two)):
		one.append(0)
	for x in range (0, len(one)):
	    one[x] = one[x] * 20
	for x in range (0, len(two)):
	    two[x] = two[x] * 20
	size = (10, 10)
	bits = 16
	#the number of channels specified here is NOT
	#the channels talked about here http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.get_num_channels
	pygame.mixer.pre_init(44100, -bits, 2)
	_display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)
	#this sounds totally different coming out of a laptop versus coming out of headphones
	sample_rate = 44100
	n_samples = int(round(len(one)*sample_rate))
	#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
	buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
	max_sample = 2**(bits - 1) - 1
	run = 0
	for x in range(n_samples):
	    thing = one[run]
	    run = int(round(x / sample_rate))
	    t = float(x)/sample_rate    # time in seconds
	    #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
	    buf[x][0] = int(round(max_sample*math.sin(2*math.pi*one[run]*t)))       # left
	    buf[x][1] = int(round(max_sample*0.5*math.sin(2*math.pi*two[run]*t)))   # right
	sound = pygame.sndarray.make_sound(buf)
	#play once, then loop forever
	sound.play(loops = -1)

def gui():
	moo = slowaes.AESModeOfOperation()
	cleartext = ""
	cypherkey = [143,194,34,208,145,203,230,143,177,246,97,206,145,92,255,84]
	iv = [103,35,148,239,76,213,47,118,255,222,123,176,106,134,98,92]
	mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"],
			cypherkey, moo.aes.keySize["SIZE_128"], iv)
	pygame.init()

	grey = 200, 200, 200
	infoObject = pygame.display.Info()
	size = width, height = int(infoObject.current_w/2), int(infoObject.current_h/2)
	screen = pygame.display.set_mode((width, height))

	pygame.display.set_caption( 'AES Encrypt Mini Project' )
	plainText = "";
	screen.fill(grey)
	screen.blit(getPunchCard("Hellllllo", width, height), (0, 0))
	#screen.blit(getBitChanges([255, 255, 1, 30, 99, 120, 120, 120, 120], [90, 90, 90, 200, 20, 20, 200, 210, 32, 98, 100], width, height), (0, 0))
	#getSounds([255, 255, 1, 30, 99, 120, 120, 120, 120], [90, 90, 90, 200, 20, 20, 200, 210, 32, 98, 100])
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
		pygame.display.flip()
		time.sleep(.1)

if __name__ == '__main__':
	gui()
	#getBitChanges(500,500)
