#! /usr/bin/env python2.7

import util
from util.include import *
import screens

def delete_event (widget, event, data = None):
    
    gobject.source_remove (timer)
    return False

writer = None
# Uncomment to record a demo for attract mode
# Use Motion JPEG because, although it's not a good codec, it's not heavily
# patent-encumbered, so decoders for it are likely to be available everywhere.
#writer = cv2.VideoWriter ("tmp.avi", cv2.cv.CV_FOURCC ("M", "J", "P", "G"), 15, (1280, 720))

def destroy (widget, data = None):
    
    gtk.main_quit ()

i = 0
thread = None

def frame (): 
    
    win.show_all ()
    
    frame = util.input.getframe ()
    
    if writer is not None:
        writer.write (frame)
    
    current_screen.mainthread_frame (frame)
    
    global thread, i
    
    if thread == None or not thread.is_alive ():
        
        if thread != None:
            thread.join ()
#            print i
#            i = 0
        
        thread = threading.Thread (group = None, target = current_screen.auxthread_frame, args = [frame])
        thread.start ()
    
    i += 1
#    if i == 100:
#        gtk.main_quit ()
    
    return True

win = gtk.Window (gtk.WINDOW_TOPLEVEL)
win.connect ("delete_event", delete_event)
win.connect ("destroy", destroy)
timer = gobject.idle_add (frame)

fullscreen = False

def keypress (widget, event):
    
    global fullscreen
    
    if event.keyval == gtk.keysyms.F11:
        
        if fullscreen:
            fullscreen = False
            win.unfullscreen ()
        else:
            fullscreen = True
            win.fullscreen ()
        
        return True
    
    return False

win.connect ("key_press_event", keypress)

win.set_events (gtk.gdk.KEY_PRESS_MASK)

notebook = gtk.Notebook ()

current_screen = None

def screen_tab_select (notebook, page, page_num):
    
    global current_screen
    
    if current_screen != None:
        current_screen.teardown (win)
    
    util.input.select_source (0)
    
    current_screen = screens.screen_list[page_num]
    current_screen.setup (win)

notebook.connect ("switch-page", screen_tab_select)

for screen in screens.screen_list:
    notebook.append_page (screen.ui, gtk.Label (screen.name))

win.add (notebook)

win.show_all ()

# http://stackoverflow.com/questions/16410852
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

gtk.threads_enter ()
gtk.main ()
gtk.threads_leave ()
