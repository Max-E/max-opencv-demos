from .include import *

class UI (gtk.VBox):
    
    def __init__ (self):
        
        gtk.VBox.__init__ (self)
    
    def teardown (self):
        
        self.remove (self.source_display)
        self.remove (self.visualization_display)
        self.set_size_request (0, 0)
    
    def setup (self):
        
        self.source_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Camera")
        self.add (self.source_display)
        
        self.visualization_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Visualization")
        self.add (self.visualization_display)
        
        full_height = float (util.input.cfg_h * 2)
        
        self.aspect_ratio = util.input.cfg_w / full_height
        self.set_size_request (int (450 * self.aspect_ratio), 450)
