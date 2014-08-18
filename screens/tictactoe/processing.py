from .include import *

class Mark:
    
    def __init__ (self, contour):
        
        self.contour = contour
        
        # Get center of mass
        mu = cv2.moments (contour, False)
        mc = (mu["m10"] / mu["m00"], mu["m01"] / mu["m00"])
        self.origin = mc
        
        # Get bounding box
        br = cv2.boundingRect (contour)
        
        # Determine if it's an X or an O
        self.type = mark_o
        if len (contour) > 3:
            hull = cv2.convexHull (contour, returnPoints = False)
            convexity_defects = cv2.convexityDefects (contour, hull)
            if convexity_defects != None and len (convexity_defects) >= 4:
                self.type = mark_x
        
        # Used for putting in the appropriate cell
        self.horiz_min = br[0]
        self.horiz_width = br[2]
        self.horiz_max = self.horiz_min + self.horiz_width
        self.vert_min = br[1]
        self.vert_height = br[3]
        self.vert_max = self.vert_min + self.vert_height

def process (color_in):
    
    contours = util.processing.getContours (color_in, 6 * util.input.scale_len, 800 * util.input.scale_area)
    
    return [Mark (c) for c in contours]
    
def visualize (ui, gamestate, marks):

    visualization = util.ui.SizedCanvas (ui.visualization_display)
    
    for mark in marks:
        red, blue = 255, 0
        if mark.type is mark_x:
            red, blue = blue, red
        visualization.scaledDrawContour (mark.contour, (red, 0, blue))
    
    gamestate.draw (visualization)
