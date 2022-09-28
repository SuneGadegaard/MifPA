# Minimum cost covering location problem

Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
Implementation of a minimum cost covering location problem where a set of potential facility
sites $0,1,2,..,n-1$ is given along with a set of customers $0,1,2,..,m-1$.

A cost for opening a facility at site $i$ is given by $f_i$. Furthermore, a binary matrix $(a_ij)$ is given where
$a_{ij} = 1$ if and only if a facility at site $i$ can cover customer $j$. In this particular example, an integer $p$
specifies the number of open facilities allowed in a fasible solution.
Finally, for each customer $j$ an integer $b_j$ specifies how many facilities should be "within reach" for customer $j$
to be fully covered.

The IP solved is given by

$$
\\begin{align}
  \min        \ & \sum_{i=0}^{n-1} f_iy_i\\
  \text{s.t.:}\ & \sum_{i=0}^{n-$} a_{ij}y_i \geq b_j,   &&\forall j=0..m-1\\
              \ & \sum_{i=0}^{n-1}y_i \leq p,\\
              \ & y_i \text{ all binary}
\\end{align}
$$

Here $y_i=1$ means a facility is opened at site $i$.

The readData(...) function uses the `readAndWriteJson.py` file to read data from a Json file in the form
```
  "site_labels": [list of strings with labels for the sites. One for each site must be provided if any]
  "customer_labels": [list of strings with labels for the customers. One for each site must be provided if any]
  "cover_matrix": [list of list. cover_maxtrix[i][j]=1 if and only if facility i can cover customer j. 0 otherwise]
  "fixed_costs": [list of fixed opening costs]
  "b": [list of integers. b[j] specifies the number of facilities needed to cover customer j]
  "p": integer specifying the maximum number of facilities to open in an optimal solution
```
