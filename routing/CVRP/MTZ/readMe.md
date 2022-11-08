This folder contains code for solving a capacitated vehicle routing problem over $n$ customers *and* a depot with $m$ vehicles
all having a capacity of $Q$. Each customer $i$ has a demand of $0\leq q_i\leqQ$.
[Pyomo](http://www.pyomo.org/) is used for modelling the problem, and the IP model used is a so-called MTZ-based formulation,
where $x_{ij}$ variables are lifted in the subtour elimination constraints. 

The problem to be solved is given by 

$$
\\begin{align}
  \min        \ & \sum_{i=0}^n \sum_{j=0}^n d_{ij}x_{ij}\\
  \text{s.t.:}\ & \sum_{i=0}^n x_{ij} = 1, & \forall j=1,..,n\\
              \ & \sum_{j=0}^n x_{ij} = 1, & \forall i=1,..,n\\
              \ & \sum_{j=1}^n x_{0j} = m,\\
              \ & \sum_{i=1}^n x{i0} = m,\\
              \ & u_i - u_j + Qx_{ij} + (Q-q_i-q_j)x_{ji} \leq Q-q_j, & \forall i,j=1,..,n\\
              \ & q_i\leq u_i \leq Q, & \forall i=1,..,n\\
              \ & x_{ij}\text{ binary}, & \forall i,j=0,...,n
\\end{align}
$$

The model is implemented in `cvrp_MTZ.py` and it uses functions from `readAndWriteJson.py` in order to read data from a Json-file.
Three data-sets are given, namely `cvrpDataFile_29`, `cvrpDataFile_39`, and `cvrpDataFile_50`. Both `cvrpDataFile_29` and `cvrpDataFile_50` are very difficult to solve using an MTZ-based formulation.

The data is stored in a Json fil using the format
```
"n" : number of customers. Stored as an integer
"m" : number of sales persons leaving and entering the depot
"Q" : the capacity of the vehicles
"q" : list of demands for each node in problem (customers and the depot). q[0] must be equal to zero
"xCord" : horizontal coordinates of the nodes (depot + customers). Stored in a list
"yCord" : vertical coordinates of the nodes (depot + customers). Stored in a list
"dist" : distance matrix where dist[i][j] is the distance between node i and node j. Stored as a list of lists
```

If the data file does not contain a distance matrix `dist` it must contain $x$- and $y$-coordinate called `xCoord` and `yCoord`. It is fine, if the data
file contains both a distance matrix and $x$- and $y$-coordinates.

It is only the `displySolution()`-function that uses the coordinates of the nodes. 
If no coordinates are given, this function will just print the sequence of visits to the prompt.
In case coordinates are supplied, the tour will be displayed in a coordinate system
