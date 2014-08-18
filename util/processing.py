from util.include import *
import input
import itertools

def getelement (sz):
    
    return cv2.getStructuringElement (cv2.MORPH_ELLIPSE, (2*sz + 1, 2*sz + 1), (sz, sz))

def getContours (color_in, approx = 2, minArea = None, maxArea = None, canny = True, rule = cv2.RETR_EXTERNAL):
    
    if len (color_in.shape) == 2:
        gray_in = color_in
    else:
        gray_in = cv2.cvtColor (color_in, cv2.COLOR_BGR2GRAY)
    if canny:
        canny_out = cv2.Canny (gray_in, 30, 60, 3)
        canny_out = cv2.dilate (canny_out, getelement (3))
    else:
        canny_out = gray_in
    contours_unfiltered, hierarchy_unfiltered = cv2.findContours (canny_out, rule, cv2.CHAIN_APPROX_SIMPLE);
    
    if hierarchy_unfiltered == None:
        hierarchy_unfiltered = [[]]
    
    contours = []
    hierarchy = []
    for i, j in itertools.izip (contours_unfiltered, hierarchy_unfiltered[0]):
        tmp_contour = cv2.approxPolyDP (i, approx, True)
        
        area = cv2.contourArea (tmp_contour)
        
        if (minArea != None and area < minArea) or (maxArea != None and area > maxArea):
            continue
        
        contours += [tmp_contour]
        hierarchy += [j]
    
    if rule == cv2.RETR_CCOMP:
        
        holes = False
        
        if hierarchy != None:
            
            for h in hierarchy:
                
                if h[3] != -1:
                    holes = True
                    break
        
        return numpy.array (contours), holes
    
    return numpy.array (contours)


