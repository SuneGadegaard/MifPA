Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
Implementation of an uncapacitated facility location problem where a set of potential facility
sites $\{0,1,2,..,n-1{}$ is given along with a set of customers $\{0,1,2,..,m-1\}$.
A cost for servicing customer $j$ from facility site $i$ is given by $c_{ij}$ and a cost for opening a facility at site $i$
is given by $f_i$.

The IP solved is given by
```
  min   sum ( i in 0..n-1 ) sum( i in 0..m-1 ) c[i][j]*x[i][j] + sum ( i in 0..n-1 ) f[i]*y[i]
  s.t.  sum ( i in 0..n-1 ) x[i][j] == 1,   for all j=0..m-1
        x[i][j] <= y[i],                    for all i in 0..n-1 and all j in 0..m-1
        x[i][j] and y[i] are all binary
```
Here $y_i=1$ means a facility is opened at site $i$ and $x_{ij}=1$ means that customer $j$ is serviced from site $i$

The readData(...) function uses the readAndWriteJson file to read data from a Json file
in the form
```
"site_labels": [list of strings with labels for the sites. One for each site must be provided if any]
"customer_labels": [list of strings with labels for the customers. One for each site must be provided if any]
"v_costs": [list of lists with the variable costs matrix]
"f_costs": [list of fixed opening costs]
```
