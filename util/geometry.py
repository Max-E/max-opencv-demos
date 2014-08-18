from util.include import *
import ctypes

# Cross (a, b) = Dot (a, perpendicular (b)) = -Dot (perpendicular (a), b)
def perpendicular (vec):
    ret = numpy.empty_like (vec)
    ret[0] = -vec[1]
    ret[1] = vec[0]
    return ret

# Used by seg_intersect to speed things up
class PrecomputedLineSegment (list):
    
    def __init__ (self, pt1, pt2):
        
        list.__init__ (self)
        
        self.append (pt1)
        self.append (pt2)
        self.vec = pt2 - pt1
        self.pvec = perpendicular (self.vec)
        
        self.mins = numpy.empty_like (self.vec)
        self.maxs = numpy.empty_like (self.vec)
        for i in xrange (2):
            if pt1[i] < pt2[i]:
                self.mins[i], self.maxs[i] = pt1[i], pt2[i]
            else:
                self.maxs[i], self.mins[i] = pt1[i], pt2[i]

def seg_getxmin (seg):
    
    return seg.mins[0]

# Flagrantly ripped off from iMalc on stack overflow:
# http://stackoverflow.com/a/14795484
def seg_intersect (l1, l2, calc = False):
    
    if      l1.maxs[0] < l2.mins[0] or l1.mins[0] > l2.maxs[0] or \
            l1.maxs[1] < l2.mins[1] or l1.mins[1] > l2.maxs[1]:
        return False
    
    pvec3 = numpy.empty_like (l1.vec)
    pvec3[0] = l2[0][1] - l1[0][1]
    pvec3[1] = l1[0][0] - l2[0][0]
    
    cross = -numpy.dot (l1.pvec, l2.vec)
    
    if abs (cross) < sys.float_info.epsilon:
        return False
    
    s = numpy.dot (pvec3, l1.vec) / cross
    t = numpy.dot (pvec3, l2.vec) / cross
    
    if s < 0.0 or t < 0.0 or s > 1.0 or t > 1.0:
        return False
    
    if calc:
        return l1[0] + t * l1.vec
    
    return True
