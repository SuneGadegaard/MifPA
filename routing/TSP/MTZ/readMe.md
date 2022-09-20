This folder contains code for solving a TSP over $n$ customers *and* a depot.
[Pyomo](http://www.pyomo.org/) is used for modelling the problem, and the IP model used is a so-called MTZ formulation,
where $x_{ij}$ variables are lifted in the subtour elimination constraints

The problem to be solved is given by 
```
min   sum ( i in 0..n ) sum( j in 0..n) dist[i][j]*x[i][j]
 s.t.  sum ( i in 0..n ) x[i][j] == 1, for all j=0,..,n
       sum ( j in 0..n ) x[i][j] == 1, for all i=0,..,n
       u[i] - u[j] + n*x[i][j] + (n-2)*x[j][i] <= n-1, for all i,j=1,..,n
       1 <= u[i] <= n, for all i=1,..,n
       x[i][j] are all binary
```

The model is implemented in `TSPmodelMTZ.py` and it uses functions from `readAndWriteJson.py` in order to read data from a Json-file.
Two data-sets are given, namely `small_tsp_data` and `bigger_tsp_data`.

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
