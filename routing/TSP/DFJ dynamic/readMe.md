This folder contains code for solving a TSP over $n$ customers *and* a depot.
[Pyomo](http://www.pyomo.org/) is used for modelling the problem, and the IP model used is based on an assignment problem with tight
sub-tour elimination constraints. The formulation was proposed in “Solution of a large-scale traveling-salesman problem" by Dantzig, Fulkerson, and 
Johnson in 1954. The $x_{ij}$ are binary variables indicating if the salesman travels directly from node $i$ to node $j$ ( $x_{ij}=1$ ) or not 
( $x_{ij}=0$ ). In this formulation, we let $V=$ { $0,...,n$ }.

The IP to be solved is given by 

$$
\\begin{align}
  \min        \ & \sum_{i\in V} \sum_{j\in V} d_{ij}x_{ij}\\
  \text{s.t.:}\ & \sum_{i\in V:i\neq j} x_{ij} = 1,                       && \forall j=0,..,n\\
              \ & \sum_{j\in V:i\neq j} x_{ij} = 1,                       && \forall i=0,..,n\\
              \ & \sum_{i\in S}\sum_{j\in S} x_{ij}\leq \vert S\vert -1,  &&\forall S\subseteq V:2\leq \vert S\vert \leq n\\
              \ & x_{ij}\text{ binary},                                   && \forall i,j\in V
\\end{align}
$$

Given that there is an exponential number of subtour elimination constriants (SECs) of the form $\sum_{i\in S}\sum_{j\in S} x_{ij} \leq \vert S\vert - 1$ 
these constraints are separated dynamically in this implementation. The algorithm used is similar to a combinatorial benders' approach, where the master
IP is given by the assignment polytope plus any separated SECs. When then IP is solved, the resulting solution is inspected to check if it contains any
disconnected sub tours. If this is the case, the SECs removing the subtours are added, and the IP is resolved to optimality.

The model is implemented in `TSP_DFJ_dynamic.py` and it uses functions from `readAndWriteJson.py` in order to read data from a Json-file.
Two data-sets are given, namely `small_tsp_data` and `bigger_tsp_data`.

Since the approach is thought to be independent on the solver used, the implementation does not use any callbacks. Therefore, the IPs are solved to 
optimality before separating cuts. A better way to implement this would be to embed the separation procedure in the branch and bound process and separate
cuts at every node in the branchin tree (could be achieved by utilizing solver callbacks).

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
