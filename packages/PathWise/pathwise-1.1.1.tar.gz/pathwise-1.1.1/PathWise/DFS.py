from .Helper import *

def DFS(Maze, start, end, diagonal = False):
    stack = [(start, [start])]
    visited = set()
    nodesExpanded = 1

    while stack:
        current, path = stack.pop()

        if current == end:
            return path, nodesExpanded
        
        if current not in visited:
            visited.add(current)
            nodesExpanded += 1

            for neighbour in getNeighbours(current, Maze, diagonal):
                if neighbour not in visited:
                    stack.append((neighbour, path + [neighbour]))
    return None, nodesExpanded