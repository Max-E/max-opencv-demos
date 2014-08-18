from .include import *
import random

# The maze generation is an implementation of the unmodified randomized Prim's
# algorithm from http://en.wikipedia.org/wiki/Maze_generation_algorithm

class Maze:
    
    def __init__ (self, w, h, seed = None):
        
        self.w, self.h = w, h 
        self.area = w * h
        
        self.scale_w = float (util.input.cfg_h) / (self.w + 2.0)
        self.scale_h = float (util.input.cfg_h) / (self.h + 2.0)
        
        self.wall_list = []
        
        self.visited = set ()
        self.passages = set ()
        
        random.seed (seed)
        self.randstate = random.getstate ()
        
        self.generate ()
    
    def wall_num_between_cells (self, cell1_num, cell2_num):
        
        if cell2_num < cell1_num:
            # cell 2 is either East or North of cell 1
            return self.wall_num_between_cells (cell2_num, cell1_num)
        
        ret = 2 * cell1_num
        if cell2_num == cell1_num + 1 and cell2_num % self.w != 0:
            return ret # cell 2 is cell 1's neighbor to the West
        elif cell2_num == cell1_num + self.w:
            return ret + 1 # cell 2 is cell 1's neighbor to the South
        
        assert False
    
    def add_wall (self, wall_num):
        
        if wall_num not in self.wall_list:
            assert wall_num not in self.passages
            self.wall_list += [wall_num]
    
    def add_wall_between_cells (self, cell1_num, cell2_num, from_wall):
        
        wall_num = self.wall_num_between_cells (cell1_num, cell2_num)
        
        if wall_num != from_wall:
            self.add_wall (wall_num)
    
    def visit_cell (self, cell_num, from_wall):
        
        self.visited.add (cell_num)
        
        if cell_num % self.w:
            self.add_wall_between_cells (cell_num, cell_num - 1, from_wall)
        if (cell_num + 1) % self.w:
            self.add_wall_between_cells (cell_num, cell_num + 1, from_wall)
        if cell_num >= self.w:
            self.add_wall_between_cells (cell_num, cell_num - self.w, from_wall)
        if cell_num + self.w < self.area:
            self.add_wall_between_cells (cell_num, cell_num + self.w, from_wall)
    
    def handle_wall (self, wall_list_num):
        
        wall_num = self.wall_list [wall_list_num]
        
        cell1_num = wall_num / 2
        
        if wall_num % 2:
            cell2_num = cell1_num + self.w
        else:
            cell2_num = cell1_num + 1
        
        cell1_visited = cell1_num in self.visited
        cell2_visited = cell2_num in self.visited
        
        if cell2_visited:
            cell1_visited, cell2_visited = cell2_visited, cell1_visited
            cell1_num, cell2_num = cell2_num, cell1_num
        
        assert cell1_visited # neither visited
        
        if cell2_visited:
            # both visited, make a passage between them
            last_wall_num = self.wall_list.pop ()
            if wall_list_num != len (self.wall_list):
                self.wall_list[wall_list_num] = last_wall_num
        else:
            # one visited, time to visit the other one
            self.passages.add (wall_num)
            self.visit_cell (cell2_num, wall_num)
    
    def repeatable_randrange (self, stop):
        
        random.setstate (self.randstate)
        ret = random.randrange (stop)
        self.randstate = random.getstate ()
        
        return ret
    
    def generate (self):
        
        self.visit_cell (self.repeatable_randrange (self.area), -1)
        
        while len (self.wall_list):
            self.handle_wall (self.repeatable_randrange (len (self.wall_list)))
        
        self.generate_lines ()
    
    def vertline (self, x, y1, y2):
            
        x, y1, y2 = (x + 1) * self.scale_w, (y1 + 1) * self.scale_h, (y2 + 1) * self.scale_h
        return numpy.array (((x, y1), (x, y2)))
        
    def horizline (self, y, x1, x2):
        
        y, x1, x2 = (y + 1) * self.scale_h, (x1 + 1) * self.scale_w, (x2 + 1) * self.scale_w
        return numpy.array (((x1, y), (x2, y)))
    
    def line_between_cells (self, cell1_num, cell2_num):
        
        if cell2_num < cell1_num:
            return self.line_between_cells (cell2_num, cell1_num)
        
        row = cell1_num // self.w
        col = cell1_num % self.w
        
        if cell1_num + 1 == cell2_num:
            return self.horizline (row + 0.5, col + 0.5, col + 1.5)
        
        assert cell1_num + self.w == cell2_num
        return self.vertline (col + 0.5, row + 0.5, row + 1.5)
    
    def generate_lines (self):

        def lines_for_cell (cell_num):
            
            row = cell_num // self.w
            col = cell_num % self.w
            
            if row < self.h - 1 and 2 * cell_num + 1 not in self.passages:
                yield self.horizline (row + 1, col, col + 1)
            if 2 * cell_num not in self.passages:
                yield self.vertline (col + 1, row, row + 1)
        
        self.maze_lines = [
            self.horizline (0, 1, self.w), # upper border
            self.vertline (0, 0, self.h), # left border
            self.horizline (self.h, 0, self.w - 1), # lower border
            
            # Draw a small square indicating the goal point
            self.horizline (self.h - 0.75, self.w - 0.75, self.w - 0.25),
            self.horizline (self.h - 0.25, self.w - 0.75, self.w - 0.25),
            self.vertline (self.w - 0.75, self.h - 0.75, self.h - 0.25),
            self.vertline (self.w - 0.25, self.h - 0.75, self.h - 0.25),
        ]
        
        for cell_num in xrange (self.area):
            for line in lines_for_cell (cell_num):
                self.maze_lines += [line]
    
    # Check whether the maze is solved by the directions given
    def trace (self, arrows):
        
        self.trace_lines = [
            # Draw a small square indicating the start point
            self.horizline (0.25, 0.25, 0.75),
            self.horizline (0.75, 0.25, 0.75),
            self.vertline (0.25, 0.25, 0.75),
            self.vertline (0.75, 0.25, 0.75)
        ]
        
        lastcell = 0
        
        for arrow in arrows:
            
            if arrow.dir is arrow_left and lastcell % self.w:
                nextcell = lastcell - 1
            elif arrow.dir is arrow_right and (lastcell + 1) % self.w:
                nextcell = lastcell + 1
            elif arrow.dir is arrow_up and lastcell >= self.w:
                nextcell = lastcell - self.w
            elif arrow.dir is arrow_down and lastcell + self.w < self.area:
                nextcell = lastcell + self.w
            else:
                continue
            
            if self.wall_num_between_cells (lastcell, nextcell) in self.passages:
                self.trace_lines += [self.line_between_cells (lastcell, nextcell)]
                lastcell = nextcell
        
        self.solved = lastcell + 1 == self.area
    
    def visualize (self, ui):
        
        visualization = util.ui.SizedCanvas (ui.game_display)
        
        for line in self.maze_lines:
            visualization.scaledLine (line[0], line[1], (0, 255, 0), 2, cv2.CV_AA)
        
        for line in self.trace_lines:
            visualization.scaledLine (line[0], line[1], (255, 0, 0), 2, cv2.CV_AA)
        
        if self.solved:
            visualization.scaledPutText ("MAZE SOLVED (\"New\" button to generate another)", numpy.array ((self.scale_w, self.scale_h * 0.5)), 0, util.input.scale_len * visualization.scale, (255, 255, 0))
