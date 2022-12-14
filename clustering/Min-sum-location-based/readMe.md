This folder contains code for performing clustering on a dataset.
The code uses a data-file format consisting of $(x,y)$-coordinates of data points, but it can easily be changed to performing clustering on any type of data
where a measure of distance between data-points is given in an $n \times n$ $(d_ij)$ matrix, where $d_{ij}$ denotes the "distance" between data point $i$ and $j$.
The only assumptions on the $(d_{ij})$ matrix are that $d_{ii}=0$ and $d_{ij}\geq 0$ for all $i$ and $j$.

The clustering is perfomed using an integer programming (IP) model identical to the $p$-median problem:
```
min   sum ( i in 0..n-1 ) sum ( i in 0..n-1 ) d[i][j]*x[i][j]
s.t.: sum ( i in 0..n-1 ) x[i][j] == 1,   for all j=0..n-1
      x[i][j] <= y[i],                    for all i,j=0..n
      sum ( i in 0..n-1 ) y[i] <= k,
      x[i][j] and y[i] all binary
```
The IP is modelled using Pyomo and then solved using an IP solver. The code suggests `glpk`, but any IP solver goes.

The code as it is relies on libraries
1. [Pyomo](pyomo.org)
2. [Matplotlib](https://matplotlib.org/)
3. [Math](https://docs.python.org/3/library/math.html)

And then the code in `readAndWriteJson.py` is used to read the data from a Json-formattet file.

After the IP i solved, the `displaySolution()`-function is called, which plots the solution for visual inspection
