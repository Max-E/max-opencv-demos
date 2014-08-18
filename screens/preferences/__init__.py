from .include import *
from .ui import *

name = "Preferences"

ui = UI ()

def mainthread_frame (frame):
    
    canvas = util.ui.SizedCanvas (ui.source_display, frame)

def auxthread_frame (frame):
    
    pass

def setup (win):
    
    ui.setup ()

def teardown (win):
    
    ui.teardown ()
