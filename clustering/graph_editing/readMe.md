This folder contains code for performing graph editing on a given graph, $G=(V,A)$.
The code uses a data-file format consisting of labels for the nodes, $V$, of the graph, an adjacency matrix defining the graph, 
and upper and lower bounds on the clusters in the graph computed.
The adjacency matrix is called $X$ and $X_{ij}=1$ if and only if there is an arc from node $i$ to node $j$ in $G$. That is, if $(i,j)\in A$.
For simplicity, we assume that $\vert V\vert=n$.

The model formulation uses binary variables $z_{ij}$ equalling one if and only if there is an arc from $i$ to $j$ in the edited graph

The graph editing problem solves is given by the IP:

```
max   w1*sum(i,j in 0..n-1) X[i][j]*z[i][j] - w2*sum(i,j in 0..n-1) (1-X[i][j])*z[i][j]
s.t.: z[i][j] + z[j][k] - 1 <= z[i][k],       for all i,j,k in 0..n-1
      l-1 <= sum(j in 0..n-1 : i!=j) z[i][j], for all i in 0..n-1
      sum(j in 0..n-1 : i!=j) z[i][j] <= u-1, for all i in 0..n-1  
      z[i][j] in {0,1},                       for all i,j in 0..n-1
```

The IP is modelled using Pyomo and then solved using an IP solver. The code suggests cbc, but any IP solver goes.

The code as it is relies on libraries
1. [Pyomo](http://www.pyomo.org/)
2. [Matplotlib](https://matplotlib.org/)
3. [networx](https://networkx.org/)
And then the code in readAndWriteJson is used to read the data from a Json-formattet file. Furthermore, there is a small file called "displayGraph.py",
which contains code for visualising the graphs - both the input and the output graphs.

First the graph defined by $X$ is displayed, then the IP is solved, and then the graph defined by $z$ as an adjacency matrix is displayed.
Below is a set of links to videos describing the implementation (danish)

* [About the structure of the code](https://www.loom.com/share/ffaa342f6c8a42738f38135478021b4c)
* [About moving files to the right folders](https://www.loom.com/share/723713b3818448de9f06e82c1a2cd130)
* [About implementing the readData function](https://www.loom.com/share/3f53e9c9413b4747a6956390a71e2f67)
* [About implementing the buildModel function](https://www.loom.com/share/f6aeb5c79ad442b489cbc22f78d67e78)
* [About implementing the solveModel function](https://www.loom.com/share/3640f790e4704c65b86c22d1b9fc3c54)
* [About implementing the displaySolution function](https://www.loom.com/share/adf23ecec6bf423a87a6bbff4369061d)
