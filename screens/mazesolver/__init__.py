from .include import *
from .ui import *
import processing, gameplay

name = "Maze Solver"

ui = UI ()

gamestate = None

def mainthread_frame (frame):
    
    canvas = util.ui.SizedCanvas (ui.source_display, frame)
    if gamestate != None:
        gamestate.draw (canvas)

def auxthread_frame (frame):
    
    global gamestate
    
    waypoints, segments = processing.process (frame)
    gamestate = gameplay.Gamestate (waypoints, segments)
    processing.visualize (ui, gamestate, waypoints, segments)

def setup (win):
    
    ui.setup ()

def teardown (win):
    
    ui.teardown ()
