from util.include import *
import time

default_w, default_h = 1280, 720

# We keep the webcam capture open permanently to keep resolution changes 
# persistant.
camera_cap = cv2.VideoCapture (0)

class Source:
    
    def __init__ (self, src):
        
        self.current_src = None
        self.select_source (src)
        self.lastframe = None
    
    def select_source (self, new_src):
        
        self.repeating = False
        
        if self.current_src != new_src:
            
            self.current_src = new_src
            
            if new_src == 0:
                self.cap = camera_cap
            else:
                self.starttime = time.time ()
                self.cap = cv2.VideoCapture (new_src)
    
    def getframe (self):
        
        if self.repeating:
            return self.lastframe
        
        # Set time position within the video file. The video files are encoded
        # at 15 FPS, we speed it up to the equivalent of 45 FPS for faster
        # playback.
        if self.current_src != 0:
            framenum = int ((time.time () - self.starttime) * 45)
            self.cap.set (cv2.cv.CV_CAP_PROP_POS_FRAMES, framenum)
        
        ret, frame = self.cap.read ()
        
        if not ret and self.current_src != 0:
            self.repeating = True
            return self.lastframe
        
        # Video file playback may require resizing.
        if self.current_src != 0:
            frame = cv2.resize (frame, (cfg_w, cfg_h))
        
        self.lastframe = frame
        return frame

main_source = Source (0)
select_source = main_source.select_source
getframe = main_source.getframe

hint_h = hint_w = cfg_h = cfg_w = scale_len = scale_area = None

# Sets the preferred resolution hint, then sets up all the scaling factors for
# the actual resulting resolution (which may be close but not the same.) NOTE:
# should only be called when the current source is 0 (i.e. the first webcam.)
def set_preferred_resolution (w, h):
    
    global hint_h, hint_w, cfg_h, cfg_w, scale_len, scale_area
    
    hint_h, hint_w = h, w
    
    main_source.cap.set (cv2.cv.CV_CAP_PROP_FRAME_WIDTH, hint_w)
    main_source.cap.set (cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, hint_h)
    
    frame = getframe ()
    
    if frame == None:
        print "NO CAMERA"
        sys.exit (0)
    
    cfg_h, cfg_w, _ = frame.shape
    
    # Even if default_w or default_h changes, DO NOT change these constants!
    scale_len = cfg_h / 960.0
    scale_area = cfg_h * cfg_w / 1280.0 / 960.0

set_preferred_resolution (default_w, default_h)
