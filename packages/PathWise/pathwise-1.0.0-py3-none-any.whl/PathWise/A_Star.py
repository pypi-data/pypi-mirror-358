import heapq
from Helper import *

def A_Star(Maze, start, end, costPerStep = 1):
    queue = [(0, 0, start, [start])]
    visited = set()
    nodesExpanded = 1

    while queue:
        heuristic, cost, current, path = heapq.heappop(queue)

        if current == end:
            return path, cost, nodesExpanded
        
        if current not in visited:
            visited.add(current)
            nodesExpanded += 1

            for neighbour in getNeighbours(current, Maze, diagonal=False):
                if neighbour not in visited:
                    newCost = cost + costPerStep
                    newHeuristic = getHeuristic(neighbour, end)
                    heapq.heappush(queue, (newHeuristic + newCost, newCost, neighbour, path + [neighbour]))
    return None, cost, nodesExpanded