import readAndWriteJson as rwJson   # Used to read the data from a Json file
from sklearn.cluster import KMeans  # Used for the K-means algorithm
import matplotlib.pyplot as plt     # Used for plotting the results


def main():
    # Read data from Json file
    data = rwJson.readJsonFileToDictionary('clusteringData_34_point')
    # Make a list of list with x as first column and y as second
    points = list(zip(data['x'], data['y']))
    # Create a k-means object with data['k'] clusters
    kmeans = KMeans(n_clusters=data['k'])
    # Run the k-means algorithm on the data
    kmeans.fit(points)
    # Plot the data en a scatter plot
    plt.scatter(data['x'], data['y'], c=kmeans.labels_)
    plt.show()


if __name__ == '__main__':
    main()