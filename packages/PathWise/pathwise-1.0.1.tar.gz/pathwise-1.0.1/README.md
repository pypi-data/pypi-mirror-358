# PathFinder

PathFinder is a Python package that provides classic pathfinding algorithms such as:

- Breadth-First Search (BFS)

- Depth-First Search (DFS)

- Uniform Cost Search (UCS)

- A-Star Search (A*)

These algorithms work on 2D mazes represented as grids, and are designed to help with visualization, teaching, or solving pathfinding problems programmatically.

## 💾 Installation
```bash
pip install PathWise
```

## 📝 Features

- Supports 2D grid mazes with customizable start, goal, and wall positions

- Clear API to run any algorithm and get the path, cost, and visited nodes

- Easily extendable for diagonal movement or custom cost functions

- Suitable for AI projects, teaching, and maze-solving

## ⚖️ Algorithms Included

### BFS

- Explores nodes level by level

- Guarantees shortest path if all moves have equal cost

### DFS

- Explores deep into one branch before backtracking

- May not find the shortest path

### UCS

- Uses a priority queue (cost-based)

- Always finds the lowest-cost path

### A*

- Uses cost + heuristic (e.g. Manhattan distance)

- Highly efficient for large or complex mazes

## 💡 Usage

### 1. Representing the Maze

A maze is a 2D list of characters:

maze = [
  ["S", " ", " ", "#", "G"],
  ["#", "#", " ", "#", " "],
  [" ", " ", " ", " ", " "],
  [" ", "#", "#", "#", " "],
  [" ", " ", " ", " ", " "]
]

S = Start

G = Goal

\# = Wall (Represented by 1)

' '  = Open path (Represented by 0)

### 2. Running an Algorithm
```python
from pathfinder import Pathfinder

solver = Pathfinder(maze)
path, visited = solver.bfs()  # or dfs(), ucs(), astar()

print("Path:", path)
print("Visited:", visited)
```
## 📁 Project Structure
```
pathfinder/
├── algorithms/
│   ├── bfs.py
│   ├── dfs.py
│   ├── ucs.py
│   ├── __init__.py
    └── astar.py
```
## 📃 License

This project is licensed under the MIT License.

## Author
Developed by Mahdi Jaffery