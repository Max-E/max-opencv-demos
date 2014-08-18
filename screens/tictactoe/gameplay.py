from .include import *
import math

class Gamestate:
    
    def __init__ (self, marks):
        
        self.grid_margin_w = util.input.cfg_w / 6.0
        self.grid_margin_h = util.input.cfg_h / 6.0
        self.cell_w = util.input.cfg_w * 2.0 / 9.0
        self.cell_h = util.input.cfg_h * 2.0 / 9.0
        
        self.grid = [[mark_none for i in xrange (3)] for j in xrange (3)]
        
        for mark in marks:
            
            cell_x = int (math.floor ((mark.origin[0] - self.grid_margin_w) / self.cell_w))
            cell_y = int (math.floor ((mark.origin[1] - self.grid_margin_h) / self.cell_h))
            
            if cell_x < 0 or cell_x >= 3 or cell_y < 0 or cell_y >= 3:
                continue
            
            self.grid [cell_y][cell_x] = mark.type
        
        self.winner = self.detect_victory ()
    
    def detect_victory (self):
        
        def SEQ (starty, stepy, startx, stepx):
            
            return  self.grid[starty][startx] is not mark_none and \
                    self.grid[starty][startx] is self.grid[starty + stepy][startx + stepx] and \
                    self.grid[starty][startx] is self.grid[starty + 2 * stepy][startx + 2 * stepx]
        
        for i in xrange (3):
            if SEQ (i, 0, 0, 1): return self.grid[i][0]
            if SEQ (0, 1, i, 0): return self.grid[0][i]
        
        if SEQ (0, 1, 0, 1): return self.grid[0][0]
        if SEQ (0, 1, 2, -1): return self.grid[0][2]
        
        return mark_none
    
    def draw_hud (self, canvas):
        
        for i in xrange (4):
            
            x = i * self.cell_w + self.grid_margin_w
            y = i * self.cell_h + self.grid_margin_h
            canvas.scaledLine ((x, self.grid_margin_h), (x, util.input.cfg_h - self.grid_margin_h), (0, 255, 0))
            canvas.scaledLine ((self.grid_margin_w, y), (util.input.cfg_w - self.grid_margin_w, y), (0, 255, 0))
    
    def draw (self, canvas):
        
        self.draw_hud (canvas)
        
        for cell_y in xrange (3):
            for cell_x in xrange (3):
                
                x = self.grid_margin_w + cell_x * self.cell_w
                y = self.grid_margin_h + cell_y * self.cell_h
                
                if self.grid[cell_y][cell_x] is mark_x:
                    canvas.scaledLine ((x, y), (x + self.cell_w, y + self.cell_h), (255, 255, 0), 3, cv2.CV_AA)
                    canvas.scaledLine ((x + self.cell_w, y), (x, y + self.cell_h), (255, 255, 0), 3, cv2.CV_AA)
                elif self.grid[cell_y][cell_x] is mark_o:
                    radius = min (self.cell_w, self.cell_h) / 2.0
                    canvas.scaledCircle ((x + 0.5 * self.cell_w, y + 0.5 * self.cell_h), radius, (255, 255, 0), 3, cv2.CV_AA)
        
        if self.winner is mark_x:
            canvas.scaledPutText ("X Wins", (self.grid_margin_w / 2.0, self.grid_margin_h / 2.0), 0, 2.0 * canvas.scale, (255, 255, 0), 1, cv2.CV_AA)
        elif self.winner is mark_o:
            canvas.scaledPutText ("O Wins", (self.grid_margin_w / 2.0, self.grid_margin_h / 2.0), 0, 2.0 * canvas.scale, (255, 255, 0), 1, cv2.CV_AA)
