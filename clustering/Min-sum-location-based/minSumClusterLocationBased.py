# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a p-median based clustering problem on n points numbered 0,1,...,n-1
# The IP solved is given by
# min   sum ( i in 0..n-1 ) sum( j in 0..n-1) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n-1 ) x[i][j] == 1,   for all j=0,..,n-1
#       x[i][j] <= y[i],                    for all i,j in 0,...,n-1
#       sum ( i in 0..n-1 ) y[i] <= k
#       x[i][j] and y[i] are all binary
# where d[i][j] is the distance between point i and point j
# The readData(...) function uses the readAndWriteJson file to read data from a Json file
# in the form of x coordinates and y coordinates
# Read data function also computes the distance matrix

import pyomo.environ as pyomo       # Used for modelling the IP
import matplotlib.pyplot as plt     # Used to plot the instance
import math                         # Used to get access to sqrt() function
import readAndWriteJson as rwJson   # Used to read data from Json file


def makeEuclideanDistanceMatrix(data: dict) -> list:
    dist = []
    nrPoints = len(data['x'])
    for i in range(0, nrPoints):
        dist.append([])
        for j in range(0, nrPoints):
            tmpDist = math.sqrt((data['x'][i] - data['x'][j]) ** 2 + (data['y'][i] - data['y'][j]) ** 2)
            dist[i].append(tmpDist)
    return dist


def makeManhattanDistanceMatrix(data: dict) -> list:
    dist = []
    nrPoints = len(data['x'])
    for i in range(0, nrPoints):
        dist.append([])
        for j in range(0, nrPoints):
            tmpDist = abs(data['x'][i]-data['x'][j]) + abs(data['y'][i]-data['y'][j])
            dist[i].append(tmpDist)
    return dist


def readData(clusterData: str) -> dict():
    data = rwJson.readJsonFileToDictionary(clusterData)
    data['nrPoints'] = len(data['x'])
    #data['dist'] = makeEuclideanDistanceMatrix(data)
    data['dist'] = makeManhattanDistanceMatrix(data)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create model
    model = pyomo.ConcreteModel()
    # Copy data to model object
    model.nrPoints = data['nrPoints']
    model.points = range(0, data['nrPoints'])
    model.xCoordinates = data['x']
    model.yCoordinates = data['y']
    model.dist = data['dist']
    model.k = data['k']
    # Define variables
    model.x = pyomo.Var(model.points, model.points, within=pyomo.Binary)
    model.y = pyomo.Var(model.points, within=pyomo.Binary)
    # Add objective function
    model.obj = pyomo.Objective(expr=sum(model.dist[i][j]*model.x[i, j] for i in model.points for j in model.points))
    # Add "all represented" constraints
    model.allRep = pyomo.ConstraintList()
    for j in model.points:
        model.allRep.add(expr=sum(model.x[i, j] for i in model.points) == 1)
    # Add only represent if y[i]=1
    model.GUB = pyomo.ConstraintList()
    for i in model.points:
        for j in model.points:
            model.GUB.add(expr=model.x[i, j] <= model.y[i])
    # Add cardinality constraint on number of groups
    model.cardinality = pyomo.Constraint(expr=sum(model.y[i] for i in model.points) == model.k)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('glpk')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    labels = [0]*model.nrPoints
    # Print the groups to promt and save coordinates for plotting
    for i in model.points:
        if pyomo.value(model.y[i]) == 1:
            print('Point', i, 'represents points:')
            for j in model.points:
                if pyomo.value(model.x[i, j]) == 1:
                    print (j,",",end='')
                    labels[j] = i
            print('\n')
    # Plot with different colors
    plt.scatter(model.xCoordinates, model.yCoordinates, c=labels)
    plt.show()



def main(clusterDataFile: str):
    data = readData(clusterDataFile)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    theDataFile = "clusteringData_34_point"
    main(theDataFile)