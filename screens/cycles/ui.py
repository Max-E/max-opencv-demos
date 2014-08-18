from .include import *

class UI (gtk.VBox):
    
    def __init__ (self):
        
        gtk.VBox.__init__ (self)
    
    def teardown (self):
        
        if self.in_tutorial:
            self.exit_tutorial ()
        
        self.remove (self.toolbar_hbox)
        self.remove (self.source_display)
        self.remove (self.game_display)
        self.set_size_request (0, 0)
    
    def setup (self):
        
        self.in_tutorial = False
        
        self.toolbar_hbox = gtk.HBox ()
        
        # Keeping a reference to it seems necessary to work around possible GC
        # bugs
        self.addtut = util.ui.AddTutorialButtons (self.toolbar_hbox, None, self.enter_tutorial, self.exit_tutorial)
        
        self.pack_start (self.toolbar_hbox, expand = False)
        
        self.source_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Camera")
        self.add (self.source_display)
        
        self.game_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Gameplay")
        self.add (self.game_display)
        
        full_height = float (util.input.cfg_h * 2)
        
        self.aspect_ratio = util.input.cfg_w / full_height
        self.set_size_request (int (450 * self.aspect_ratio), 450)
    
    # Since the AI outcome is so timing and resolution dependent, we cannot feed
    # in the a video of the player playing a game and expect the gameplay code
    # to reliably come up with the same simulation every time. Instead, tutorial
    # mode takes over both the camera and gameplay viewports and feeds an 
    # independent video stream to both.
    
    def tutorial_frame (self):
        
        camera_frame = self.tutorial_camera_video.getframe ()
        self.source_display.draw_from_opencv_scale_bgr (camera_frame)
        
        game_frame = self.tutorial_game_video.getframe ()
        self.game_display.draw_from_opencv_scale_bgr (game_frame)
    
    def enter_tutorial (self):
        
        self.in_tutorial = True
        
        self.tutorial_camera_video = util.input.Source ("tutorials/cycles_camera.avi")
        self.tutorial_game_video = util.input.Source ("tutorials/cycles_game.avi")
    
    def exit_tutorial (self):
        
        self.in_tutorial = False
        
        del self.tutorial_camera_video
        del self.tutorial_game_video
