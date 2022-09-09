# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a p-center based clustering problem on n points numbered 0,1,...,n-1
# The IP solved is given by
# min   sum ( i in 0..n-1 ) rhoMax
# s.t.  sum ( i in 0..n-1 ) x[i][j] == 1,   for all j=0,..,n-1
#       x[i][j] <= y[i],                    for all i,j in 0,...,n-1
#       sum ( i in 0..n-1 ) y[i] <= k
#       sum ( i in 0..n-1 ) d[i][j]*x[i][j] <= rhoMax
#       x[i][i] == y[i]                     for all i=0...n-1
#       x[i][j] and y[i] are all binary
# where d[i][j] is the distance between point i and point j
# The readData(...) function uses the readAndWriteJson file to read data from a Json file
# in the form of x coordinates and y coordinates
# Read data function also computes the distance matrix

import pyomo.environ as pyomo  # Used for modelling the IP
import matplotlib.pyplot as plt  # Used to plot the instance
import math  # Used to get access to sqrt() function
import readAndWriteJson as rwJson  # Used to read data from Json file


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
            tmpDist = abs(data['x'][i] - data['x'][j]) + abs(data['y'][i] - data['y'][j])
            dist[i].append(tmpDist)
    return dist


def readData(clusterData: str) -> dict():
    data = rwJson.readJsonFileToDictionary(clusterData)
    data['nrPoints'] = len(data['x'])
    data['dist'] = makeEuclideanDistanceMatrix(data)
    #data['dist'] = makeManhattanDistanceMatrix(data)
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
    model.groups = range(0, model.k)
    # Define variables
    model.x = pyomo.Var(model.points, model.groups, within=pyomo.Binary)
    model.D = pyomo.Var(model.groups, within=pyomo.NonNegativeReals)
    model.Dmax = pyomo.Var(within=pyomo.NonNegativeReals)
    # Add objective function
    model.obj = pyomo.Objective(expr=model.Dmax)
    # Add definition for Dmax
    model.DmaxDef = pyomo.ConstraintList()
    for l in model.groups:
        model.DmaxDef.add(expr=model.D[l] <= model.Dmax)
    # Add defintion for the D-variables
    model.Ddef = pyomo.ConstraintList()
    for i in model.points:
        for j in model.points:
            if i != j:
                for l in model.groups:
                    model.Ddef.add(expr=model.D[l] >= model.dist[i][j] * (model.x[i, l] + model.x[j, l] - 1))
    # Make sure that all points a in a group
    model.assignAll = pyomo.ConstraintList()
    for i in model.points:
        model.assignAll.add(expr=sum(model.x[i, l] for l in model.groups) == 1)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('glpk')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    print('Optimal diameter is:',pyomo.value(model.obj))
    labels = [0] * model.nrPoints
    ptNumber = list(model.points)
    # Print the groups to promt and save coordinates for plotting
    for l in model.groups:
        print('Group',l,'consists of:')
        for i in model.points:
            if pyomo.value(model.x[i,l]) == 1:
                print(i,',',end='')
                labels[i] = l
        print('')
    # Plot with different colors
    plt.scatter(model.xCoordinates, model.yCoordinates, c=labels)
    for i, label in enumerate(ptNumber):
        plt.annotate(ptNumber[i], (model.xCoordinates[i], model.yCoordinates[i]))
    plt.show()


def main(clusterDataFile: str):
    data = readData(clusterDataFile)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    theDataFile = "clusteringData_34_point"
    main(theDataFile)
