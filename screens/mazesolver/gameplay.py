from .include import *
import heapq

# A* Search:
# http://en.wikipedia.org/wiki/A*_search_algorithm
# http://www.policyalmanac.org/games/aStarTutorial.htm

class Waypoint:
    
    def __init__ (self, gamestate, pt):
        
        self.gamestate = gamestate
        self.origin = pt.astype (float)
        self.parent = None
        self.g_cost = None
        self.f_cost = None
        self.h_cost = cv2.norm (pt - gamestate.goal)
        self.can_see_goal = gamestate.check_visibility (pt, gamestate.goal)
        self.dists = {}
    
    def finalize (self):
        
        for other in self.gamestate.waypoints:
            if other not in self.dists:
                if self.gamestate.check_visibility (self.origin, other.origin):
                    dist = cv2.norm (self.origin - other.origin)
                else:
                    dist = -1.0
                self.dists.update ({other: dist})
                other.dists.update ({self: dist})
    
    # So we can send the final waypoints over multiprocessing queues without
    # dragging the whole gamestate along with it.
    def unlink (self):
        
        self.dists = None
        self.gamestate = None
    
    def __le__ (self, other):
        
        return self.f_cost <= other.f_cost

class Gamestate:
    
    def __init__ (self, waypoints_raw, segments):
        
        self.segments = [util.geometry.PrecomputedLineSegment (pt1, pt2) for pt1, pt2 in segments]
        self.segments.sort (key = util.geometry.seg_getxmin)
        self.upperleft = numpy.array ((maze_margin, maze_margin))
        self.lowerright = numpy.array ((util.input.cfg_w - maze_margin, util.input.cfg_h - maze_margin))
        self.start = numpy.array ((2.0 * maze_margin, 2.0 * maze_margin))
        self.goal = numpy.array ((util.input.cfg_w - 2.0 * maze_margin, util.input.cfg_h - 2.0 * maze_margin))
        
        self.trivial_solution = self.check_visibility (self.start, self.goal)
        if self.trivial_solution:
            return
        
        self.waypoints = set ([Waypoint (self, pt) for pt in waypoints_raw])
        
        self.open = []
        
        self.solution = None
        
        for waypoint in self.waypoints:
            
            waypoint.finalize ()
            
            if not self.check_visibility (self.start, waypoint.origin):
                continue
            
            heapq.heappush (self.open, waypoint)
            waypoint.g_cost = cv2.norm (waypoint.origin, self.start)
            waypoint.f_cost = waypoint.g_cost + waypoint.h_cost
            
            if waypoint.can_see_goal:
                self.solution = waypoint
        
        self.solution = None
        self.solvable = None
        while self.solvable == None:
            self.solvable = self.iterate ()
        
        for waypoint in self.waypoints:
            waypoint.unlink ()
    
    def iterate (self):
        
        if not len (self.open):
            return False
        
        self.solution = heapq.heappop (self.open)
        self.waypoints.remove (self.solution)
        
        if self.solution.can_see_goal:
            return True
        
        for waypoint in self.waypoints:
            
            if self.solution.dists[waypoint] == -1.0:
                continue
            
            new_g = self.solution.g_cost + self.solution.dists[waypoint]
            
            if waypoint in self.open and new_g >= waypoint.g_cost:
                continue
            
            waypoint.g_cost = new_g
            waypoint.f_cost = waypoint.g_cost + waypoint.h_cost
            waypoint.parent = self.solution
            
            if waypoint.can_see_goal:
                self.solution = waypoint
                return True
            
            if waypoint not in self.open:
                # At this point, the heap invariant may be violated, so who
                # knows how much better this is than just appending it
                heapq.heappush (self.open, waypoint)
        
        heapq.heapify (self.open)
    
    def check_visibility (self, pt1, pt2):
        
        s1 = util.geometry.PrecomputedLineSegment (pt1, pt2)
        
        minseg = 0
        maxseg = len (self.segments) - 1
        
        for s2 in self.segments[minseg:]:
            if s2.mins[0] > s1.maxs[0]:
                return True
            if util.geometry.seg_intersect (s1, s2):
                return False
        
        return True
    
    def draw_hud (self, canvas):
        
        canvas.scaledDot (self.start, 6, (0, 255, 0), cv2.cv.CV_FILLED, cv2.CV_AA)
        canvas.scaledDot (self.goal, 6, (255, 0, 0), cv2.cv.CV_FILLED, cv2.CV_AA)
        
        canvas.scaledRectangle (self.upperleft, self.lowerright, (255, 0, 0), 2, cv2.CV_AA)
    
    def draw (self, canvas):
        
        self.draw_hud (canvas)
        
        if self.trivial_solution:
            
            canvas.scaledLine (self.start, self.goal, (0, 255, 0), 2, cv2.CV_AA)
            canvas.scaledPutText ("Draw some obstacles!", (maze_margin, maze_margin), 0, 1.5 * util.input.scale_len * canvas.scale, (255, 255, 0), 1, cv2.CV_AA)
        
        elif self.solution != None:
            
            waypoint = self.solution
            
            if self.solvable:
                canvas.scaledLine (self.goal, waypoint.origin, (0, 255, 0), 2, cv2.CV_AA)
            
            while waypoint.parent != None:
                canvas.scaledLine (waypoint.origin, waypoint.parent.origin, (0, 255, 0), 2, cv2.CV_AA)
                waypoint = waypoint.parent
            
            canvas.scaledLine (self.start, waypoint.origin, (0, 255, 0), 2, cv2.CV_AA)
