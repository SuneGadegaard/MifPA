This folder contains a small example showing how to perform a $k$-means cluster analysis on a small 2D example
The data in `clusteringData_34_point` is stored in a Json file with the following lay-out
```
"x": x-coordinates of the points
"y": y-coordinates of the points
"k": number of clusters 
```
The code snippet uses [`sklearn`](https://scikit-learn.org/stable/){:target="_blank"} library and its [$k$-means algorithm](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html){:target="_blank"}. 
After clustering the data, [matplotlib](https://matplotlib.org/){:target="_blank"} is used to plot the data as a scatter plot for visual inspection.

In order to read the data, the code in `readAndWriteJson.py` is used.
