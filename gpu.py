from pygame import Color, display, draw, Rect, RESIZABLE
SCALE_FACTOR = 4
DISP_WIDTH = 64
DISP_HEIGHT = 32

COLORS = {
    0: Color(0,0,0,255),
    1: Color(250, 250, 250, 255)
}

class chip8_gpu(object):

    def __init__(self, height=DISP_HEIGHT, width=DISP_WIDTH):
        self.height = height
        self.width = width
        self.surface = None
        self.screen_state = [[0 for i in range(DISP_WIDTH)] for j in range(DISP_WIDTH)]

    def init_display(self):
        display.init()
        display.set_caption("Chip-8 Interpreter")
        self.surface = display.set_mode((DISP_WIDTH*SCALE_FACTOR, DISP_HEIGHT*SCALE_FACTOR), RESIZABLE, 8)
        self.surface.fill(COLORS[0])
        self.clear()
        self.update()

    def flip_pixel(self, x_pos, y_pos):
        self.screen_state[x_pos][y_pos] = not self.screen_state[x_pos][y_pos]
        if self.screen_state[x_pos][y_pos] == 0:
            return 1
        return 0

    def get_pixel(self, x_pos, y_pos):
        return self.screen_state[x_pos][y_pos]

    def set_pixel(self, x_pos, y_pos, state):
        self.screen_state[x_pos][y_pos] = state

    def display_byte(self, x_pos, y_pos, byte):
        return_val = 0
        for i in range(8):
            if byte[i] == 1:
                return_val += self.flip_pixel(x_pos+i, y_pos)
        return return_val > 0



    def clear(self):
        for row in self.screen_state:
            for pixel in self.screen_state:
                pixel = 0
        self.update()
    
    def update(self):
        for x in range(DISP_HEIGHT):
            for y in range(DISP_WIDTH):
                draw.rect(self.surface, COLORS[self.screen_state[x][y]], Rect(x*SCALE_FACTOR, y*SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR))
        display.flip()

