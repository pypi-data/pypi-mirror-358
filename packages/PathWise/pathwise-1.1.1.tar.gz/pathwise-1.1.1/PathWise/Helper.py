import numpy as np

def getNeighbours(current, Maze, diagonal = False):
    neighbours = []
    cx, cy = current
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] 
    
    newMaze = np.array(Maze).astype(str)

    if diagonal:
        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for dx, dy in directions:
        x, y = cx + dx, cy + dy

        if 0 <= x < len(newMaze) and 0 <= y < len(newMaze[0]) and newMaze[x][y] != '1':
            neighbours.append((x, y))
    return neighbours

def getHeuristic(current, end):
    return abs(current[0] - end[0]) + abs(current[1] - end[1])