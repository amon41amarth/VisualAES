#-------------------------------------------------------------------------------
# Name:        evan.py
# Purpose:     play around w/ Pygame and AES
#
# Author:      Evan Williams
#
# Created:     02/01/2014
# Copyright:   (c) Evan Williams 2014
# Licence:     Public Domain
#-------------------------------------------------------------------------------

import pygame, slowaes, sys, time, array

def gui():
    moo = slowaes.AESModeOfOperation()
    cleartext = raw_input("Enter a String to encrypt:")
    cypherkey = [143,194,34,208,145,203,230,143,177,246,97,206,145,92,255,84]
    iv = [103,35,148,239,76,213,47,118,255,222,123,176,106,134,98,92]
    mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"],
    		cypherkey, moo.aes.keySize["SIZE_128"], iv)
    print 'm=%s, ol=%s (%s), ciph=%s' % (mode, orig_len, len(cleartext), ciph)
    decr = moo.decrypt(ciph, orig_len, mode, cypherkey,
    		moo.aes.keySize["SIZE_128"], iv)
    print decr

    pygame.init()

    size = width, height = 320, 240
    speed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    pygame.display.set_caption( 'AES Encrypt Simulator w/ User Input!!' )
    ball = pygame.image.load("ball.bmp")
    ballrect = ball.get_rect()

    while True:
    	for event in pygame.event.get():
    		if event.type == pygame.QUIT: sys.exit()

    	ballrect = ballrect.move(speed)
    	if ballrect.left < 0 or ballrect.right > width:
    		speed[0] = -speed[0]
    	if ballrect.top < 0 or ballrect.bottom > height:
    		speed[1] = -speed[1]
        font = pygame.font.Font(None, 30)
        strCIPH = "".join( chr( val ) for val in ciph )
        textImg = font.render( "Ciphertext: " + strCIPH, 1, (255,40,0))
        clearImg = font.render( "Cleartext: " + cleartext, 1, (0,255,40))
    	screen.fill(black)
    	screen.blit(ball, ballrect)
        screen.blit(textImg, (0,0))
        screen.blit(clearImg, (0,20))
    	pygame.display.flip()
        time.sleep(.01)

if __name__ == '__main__':
    gui()