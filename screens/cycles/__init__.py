from .include import *
from .ui import *
import processing, gameplay

name = "Cycles"

ui = UI ()

gamestate = gameplay.Gamestate ()

def mainthread_frame (frame):
    
    if ui.in_tutorial:
        
        ui.tutorial_frame ()
    
    else:
        
        canvas = util.ui.SizedCanvas (ui.source_display, frame)
        gamestate.drawgame (canvas)

def auxthread_frame (frame):
    
    if not ui.in_tutorial:
        
        frame = processing.process (frame)
        gamestate.add_frame (frame)
        gamestate.visualize (ui)

def setup (win):
    
    gamestate.reset ()
    ui.setup ()

def teardown (win):
    
    ui.teardown ()
