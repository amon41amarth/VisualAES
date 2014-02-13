import pygame

import view


class FlipbookView(view.View):
    """Flipbook-style image animation view.

    Displays animation frames stored in equally sized rectangles of
    a single "sprite sheet" image file.

    Only works with sheets with N columns in a single row.

    """

    def __init__(self, frame, image, delay=1/10.0):
        """Create a flipbook view.

        frame.topleft

            where to position the view.

        frame.size

            size of each sub-image.

        image

            the spritesheet image.

        """
        view.View.__init__(self, frame)
        self.image = image
        self.frame_count = self.image.get_size()[0] // frame.size[0]
        self.current_frame = 0
        self.delay = delay
        self.elapsed = 0

    def update(self, dt):
        view.View.update(self, dt)
        self.elapsed += dt
        if self.elapsed > self.delay:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.elapsed = 0

    def draw(self):
        if not view.View.draw(self):
            return False

        rect = pygame.Rect((self.current_frame * self.frame.size[0], 0),
                           self.frame.size)

        self.surface.blit(self.image, (0, 0), rect)
        return True
