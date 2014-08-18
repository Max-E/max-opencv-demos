from .include import *

arrow_scale = 15.0 * util.input.scale_len

class Arrow:
    
    def __init__ (self, origin, dir):
    
        self.origin = numpy.array (origin)
        self.dir = dir
        
        # Used for drawing
        self.axis, self.ortho_axis = numpy.array ([0, 0]), numpy.array ([0, 0])
        if self.dir is arrow_up or self.dir is arrow_down:
            self.axis[1] = self.ortho_axis[0] = self.dir[0]
        else:
            self.axis[0] = self.ortho_axis[1] = self.dir[0]
    
    def draw (self, canvas, color):
        
        def DRAWPT (x, y):
            return self.origin + arrow_scale * (x * self.axis + y * self.ortho_axis)
        
        arrow_start = DRAWPT (-1, 0)
        arrow_tip = DRAWPT (1, 0)
        arrow_left = DRAWPT (0.5, 0.5)
        arrow_right = DRAWPT (0.5, -0.5)
        
        canvas.scaledLine (arrow_start, arrow_tip, color, 2, cv2.CV_AA)
        canvas.scaledLine (arrow_tip, arrow_right, color, 2, cv2.CV_AA)
        canvas.scaledLine (arrow_tip, arrow_left, color, 2, cv2.CV_AA)
        canvas.scaledLine (arrow_right, arrow_left, color, 2, cv2.CV_AA)

class ArrowFromContour (Arrow):
    
    def __init__ (self, contour):
        
        self.contour = contour
        
        contour_len = len (contour)
        
        # Determine the arrow's axis (vertical or horizontal)
        vertweight, horizweight = 0.0, 0.0
        
        for j in xrange (contour_len):
            diff = (contour[(j + 1) % contour_len] - contour[j])[0]
            weight = cv2.norm (diff)
            
            if abs (diff[0]) > abs (diff[1]):
                horizweight += weight
            else:
                vertweight += weight
        
        vert = vertweight > horizweight
        
        # Get center of mass
        mu = cv2.moments (contour, False)
        mc = (mu["m10"] / mu["m00"], mu["m01"] / mu["m00"])
        
        # Get center of bounding box
        br = cv2.boundingRect (contour)
        bc = (br[0] + br[2] * 0.5, br[1] + br[3] * 0.5)
        
        # determine the arrow's direction (left/right, up/down)
        if vert:
            if mc[1] > bc[1]:
                dir = arrow_down
            else:
                dir = arrow_up
        else:
            if mc[0] > bc[0]:
                dir = arrow_right
            else:
                dir = arrow_left
        
        # Used for sorting
        self.vert_min = br[1]
        self.vert_height = br[3]
        self.vert_max = self.vert_min + self.vert_height
        
        Arrow.__init__ (self, mc, dir)
        
    # For sorting arrows right to left, top to bottom.
    def __cmp__ (self, other):
        
        if self.vert_max - 0.15 * self.vert_height < other.vert_min:
            return -1
        
        if self.vert_min > self.vert_max - 0.15 * self.vert_height:
            return 1
        
        return cmp (self.origin[0], other.origin[0])

def process (color_in):
    
    contours = util.processing.getContours (color_in, 2, 800 * util.input.scale_area, 25600 * util.input.scale_area)
    
    arrows = [ArrowFromContour (c) for c in contours]
    arrows.sort (cmp = ArrowFromContour.__cmp__)
    
    return arrows
    
def visualize (ui, arrows):
    
    cursor = [arrow_scale, arrow_scale]
    n = 0
    
    visualization = util.ui.SizedCanvas (ui.visualization_display)
    for arrow in arrows:
        axis = arrow.axis.tolist ()
        
        # Draw an outline of the shape, color-coded by what type of arrow we
        # think it is.
        color = (abs (axis[0]) * 255, (axis[0] + axis[1]) * 255, abs (axis[1]) * 255)
        visualization.scaledDrawContour (arrow.contour, color)
        
        # Draw what type of arrow we think the shape is over the shape itself
        arrow.draw (visualization, (255, 255, 255))
        
        # Draw a number representing which arrow this is over the shape. These 
        # numbers should match the intended sequence/order of the arrows as
        # drawn.
        visualization.scaledPutText (str (n), arrow.origin, 0, 0.8, (0, 255, 0))
        n += 1
        
        # We also draw all the arrows in a "paragraph" at the top of the screen
        # so you can read them in order. This sequence of arrows should match
        # the intended sequence/order of the arrows as drawn.
        Arrow (cursor, arrow.dir).draw (visualization, (0, 255, 0))
        
        cursor[0] += (2.0 + abs (axis[0])) * arrow_scale
        if cursor[0] >= util.input.cfg_w:
            cursor[1] += 2.5 * arrow_scale
            cursor[0] = arrow_scale
