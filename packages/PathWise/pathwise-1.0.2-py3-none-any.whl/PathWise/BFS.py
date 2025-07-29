from collections import deque
from .Helper import *

def BFS(Maze, start, end):
    queue = deque([(start, [start])])
    visited = set()
    nodesExpanded = 1

    while queue:
        current, path = queue.popleft()

        if current == end:
            return path, nodesExpanded
        
        if current not in visited:
            visited.add(current)
            nodesExpanded += 1

            for neighbour in getNeighbours(current, Maze, diagonal=False):
                if neighbour not in visited:
                    queue.append((neighbour, path + [neighbour]))
    
    return None, nodesExpanded