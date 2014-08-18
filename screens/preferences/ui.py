from .include import *

class UI (gtk.VBox):
    
    def __init__ (self):
        
        gtk.VBox.__init__ (self)
        
        self.preferred_w = self.incoming_w = util.input.default_w
        self.preferred_h = self.incoming_h = util.input.default_h
        self.source_display = None
    
    def teardown (self):
        
        self.remove (self.toolbar_hbox)
        self.source_display_teardown ()
    
    def source_display_teardown (self):
        
        self.remove (self.source_display)
        self.set_size_request (0, 0)
    
    def setup (self):
        
        self.trueres_label = gtk.Label ()
        self.res_apply = gtk.Button (stock = gtk.STOCK_APPLY)
        
        self.source_display_setup ()
        
        self.toolbar_hbox = gtk.HBox ()
        
        self.toolbar_hbox.pack_start (gtk.Label ("camera resolution hint: "), expand = False)
        
        width_entry = gtk.Entry ()
        width_entry.connect ("changed", self.preferred_w_changed)
        width_entry.set_text (str (self.preferred_w))
        self.toolbar_hbox.pack_start (width_entry, expand = True)
        
        self.toolbar_hbox.pack_start (gtk.Label (" by "), expand = False)
        
        height_entry = gtk.Entry ()
        height_entry.connect ("changed", self.preferred_h_changed)
        height_entry.set_text (str (self.preferred_h))
        self.toolbar_hbox.pack_start (height_entry, expand = True)
        
        self.res_apply.connect ("clicked", self.resolution_changed)
        self.toolbar_hbox.pack_start (self.res_apply, expand = False)
        
        self.toolbar_hbox.pack_start (self.trueres_label, expand = False)
        
        self.pack_start (self.toolbar_hbox, expand = False)
        
    def source_display_setup (self):
        
        self.res_apply_status ()
        
        self.trueres_label.set_text ("(true resolution %d by %d)" % (util.input.cfg_w, util.input.cfg_h))
        
        self.source_display = util.ui.VideoDisplay (util.input.cfg_w, util.input.cfg_h, "Camera")
        self.pack_end (self.source_display)
        
        self.aspect_ratio = float (util.input.cfg_w) / float (util.input.cfg_h)
        self.set_size_request (int (450 * self.aspect_ratio), 450)
    
    def resolution_changed (self, widget):
        
        self.preferred_w, self.preferred_h = self.incoming_w, self.incoming_h
        
        util.input.set_preferred_resolution (self.preferred_w, self.preferred_h)
        self.source_display_teardown ()
        self.source_display_setup ()
    
    def res_apply_status (self):
        
        self.res_apply.set_sensitive (
            self.incoming_w != None and self.incoming_h != None and
            (self.incoming_w != self.preferred_w or self.incoming_h != self.preferred_h)
        )
    
    def preferred_w_changed (self, widget):
        
        string = widget.get_text ()
        
        if string.isdigit ():
            self.incoming_w = int (string)
        else:
            self.incoming_w = None
        
        self.res_apply_status ()
    
    def preferred_h_changed (self, widget):
        
        string = widget.get_text ()
        
        if string.isdigit ():
            self.incoming_h = int (string)
        else:
            self.incoming_h = None
        
        self.res_apply_status ()
