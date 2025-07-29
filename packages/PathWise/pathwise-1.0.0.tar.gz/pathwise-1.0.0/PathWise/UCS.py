import heapq
from Helper import *

def UCS(Maze, start, end, costPerStep = 1):
    queue = [(0, start, [start])]
    visited = set()
    nodesExpanded = 1

    while queue:
        cost, current, path = heapq.heappop(queue)

        if current == end:
            return path, cost, nodesExpanded
        
        if current not in visited:
            visited.add(current)
            nodesExpanded += 1

            for neighbour in getNeighbours(current, Maze, diagonal=False):
                if neighbour not in visited:
                    new_cost = cost + costPerStep
                    heapq.heappush(queue, (new_cost, neighbour, path + [neighbour]))
    return None, cost, nodesExpanded