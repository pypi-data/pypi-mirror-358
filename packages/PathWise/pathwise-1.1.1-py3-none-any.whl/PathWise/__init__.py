from .A_Star import A_Star
from .BFS import BFS
from .DFS import DFS
from .UCS import UCS

class PathWise:
    def __init__(self):
        pass

    def DFS(self, Maze, start, end, diagonal = False):
        return DFS(Maze, start, end, diagonal)

    def BFS(self, Maze, start, end, diagonal = False):
        return BFS(Maze, start, end, diagonal)
    
    def UCS(self, Maze, start, end, costPerStep = 1, diagonal = False):
        return UCS(Maze, start, end, costPerStep, diagonal)
    
    def A_Star(self, Maze, start, end, costPerStep = 1, diagonal = False):
        return A_Star(Maze, start, end, costPerStep, diagonal)
    
    pass
PathWise = PathWise
__all__ = ['PathWise']