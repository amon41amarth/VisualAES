import pygame
from pygame.locals import *
import math
import numpy
one = [1, 10, 20, 30, 200, 210, 220, 230, 240, 250]
two = [255, 245, 235, 225, 120, 100, 80, 60, 20, 5]

for x in range (0, len(one)):
    one[x] = one[x] * 20
for x in range (0, len(two)):
    two[x] = two[x] * 20
size = (10, 10)
bits = 16
#the number of channels specified here is NOT
#the channels talked about here http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.get_num_channels
pygame.mixer.pre_init(44100, -bits, 2)
pygame.init()
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
#This will keep the sound playing forever, the quit event handling allows the pygame window to close without crashing
_running = True
while _running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _running = False
            break
pygame.quit()
