from .include import *

def process (color_in):
    
    contours = util.processing.getContours (color_in, 10 * util.input.scale_len, 50 * util.input.scale_area)
    
    segments = [
        (c[i][0], c[(i + 1) % len (c)][0]) for c in contours for i in xrange (len (c))
    ]
    
    waypoints = []
    
    def add_waypoint (pt, waypoints = waypoints):
        
        pt = tuple (pt)
        
        if pt[0] < maze_margin or pt[1] < maze_margin:
            return
        
        if pt[0] > util.input.cfg_w - maze_margin or pt[1] > util.input.cfg_h - maze_margin:
            return
        
        for contour in contours:
            dist = cv2.pointPolygonTest (contour, pt, True)
            if dist >= -1.333 * util.input.scale_len:
                return
        
        waypoints += [numpy.array (pt)]
    
    for c in contours:
        
        clen = len (c)
        
        for i in xrange (clen):
            
            pt1, pt2, pt3 = c[i][0], c[(i + 1) % clen][0], c[(i + 2) % clen][0]
            
            vec1 = (pt2 - pt1).astype (float)
            vec1 /= math.sqrt (numpy.dot (vec1, vec1))
            vec2 = (pt2 - pt3).astype (float)
            vec2 /= math.sqrt (numpy.dot (vec2, vec2))
            
            vecavg = (vec1 + vec2) / 2.0
            
            add_waypoint (pt2.astype (float) + 8.0 * util.input.scale_area * vecavg)
            
    return waypoints, segments
    
def visualize (ui, gamestate, waypoints, segments):

    visualization = util.ui.SizedCanvas (ui.visualization_display)
    for pt1, pt2 in segments:
        visualization.scaledLine (pt1, pt2, (255, 0, 0), 1, cv2.CV_AA)
    
    for pt in waypoints:
        visualization.scaledDot (pt, 3, (0, 255, 0), 2, cv2.CV_AA)
    
    gamestate.draw (visualization)
