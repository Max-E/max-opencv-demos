from .include import *
import math, random

class Gamestate:
    
    def __init__ (self):

        self.left = numpy.array ((-1.0, 0.0))
        self.right = numpy.array ((1.0, 0.0))        
        self.up = numpy.array ((0.0, -1.0))
        self.down = numpy.array ((0.0, 1.0))
        self.vecs = [self.right, self.down, self.left, self.up]
        
        self.margin_w = util.input.cfg_w / 12.0
        self.margin_h = util.input.cfg_h / 12.0
        
        self.ai_path = []
        
        random.seed ()
        
        self.reset ()
    
    def update_scale (self):
        
        self.ai_scale = 32.0 * util.input.scale_len
        
        self.upperleft = numpy.array ((self.margin_w, self.margin_h))
        self.upperright = numpy.array ((util.input.cfg_w - self.margin_w, self.margin_h))
        self.lowerleft = numpy.array ((self.margin_w, util.input.cfg_h - self.margin_h))
        self.lowerright = numpy.array ((util.input.cfg_w - self.margin_w, util.input.cfg_h - self.margin_h))
    
    def reset (self):
        
        self.update_scale ()
        
        self.coherent_image = numpy.zeros ((util.input.cfg_h, util.input.cfg_w), dtype = numpy.uint16)
        self.last_half_perimeter = 0
        
        if len (self.ai_path) != 1:
            rn = random.random ()
            self.ai_path = [numpy.array ((2 * self.margin_w, 2 * self.margin_h + rn * (util.input.cfg_h - 4 * self.margin_h)))]
            self.ai_contour = []
            self.ai_last_vec = None
            self.ai_run_room = self.ai_run_dist = 0.0
        
        self.ai_lose = False
    
    def add_frame (self, frame):
        
        cv2.addWeighted (frame.astype (numpy.uint16), 2, self.coherent_image, 1, -100, self.coherent_image)
        
        if cv2.countNonZero (frame) < 200 * util.input.scale_area:
            self.reset ()
        
        contour_in = numpy.uint8 (numpy.clip (self.coherent_image, 0, 255))
        self.player_contours, self.player_holes = util.processing.getContours (contour_in, 2, 200 * util.input.scale_area, canny = False, rule = cv2.RETR_CCOMP)
        
        half_perimeter = sum ([cv2.arcLength (c, True) for c in self.player_contours]) / 2.0
        
        ai_budget = half_perimeter - self.last_half_perimeter
        if ai_budget > 1.0 and not self.ai_lose:
            self.last_half_perimeter = half_perimeter
        
        self.world_obstacle_segments = [
            util.geometry.PrecomputedLineSegment (self.upperleft, self.upperright),
            util.geometry.PrecomputedLineSegment (self.upperright, self.lowerright),
            util.geometry.PrecomputedLineSegment (self.lowerright, self.lowerleft),
            util.geometry.PrecomputedLineSegment (self.lowerleft, self.upperleft),
        ]
        
        for ci in self.player_contours:
            
            c = ci.astype (float)
            clen = len (c)
            for i in xrange (clen):
                
                self.world_obstacle_segments += [util.geometry.PrecomputedLineSegment (c[i][0], c[(i + 1) % clen][0])]
        
        self.regen_ai_obstacle_segments ()
        
        self.obstacle_segments = self.world_obstacle_segments + self.ai_obstacle_segments
        
        if not self.ai_lose:
            self.ai_decide (ai_budget)
    
    def regen_ai_obstacle_segments (self):
        
        self.ai_obstacle_segments = []
        
        clen = len (self.ai_contour)
        for i in xrange (clen):
           
            self.ai_obstacle_segments += [util.geometry.PrecomputedLineSegment (self.ai_contour[i], self.ai_contour[(i + 1) % clen])]
    
    def closest_intersection (self, a, vec):
        
        dist = util.input.cfg_w + util.input.cfg_h
        b = a + vec * dist
        l1 = util.geometry.PrecomputedLineSegment (a, b)
        
        for l2 in self.obstacle_segments:
            
            res = util.geometry.seg_intersect (l1, l2, calc = True)
            
            if res is not False:
                b = res
                l1 = util.geometry.PrecomputedLineSegment (a, b)
        
        dist = cv2.norm (l1.vec)
        return dist - self.ai_scale
    
    def get_room (self, a, vec):
        
        ret_dist = self.closest_intersection (a, vec)
        
        end = a + ret_dist * vec
        
        vec2 = util.geometry.perpendicular (vec)
        ret1 = self.closest_intersection (end, vec2)
        ret2 = self.closest_intersection (end, -vec2)
        
        if ret1 > ret2:
            room = ret_dist + ret1
        else:
            room = ret_dist + ret2
        
        return ret_dist, room
    
    def recalc_ai_room (self):
        
        vec2 = util.geometry.perpendicular (self.ai_last_vec)
        pt = self.ai_path[-1] + self.ai_run_dist * self.ai_last_vec
        _, projectedroom1 = self.get_room (pt, vec2)
        _, projectedroom2 = self.get_room (pt, -vec2)
        projectedroom = max (0, projectedroom1, projectedroom2)
        self.ai_run_room = self.ai_run_dist + projectedroom
    
    def ai_decide (self, dist_budget):
        
        if self.ai_last_vec is not None:
            
            self.ai_run_dist = self.closest_intersection (self.ai_path[-1], self.ai_last_vec)
            self.recalc_ai_room ()
        
        while dist_budget > sys.float_info.epsilon:
            
            best_room = 0.0
            best_dist = 0.0
            best_vec = None
            
            a = self.ai_path[-1]
            
            for vec in self.vecs:
                
                if self.ai_last_vec is not None and (self.ai_last_vec == -vec).all ():
                    continue
                
                if vec is self.ai_last_vec:
                    dist, room = self.ai_run_dist, self.ai_run_room
                else:
                    dist, room = self.get_room (a, vec)
                
                if dist > 8.0 * util.input.scale_len and \
                   (room > best_room or (room == best_room and dist > best_dist)):
                    best_room, best_dist, best_vec = room, dist, vec
            
            if best_vec is None:
                
                self.ai_lose = True
                return
            
            changedir = self.ai_last_vec is not best_vec
            
            progress = min (dist_budget, best_dist, self.ai_scale / 2)
            
            new_ai_path = a + best_vec * progress
            
            if self.ai_last_vec is None:
                self.ai_last_vec = best_vec
            new_ai_contour_beginning = a + util.geometry.perpendicular (self.ai_last_vec) * self.ai_scale / 4
            new_ai_contour_end = a - util.geometry.perpendicular (self.ai_last_vec) * self.ai_scale / 4
            
            if changedir or len (self.ai_contour) <= 2:
                
                self.ai_path += [new_ai_path]
                if self.ai_last_vec is not best_vec:
                    new_ai_contour_beginning += util.geometry.perpendicular (best_vec) * self.ai_scale / 4
                    new_ai_contour_end -= util.geometry.perpendicular (best_vec) * self.ai_scale / 4
                self.ai_contour = \
                    [new_ai_contour_beginning, new_ai_contour_beginning] + \
                    self.ai_contour + \
                    [new_ai_contour_end, new_ai_contour_end]
                self.regen_ai_obstacle_segments ()
                
                self.ai_last_vec = best_vec
                self.ai_run_dist = best_dist
                self.recalc_ai_room ()
                
            else:
                
                self.ai_path[-1] = new_ai_path
                self.ai_contour[0] = new_ai_contour_beginning
                self.ai_contour[-1] = new_ai_contour_end
                self.ai_obstacle_segments[0] = util.geometry.PrecomputedLineSegment (self.ai_contour[0], self.ai_contour[1])
                self.ai_obstacle_segments[-1] = util.geometry.PrecomputedLineSegment (self.ai_contour[-1], self.ai_contour[0])
                self.ai_obstacle_segments[-2] = util.geometry.PrecomputedLineSegment (self.ai_contour[-2], self.ai_contour[-1])
            
            self.obstacle_segments = self.world_obstacle_segments + self.ai_obstacle_segments
            
            dist_budget -= progress
            self.ai_run_room -= progress
            self.ai_run_dist -= progress
    
    def drawgame (self, canvas):
        
        # Make a new reference to avoid race conditions when drawing gamestate
        # on the main thread while a new game is starting on the aux thread
        ai_path_cp = self.ai_path
        
        for i in xrange (len (ai_path_cp) - 1):
            canvas.scaledLine (ai_path_cp[i], ai_path_cp[i + 1], (255, 0, 0), int (6 * util.input.scale_len * canvas.scale))
        
        canvas.scaledCircle (ai_path_cp[-1], 10 * util.input.scale_len, (255, 0, 0))
        
        canvas.scaledRectangle (self.upperleft, self.lowerright, (0, 0, 255), int (6 * util.input.scale_len))
        
        if self.ai_lose:
            canvas.scaledPutText ("AI Crashed! Erase the board to start a new game.", (self.margin_w / 1.5, self.margin_h / 1.5), 0, 1.5 * util.input.scale_len * canvas.scale, (255, 255, 0), 1, cv2.CV_AA)
    
    def visualize (self, ui):
        
        visualization = util.ui.SizedCanvas (ui.game_display, cv2.cvtColor (numpy.clip (self.coherent_image, 0, 255).astype (numpy.uint8), cv2.COLOR_GRAY2BGR))
        
        self.drawgame (visualization)
