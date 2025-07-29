import numpy as np
from .A_Star import A_Star
from .BFS import BFS
from .DFS import DFS
from .UCS import UCS

class PathWise:
    def __init__(self):
        self.Maze = None
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
                    if newMaze[i][j] == '0':
                        newMaze[i][j] = ' '
                elif newMaze[i][j] == '1':
                    newMaze[i][j] = '#'
                else:
                    newMaze[i][j] = 'X'

        print(np.array(newMaze))
        pass

    def generateMaze(self, maxRows, maxCols, density = 0.3):
        self.Maze = np.random.choice(['0', '1'], size=(maxRows, maxCols), p=[1 - density, density])
        start = (np.random.randint(0, maxRows), np.random.randint(0, maxCols))
        end = (np.random.randint(0, maxRows), np.random.randint(0, maxCols))
        self.Maze[start] = 'S'
        self.Maze[end] = 'G'

        self.start = start
        self.end = end

        return self.Maze

    def setMaze(self, maze):
        self.Maze = maze
        if not np.issubdtype(self.Maze.dtype, np.integer):
            self.Maze = np.array(self.Maze)
        start = None
        end = None
        maze_arr = np.array(self.Maze)
        for i in range(maze_arr.shape[0]):
            for j in range(maze_arr.shape[1]):
                if maze_arr[i, j] == 'S':
                    start = (i, j)
                elif maze_arr[i, j] == 'G':
                    end = (i, j)
        self.start = start
        self.end = end
        return self.Maze

    pass
PathWise = PathWise
__all__ = ['PathWise']