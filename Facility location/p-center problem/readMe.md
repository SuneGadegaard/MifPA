Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022

Implementation of a $p$-center problem where a set of potential facility sites {$0,1,2,..,n-1$} is given along
with a set of customers {$0,1,2,..,m-1$}. A cost for servicing customer $j$ from facility site $i$ is given by $c_{ij}$.
Furthermore, an integer $p$ indicates how many facilities can be open in a feasible solution
The IP solved is given by

$$
\\begin{align}
      min         \ & \rho^{\mbox{max}}\\
      \text{s.t.:}\ & \sum_{i=0}^{n-1} x_{ij} = 1,    &&\forall j=0,\dots,m-1\\
                  \ & x_{ij} \leq y_i,                &&\forall i= 0,\dots,n-1,\ j = 0,\dots,m-1
                  \ & \sum_{i=1}^{n-1} y_i \leq p\\
                  \ & \sum_{i=0}^{n-1} c_{ij}x_{ij} \leq \rho^{\mbox{max}},&& \forall j in 0,\dots,m-1
                  \ & x_{ij}, y_i \text{ binary},     && \forall i=0,\dots,n-1,\ j=0,\dots,m-1
\\end{align}
$$

Here $y_i=1$ means a facility is opened at site i and $x_{ij}=1$ means that customer $j$ is serviced from site $i$.
The variable $\rho^{\mbox{max}}$ will equal the largest cost across all customers.

The readData(...) function uses the readAndWriteJson file to read data from a Json file
in the form
```
"site_labels": [list of strings with labels for the sites. One for each site must be provided if any]
"customer_labels": [list of strings with labels for the customers. One for each site must be provided if any]
"costs": [list of lists with the costs matrix]
"p": integer indicating how many facilities can be open in a feasible solution
```
