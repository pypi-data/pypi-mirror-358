import numpy as np
from .A_Star import A_Star
from .BFS import BFS
from .DFS import DFS
from .UCS import UCS

class PathWise:
    def __init__(self, Maze):
        self.Maze = Maze
        pass

    def DFS(self, start, end, diagonal = False):
        return DFS(self.Maze, start, end, diagonal)

    def BFS(self, start, end, diagonal = False):
        return BFS(self.Maze, start, end, diagonal)

    def UCS(self, start, end, costPerStep = 1, diagonal = False):
        return UCS(self.Maze, start, end, costPerStep, diagonal)

    def A_Star(self, start, end, costPerStep = 1, diagonal = False):
        return A_Star(self.Maze, start, end, costPerStep, diagonal)
    
    def printMaze(self):
        newMaze = [row[:] for row in self.Maze]
        
        newMaze = np.array(newMaze).astype(str)

        for i in range(len(newMaze)):
            for j in range(len(newMaze[i])):
                if newMaze[i][j] == '0' or newMaze[i][j].lower() == 'g' or newMaze[i][j].lower() == 's':
                    newMaze[i][j] = ' '
                elif newMaze[i][j] == '1':
                    newMaze[i][j] = '#'
                else:
                    newMaze[i][j] = 'X'

        print(np.array(newMaze))
        print(np.array(self.Maze))

    pass
PathWise = PathWise
__all__ = ['PathWise']