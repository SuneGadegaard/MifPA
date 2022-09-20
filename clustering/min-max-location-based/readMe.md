This folder contains code for performing clustering on a dataset.
The code uses a data-file format consisting of $(x,y)$-coordinates of data points, 
but it can easily be changed to performing clustering on any type of data
where a measure of distance between data-points is given in an $n \times n$ $(d_{ij})$-matrix, where $d_{ij}$ denotes the "distance" 
between data point $i$ and $j$.
The only assumptions on the $(d_{ij})$-matrix are that $d_{ii}=0$ and $d_{ij}\geq 0$ for all $i$ and $j$.

The clustering is perfomed using an integer programming (IP) model identical to the p-center problem:
```
min   rhoMax
s.t.: sum ( i in 0..n-1 ) x[i][j] == 1,               for all j=0..n-1
      x[i][j] <= y[i],                                for all i,j=0..n
      sum ( i in 0..n-1 ) y[i] <= k,
      sum ( i in 0..n-1 ) d[i][j]*x[i][j] <= rhoMax,  for all j=0..n-1
      x[i][i]==y[i],                                  for i=0..n-1
      x[i][j] and y[i] all binary
```

The IP is modelled using [Pyomo](http://www.pyomo.org/) and then solved usin an IP solver. The code suggests [`glpk`](https://www.gnu.org/software/glpk/), but any IP solver goes.

The code as it is relies on libraries
1. [Pyomo](http://www.pyomo.org/)
2. [Matplotlib](https://matplotlib.org/)
3. [Math](https://docs.python.org/3/library/math.html)
And then the code in `readAndWriteJson.py` is used to read the data from a Json-formattet file.

After the IP i solved, the `displaySolution()`-function is called which plots the solution for visual inspection
