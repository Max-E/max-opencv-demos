from util.include import *
import input
import processing

class VideoDisplay (gtk.AspectFrame):
    
    def __init__ (self, w, h, label = None):
        
        self.virtual_w, self.virtual_h = w, h
        
        gtk.AspectFrame.__init__ (self, label, ratio = float(w) / float(h), obey_child = False)
        
        self.area = gtk.DrawingArea ()
        self.add (self.area)
    
    def current_size (self):
        
        return self.area.allocation.width, self.area.allocation.height
    
    # Draws an RGB OpenCV image into the video display. MUST be the correct size
    # already!
    def draw_from_opencv (self, cvimg):
        
        w, h = self.current_size ()
        
        gtk.threads_enter ()
        try:
            self.area.window.draw_rgb_image (self.area.get_style().black_gc, 0, 0, w, h, gtk.gdk.RGB_DITHER_NONE, cvimg.tostring (), 3 * w)
        except Exception as e:
            print e # Worst case scenario, we just miss a frame
        finally:
            gtk.threads_leave ()
    
    # Draws a BGR OpenCV image into the video display. Need not be the correct
    # size already.
    def draw_from_opencv_scale_bgr (self, cvimg):
        
        SizedCanvas (self, cvimg)

# Instead of drawing directly to a VideoDisplay, you create a SizedCanvas for 
# it. VideoDisplays resize constantly as the GUI window is resized, so
# SizedCanvas partially abstracts that away by presenting a virtual coordinate
# space. Vector rendering is done at the actual display resolution for better
# quality. Actual rendering to the VideoDisplay is deferred until the
# SizedCanvas passes out of scope, so auxilliary threads only have to acquire
# the GTK lock in one place.
class SizedCanvas:
    
    def __init__ (self, display, background = None):
    
        w, h = display.current_size ()
        self.scale = float (w) / display.virtual_w
        
        if background == None:
            self.canvas = numpy.zeros ((h, w, 3), dtype = numpy.uint8)
        else:
            sized = cv2.resize (background, (w, h))
            self.canvas = cv2.cvtColor (sized, cv2.COLOR_BGR2RGB)
        
        self.display = display

    def _do_scale (self, x):
        
        if not isinstance (x, numpy.ndarray):
            x = numpy.array (x)
        
        x = x * self.scale
        
        return x.astype (int)
    
    # As much as I hate making a bunch of methods that behave almost, but not
    # quite like OpenCV APIs, that's the easiest way to hide the scaling.
    
    def scaledDrawContour (self, contour, *args, **kwargs):
        
        cv2.drawContours (self.canvas, [self._do_scale (contour)], -1, *args, **kwargs)
    
    def scaledLine (self, pt1, pt2, *args, **kwargs):
        
        cv2.line (self.canvas, tuple (self._do_scale (pt1)), tuple (self._do_scale (pt2)), *args, **kwargs)
    
    def scaledPutText (self, text, org, *args, **kwargs):
        
        cv2.putText (self.canvas, text, tuple (self._do_scale (org)), *args, **kwargs)
    
    def scaledDot (self, center, *args, **kwargs):
        
        cv2.circle (self.canvas, tuple (self._do_scale (center)), *args, **kwargs)
    
    def scaledCircle (self, center, radius, *args, **kwargs):
        
        cv2.circle (self.canvas, tuple (self._do_scale (center)), int (radius * self.scale), *args, **kwargs)
    
    def scaledRectangle (self, pt1, pt2, *args, **kwargs):
        
        cv2.rectangle (self.canvas, tuple (self._do_scale (pt1)), tuple (self._do_scale (pt2)), *args, **kwargs)
    
    def __del__ (self):
        
        self.display.draw_from_opencv (self.canvas)

# Add attract mode buttons to a toolbar
class AddTutorialButtons:
    
    def __init__ (self, toolbar, tutorial_name = None, enter_callback = None, exit_callback = None, other_controls = []):
        
        self.tutorial_name = tutorial_name
        self.enter_callback, self.exit_callback = enter_callback, exit_callback
        self.other_controls = other_controls
        
        self.help_button = gtk.Button (stock = gtk.STOCK_HELP)
        self.help_button.connect ("clicked", self.enter_tutorial)
        toolbar.pack_start (self.help_button, expand = False)
        
        self.exithelp_button = gtk.Button (stock = gtk.STOCK_OK)
        self.exithelp_button.connect ("clicked", self.exit_tutorial)
        toolbar.pack_start (self.exithelp_button, expand = False)
        self.exithelp_button.set_sensitive (False)
    
    def enter_tutorial (self, widget):
        
        if self.tutorial_name != None:
            input.select_source ("tutorials/%s.avi" % self.tutorial_name)
        
        self.help_button.set_sensitive (False)
        self.exithelp_button.set_sensitive (True)
        
        for control in self.other_controls:
            control.set_sensitive (False)
        
        if self.enter_callback != None:
            self.enter_callback ()
    
    def exit_tutorial (self, widget):
        
        input.select_source (0)
        
        self.help_button.set_sensitive (True)
        self.exithelp_button.set_sensitive (False)
        
        for control in self.other_controls:
            control.set_sensitive (True)
        
        if self.exit_callback != None:
            self.exit_callback ()
