from .include import *
from .ui import *
import processing, gameplay

name = "Tic Tac Toe"

ui = UI ()

gamestate = None

def mainthread_frame (frame):
    
    canvas = util.ui.SizedCanvas (ui.source_display, frame)
    if gamestate != None:
        gamestate.draw (canvas)

def auxthread_frame (frame):
    
    global gamestate
    
    marks = processing.process (frame)
    gamestate = gameplay.Gamestate (marks)
    processing.visualize (ui, gamestate, marks)

def setup (win):
    
    ui.setup ()

def teardown (win):
    
    ui.teardown ()
