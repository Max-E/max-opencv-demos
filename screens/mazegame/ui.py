from .include import *

class UI (gtk.HBox):
    
    def __init__ (self):
        
        gtk.HBox.__init__ (self)
        
        self.maze_size = 6
    
    def teardown (self):
        
        self.remove (self.left_vbox)
        self.remove (self.right_vbox)
        self.set_size_request (0, 0)
    
    def setup (self):
        
        self.seed = None
        
        self.left_vbox = gtk.VBox ()
        
        self.source_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Camera")
        self.left_vbox.add (self.source_display)
        
        self.visualization_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Visualization")
        self.left_vbox.add (self.visualization_display)
        
        self.add (self.left_vbox)
        
        self.right_vbox = gtk.VBox ()
        
        toolbar_hbox = gtk.HBox ()
        
        toolbar_hbox.pack_start (gtk.Label ("Maze Size:"), expand = False)
        
        self.maze_size_adjustment = gtk.Adjustment (6, 3, 10, 1, 1, 0)
        maze_size_scale = gtk.HScale (self.maze_size_adjustment)
        maze_size_scale.set_digits (0)
        maze_size_scale.set_value_pos (gtk.POS_RIGHT)
        maze_size_scale.set_draw_value (True)
        maze_size_scale.connect ("value-changed", self.maze_size_changed)
        self.maze_size_adjustment.set_value (self.maze_size)
        toolbar_hbox.pack_start (maze_size_scale, expand = True)
        
        refresh_button = gtk.Button (stock = gtk.STOCK_NEW)
        refresh_button.connect ("clicked", self.refresh_clicked)
        self.refresh = True
        toolbar_hbox.pack_start (refresh_button, expand = False)
        
        # Keeping a reference to it seems necessary to work around possible GC
        # bugs
        self.addtut = util.ui.AddTutorialButtons (toolbar_hbox, "mazegame", self.enter_tutorial, self.exit_tutorial, [refresh_button, maze_size_scale])
        
        self.right_vbox.pack_start (toolbar_hbox, expand = False)
        
        self.game_display = util.ui.VideoDisplay (util.input.cfg_h, util.input.cfg_h, "Gameplay")
        self.right_vbox.add (self.game_display)
        
        self.add (self.right_vbox)
        
        full_width = float (util.input.cfg_w + 2 * util.input.cfg_h)
        
        self.left_vbox_proportion = float (util.input.cfg_w) / full_width
        self.right_vbox_proportion = 1.0 - self.left_vbox_proportion
        
        self.aspect_ratio = full_width / (2 * util.input.cfg_h)
        self.set_size_request (750, int (750 / self.aspect_ratio))
        
        self.connect ("size-allocate", self.do_size_allocate)
    
    def maze_size_changed (self, widget):
        
        self.maze_size = int (widget.get_value ())
    
    def refresh_clicked (self, widget):
        
        self.refresh = True
    
    # Idea from http://www.daa.com.au/pipermail/pygtk/2007-March/013532.html
    def do_size_allocate (self, widget, allocation):
        
        allocation_ratio = float (allocation.width) / float (allocation.height)
        
        true_width, true_height = allocation.width, allocation.height
        
        if allocation_ratio > self.aspect_ratio:
            true_width = self.aspect_ratio * true_height
        elif allocation_ratio < self.aspect_ratio:
            true_height = true_width / self.aspect_ratio
        
        excess_width = allocation.width - true_width
        excess_height = allocation.height - true_height
        
        start_x = int (allocation.x + excess_width / 2)
        start_y = int (allocation.y + excess_height / 2)
        
        child_rect = gtk.gdk.Rectangle (start_x, start_y, 0, int (true_height))
        child_rect.width = true_width * self.left_vbox_proportion
        self.left_vbox.size_allocate (child_rect)
        
        child_rect.x += child_rect.width
        child_rect.width = true_width * self.right_vbox_proportion
        self.right_vbox.size_allocate (child_rect)
    
    def enter_tutorial (self):
        
        self.seed = 0
        self.refresh = True
        
        self.old_size = self.maze_size
        self.maze_size_adjustment.set_value (6)
    
    def exit_tutorial (self):
        
        self.seed = None
        self.refresh = True
        
        self.maze_size_adjustment.set_value (self.old_size)
        del self.old_size
