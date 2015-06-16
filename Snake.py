from Tkinter import *
import random, pylsl
from pylsl import stream_inlet, stream_outlet, stream_info
info = stream_info('RandomData', 'EEG', 4, 50, pylsl.cf_int32, 'RandomDev123')
outlet = stream_outlet(info)
inlet = stream_inlet(info)
inlet.open_stream()

WIDTH = 800
HEIGHT = 600
SEG_SIZE = 20
IN_GAME = True


def create_block():
    global BLOCK
    posx = SEG_SIZE * random.randint(1, (WIDTH-SEG_SIZE) / SEG_SIZE)
    posy = SEG_SIZE * random.randint(1, (HEIGHT-SEG_SIZE) / SEG_SIZE)
    BLOCK = c.create_oval(posx, posy, posx+SEG_SIZE, posy+SEG_SIZE, fill="red")

    
def main():
    global IN_GAME
    if IN_GAME:
        s.move()
        head_coords = c.coords(s.segments[-1].instance)
        x1, y1, x2, y2 = head_coords
        insample = pylsl.vectorf()
        inlet_list = []
        while inlet.samples_available():
            inlet.pull_sample(insample)
            inlet_list.append(list(insample))
        for i in range(len(inlet_list)):
            s.change_direction(inlet_list[i])
        if x2 > WIDTH or x1 < 0 or y1 < 0 or y2 > HEIGHT:
            IN_GAME = False
        elif head_coords == c.coords(BLOCK):
            s.add_segment()
            c.delete(BLOCK)
            create_block()
        else:
            for index in range(len(s.segments)-1):
                 if head_coords == c.coords(s.segments[index].instance):
                    IN_GAME = False
        root.after(100, main)
    else:
        c.create_text(WIDTH/2, HEIGHT/2, text="GAME OVER!", font="Arial 20", fill="red")

        
class Segment(object):
    def __init__(self, x, y):
        self.instance = c.create_rectangle(x, y, x+SEG_SIZE, y+SEG_SIZE, fill="white")
        
class Snake(object):
    def __init__(self, segments):
        self.segments = segments
        self.mapping = {"Down": (0, 1), "Right": (1, 0), "Up": (0, -1), "Left": (-1, 0)}
        self.vector = self.mapping["Right"]
        
    def move(self):
        for index in range(len(self.segments)-1):
            segment = self.segments[index].instance
            x1, y1, x2, y2 = c.coords(self.segments[index+1].instance)
            c.coords(segment, x1, y1, x2, y2)
            
        x1, y1, x2, y2 = c.coords(self.segments[-2].instance)
        c.coords(self.segments[-1].instance,
                x1+self.vector[0]*SEG_SIZE, y1+self.vector[1]*SEG_SIZE,
                x2+self.vector[0]*SEG_SIZE, y2+self.vector[1]*SEG_SIZE)
        
    def add_segment(self):
        last_seg = c.coords(self.segments[0].instance)
        x = last_seg[2] - SEG_SIZE
        y = last_seg[3] - SEG_SIZE
        self.segments.insert(0, Segment(x, y))
        
    def change_direction(inlet_list, self):
        if (inlet_list[0] > 0) or (inlet_list[1] > 0):
            self.vector = self.mapping["Up"]
        elif (inlet_list[0] < 0) or (inlet_list[1] < 0):
            self.vector = self.mapping["Down"]
        elif (inlet_list[2] > 0) or (inlet_list[3] > 0):
            self.vector = self.mapping["Right"]
        elif (inlet_list[2] < 0) or (inlet_list[3] < 0):
            self.vector = self.mapping["Left"]

root = Tk()
root.title("PythonicWay Snake")

c = Canvas(root, width=WIDTH, height=HEIGHT, bg="#003300")
c.grid()
c.focus_set()
segments = [Segment(SEG_SIZE, SEG_SIZE), Segment(SEG_SIZE*2, SEG_SIZE), Segment(SEG_SIZE*3, SEG_SIZE)]
s = Snake(segments)

create_block()
main()
root.mainloop()


