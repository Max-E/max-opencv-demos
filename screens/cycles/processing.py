from .include import *

def process (color_in):
    
    r = color_in[:,:,2]
    g = color_in[:,:,1]
    green_emphasized = numpy.uint8 (numpy.clip ((255 - r).astype (numpy.uint16) * g.astype (numpy.uint16) / 96, 0, 255))
    
    _, thresh = cv2.threshold (green_emphasized, 190, 255, cv2.THRESH_BINARY)
    thresh = cv2.erode (cv2.dilate (thresh, util.processing.getelement (2)), util.processing.getelement (4))
    
    return thresh
