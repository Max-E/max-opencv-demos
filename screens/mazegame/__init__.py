from .include import *
from .ui import *
import processing, gameplay

name = "Maze Generator"

ui = UI ()

n_arrows = 0

def mainthread_frame (frame):
    
    canvas = util.ui.SizedCanvas (ui.source_display, frame)
    
    if n_arrows == 0:
        canvas.scaledPutText ("Draw some arrows!", numpy.array ((util.input.cfg_w, util.input.cfg_h)) / 12, 0, 2.5 * util.input.scale_len * canvas.scale, (255, 255, 0))

maze = None

def auxthread_frame (frame):
    
    global maze, n_arrows
    
    if maze == None or maze.w != ui.maze_size or ui.refresh:
        ui.refresh = False
        maze = gameplay.Maze (ui.maze_size, ui.maze_size, ui.seed)
    
    arrows = processing.process (frame)
    n_arrows = len (arrows)
    maze.trace (arrows)
    processing.visualize (ui, arrows)
    maze.visualize (ui)

def setup (win):
    
    ui.setup ()

def teardown (win):
    
    ui.teardown ()
