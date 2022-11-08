# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Author: Sune Lauth Gadegaard
# Implementation of a Traveling Salesman Problem (TSP) between n-customers nodes and a depot (labeled 0)
# The implementation uses a one commmodity flow formulation akin to the model presented by Gavish and Graves in
# "THE TRAVELLING SALESMAN PROBLEM AND RELATED PROBLEMS" (1978).
# The IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1, for all j=1,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1, for all i=1,..,n
#       sum ( j in 1..n ) x[0][j] == m,
#       sum ( i in 1..n ) x[i][0] == m,
#       f[i][j] <= S*x[i][j],                  for all i,j=0,...,n
#       f[i][j] >= min(1,i)*x[i][j],           for all i,j=0,...,n
#       sum ( j in 0..n ) f[i][j] == sum ( j in 0..n ) f[j][i] +1,  for all i=1,...,n
#       x[i][j] binary,                        for all i,j in 0..n
#       f[i][j] >= 0,                          for all i,j in 0..n
# where d[i][j] is the distance between location i and location j and f[i][j] equals the position of node i on the TSP
# route if x[i][j] = 1 otherwise f[i][j] = 0 and has no interpretation. S is the maximum number of customers that
# can be serviced on a route, and m is the number of vehicles available for dispatching.
# The readData(...) function uses the readAndWriteJson file to read data from a Json file

import pyomo.environ as pyomo       # Used to model the IP
import readAndWriteJson as rwJson   # Used for reading the data file in Json format
import matplotlib.pyplot as plt     # Used for plotting the result
import math                         # Used for generating a distance matrix, if it is not present


# Function, taking a dict as argument, and returns a list of lists storing a distance matrix
# "data" must have keys "xCoord" and "yCoord". No error handling at the moment!
def makeDistanceMatrix(data: dict) -> list:
    numNodes = len(data['xCoord'])
    dist = []
    for i in range(numNodes):
        dist.append([])
        for j in range(numNodes):
            tmpDist = (data['xCoord'][i] - data['xCoord'][j]) ** 2 + (data['yCoord'][i] - data['yCoord'][j]) ** 2
            dist[i].append(round(math.sqrt(tmpDist)))
    return dist


# Reads the data from a data file in Json format. Must include
# n = number of customers as an int
# m = number of vehicles as an int
# Q = capacity of the vehicles as an int
# q = list of demands of length n+1
# The data file must include either
#   xCoord = list of x-coordinates of length n+1
#   yCoord = list of y-coordinates of length n+1
# or
#   dist = list of lists containing a distance matrix of size (n+1) x (n+1).
# or both
def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    if 'dist' not in data:
        data['dist'] = makeDistanceMatrix(data)
        newFileName = filename + '_new'
        rwJson.saveDictToJsonFile(data, newFileName)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create a model object
    model = pyomo.ConcreteModel()
    # Store some data in the model object
    model.numOfNodes = data['n'] + 1
    model.nodes = range(0, model.numOfNodes)
    model.customers = range(1, model.numOfNodes)
    # Define variables
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    model.f = pyomo.Var(model.nodes, model.nodes, within=pyomo.NonNegativeReals, bounds=(0, data['Q']))
    # Remove the diagonal. Change to "for i in mode.customers:" if it should be allowed to not use all vehicles
    for i in model.nodes:
        model.x[i, i].fix(0)
    # Add the objective to the model
    model.obj = pyomo.Objective(
        expr=sum(data['dist'][i][j] * model.x[i, j] for i in model.nodes for j in model.nodes if i != j)
    )
    # Add the in- and out-degree constraints for all the customers
    model.sumToOne = pyomo.ConstraintList()
    for i in model.customers:
        # Out of node i
        model.sumToOne.add(expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1)
        # Into node i
        model.sumToOne.add(expr=sum(model.x[j, i] for j in model.nodes if i != j) == 1)
    # Add the in- and out-degree constraints for the depot
    model.depotOut = pyomo.Constraint(expr=sum(model.x[0, j] for j in model.nodes) == data['m'])
    model.depotIn = pyomo.Constraint(expr=sum(model.x[i, 0] for i in model.nodes) == data['m'])
    # Add the generalized variable bounds f[i][j] <= (Q-q[j])x[i][j] and f[i][j] >= min(i,1)x[i][j]
    model.GeneralizedBounds = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            model.GeneralizedBounds.add(expr=model.f[i, j] <= (data['Q'] - data['q'][j]) * model.x[i, j])
            model.GeneralizedBounds.add(expr=model.f[i, j] >= data['q'][i] * model.x[i, j])
    # Add the flow conservation constraints to the model
    model.flowConservation = pyomo.ConstraintList()
    for i in model.customers:
        model.flowConservation.add(
            expr=sum(model.f[i, j] for j in model.nodes) == sum(model.f[j, i] for j in model.nodes) + data['q'][i]
        )
    # Return the model object
    return model


def solveModel(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory('cplex')
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel(), data: dict):
    print('Total length of the', data['m'], 'tours are', pyomo.value(model.obj))
    # Find a tour for each vehicle
    lastRouteStarter = 0
    # Make flag for checking if coordinates are available
    coordinatesPresent = ('xCoord' in data) and ('yCoord' in data)
    # Create a route for each vehicle
    for vehicle in range(1, data['m'] + 1):
        # Each route starts at the depot
        if coordinatesPresent:
            displayX = [data['xCoord'][0]]
            displayY = [data['yCoord'][0]]
            labels = [0]
        # Find the customer, that starts this route
        currentNode = 0
        for j in model.customers:
            if j > lastRouteStarter and pyomo.value(model.x[0, j]) >= 0.9999:
                currentNode = j
                if coordinatesPresent:
                    displayX.append(data['xCoord'][currentNode])
                    displayY.append(data['yCoord'][currentNode])
                    labels.append(currentNode)
                break
        lastRouteStarter = currentNode
        print('The route for vehicle', vehicle, 'is:')
        print('0->', currentNode, end='')
        # Build the route from currentNode back to the depot
        while currentNode != 0:
            for j in model.nodes:
                if currentNode != j and pyomo.value(model.x[currentNode, j]) >= 0.9999:
                    print('->', j, end='')
                    currentNode = j
                    if coordinatesPresent:
                        displayX.append(data['xCoord'][currentNode])
                        displayY.append(data['yCoord'][currentNode])
                        labels.append(currentNode)
                    break
        print('\n')
        if coordinatesPresent:
            # Start plotting the solution to a coordinate system if coordinates are present
            if coordinatesPresent:
                plt.plot(displayX, displayY, '-o')
                for i, label in enumerate(labels):
                    plt.annotate(label, (displayX[i], displayY[i]))
    plt.show()


def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model, data)


if __name__ == '__main__':
    main('cvrpDataFile_n_39')
