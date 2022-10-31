This folder contains code for solving a TSP over $n$ customers *and* a depot.
[Pyomo](http://www.pyomo.org/) is used for modelling the problem, and the IP model used is based on an assignment problem with tight
sub-tour elimination constraints. The formulation was proposed in “Solution of a large-scale traveling-salesman problem" by Dantzig, Fulkerson, and 
Johnson in 1954. The $x_{ij}$ are binary variables indicating if the salesman travels directly from node $i$ to node $j$ ( $x_{ij}=1$ ) or not 
( $x_{ij}=0$ )

The IP to be solved is given by 

$$
\\begin{align}
  \min        \ & \sum_{i=0}^n \sum_{j=0}^n d_{ij}x_{ij}\\
  \text{s.t.:}\ & \sum_{i=0}^n x_{ij} = 1,& \forall j=0,..,n\\
              \ & \sum_{j=0}^n x_{ij} = 1,& \forall i=0,..,n\\
              \ & \sum_{i\in S}\sum_{j\in S} x_{ij}\leq \vert S\vert -1,&\forall S\subseteq \text{\{}0,...,n\text{\}}:2\leq \vert S\vert n\\
              \ & x_{ij}\text{ binary},& \forall i,j=0,...,n
\\end{align}
$$

The model is implemented in `TSP_DFJ.py` and it uses functions from `readAndWriteJson.py` in order to read data from a Json-file.
Two data-sets are given, namely `small_tsp_data` and `bigger_tsp_data`.

Since the formulation enumerates *all* the subtour elimination constraints, it is not a viable way to solve TSP of sizes more than $n=10$. 
This is implemented for educational purposes alone!

The data is stored in a Json fil using the format
```
"n" : number of customers. Stored as an integer
"xCord" : horizontal coordinates of the nodes (depot + customers). Stored in a list
"yCord" : vertical coordinates of the nodes (depot + customers). Stored in a list
"dist" : distance matrix where dist[i][j] is the distance between node i and node j. Stored as a list of lists
```

It is only the `displySolution()`-function that uses the coordinates of the nodes. 
If no coordinates are given, this function will just print the sequence of visits to the prompt.
In case coordinates are supplied, the tour will be displayed in a coordinate system
