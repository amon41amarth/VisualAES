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

def gui():
    moo = slowaes.AESModeOfOperation()
    cleartext = "This is a test!"
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

    pygame.display.set_caption( 'AES Encrypt Simulator!!' )
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
        textImg = font.render( strCIPH, 1, (255,40,0))
    	screen.fill(black)
    	screen.blit(ball, ballrect)
        screen.blit(textImg, (0,0))
    	pygame.display.flip()
        time.sleep(.01)

if __name__ == '__main__':
    gui()