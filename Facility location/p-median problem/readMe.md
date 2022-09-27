Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
Implementation of a $p$-median problem where a set of potential facility sites $\{0,1,2,..,n-1\}$ is given along
with a set of customers $\{0,1,2,..,m-1\}$. A cost for servicing customer $j$ from facility site $i$ is given by $c_{ij}$
Furthermore, an integer $p\geq 1$ indicates how many facilities can be open in a feasible solution
The IP solved is given by
```
min   rhoMax
s.t.  sum ( i in 0..n-1 ) x[i][j] == 1,   for all j=0..m-1
      x[i][j] <= y[i],                    for all i in 0..n-1 and all j in 0..m-1
      sum ( i in 0..n-1 ) y[i] <= p
      sum ( i in 0..n-1 ) c[i][j]*x[i][j] <= rhoMax, for all j in 0..m-1
      x[i][j] and y[i] are all binary
```
Here $y_i=1$ means a facility is opened at site $i$ and $x_{ij}=1$ means that customer $j$ is serviced from site $i$
$\rho^{\max}$ will equal the largest cost across all customers
The readData(...) function uses the readAndWriteJson file to read data from a Json file
in the form
```
"site_labels": [list of strings with labels for the sites. One for each site must be provided if any]
"customer_labels": [list of strings with labels for the customers. One for each site must be provided if any]
"costs": [list of lists with the costs matrix]
"p": integer indicating how many facilities can be open in a feasible solution
```
