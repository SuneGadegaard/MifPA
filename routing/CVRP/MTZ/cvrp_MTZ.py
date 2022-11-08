# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Author: Sune Lauth Gadegaard
# Implementation of a capacitated vehicle routing problem (CVRP) with n-customers nodes and a depot (labeled 0)
# The implementation uses a an MTZ-based formulation where the classical u[i] - u[j] + Q*x[i][j] <= Q - q[j] are lifted
# to u[i] - u[j] + Q*x[i][j] + (Q - q[j] - q[i])*x[j][i] <= Q - q[j].
# The  IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1,                              for all j=1,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1,                              for all i=1,..,n
#       sum ( j in 1..n ) x[0][j] == m,
#       sum ( i in 1..n ) x[i][0] == m,
#       q[i] <= u[i] <= Q,                                                  for all i=1,...,n
#       u[i] - u[j] + Q*x[i][j] + (Q - q[j] - q[i])*x[j][i] <= Q - q[j],       for all i,j=1,...,n
#       x[i][j] are all binary
# where d[i][j] is the distance between location i and location j and u[i] is an upper bound on the amount of demand
# serviced on the route from the depot to the customer node i.
# Q is the maximum capacity on a vehicle and q[i] is the demand at node i (we assume, that q[0]=0)
# number of vehicles available for dispatching.
# The readData(...) function uses the readAndWriteJson file to read data from a Json file

import pyomo.environ as pyomo       # Used to model the IP
import readAndWriteJson as rwJson   # Used for reading the data file in Json format
import matplotlib.pyplot as plt     # Used for plotting the result
import math

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
    # Create model object
    model = pyomo.ConcreteModel()
    # Add some data to the model object
    model.numOfNodes = data['n'] + 1
    model.nodes = range(0, model.numOfNodes)
    model.customers = range(1, model.numOfNodes)
    # Define the variables
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    model.u = pyomo.Var(model.customers, within=pyomo.NonNegativeReals, bounds=(1, data['Q']))
    # Set a lower bound on each u[i] variable corresponding to customer i's demand
    for i in model.customers:
        model.u[i].setlb(data['q'][i])
    # Remove the diagonal. Change to "for i in model.customers" if it should be allowed to not use all vehicles
    for i in model.nodes:
        model.x[i, i].fix(0)
    # Add the objective function
    model.obj = pyomo.Objective(
        expr=sum(data['dist'][i][j]*model.x[i, j] for i in model.nodes for j in model.nodes if i != j)
    )
    # Add both the in- and out-degree constraints for the customers
    model.sumToOne = pyomo.ConstraintList()
    for i in model.customers:
        # Out of node i
        model.sumToOne.add(expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1)
        # Into node i
        model.sumToOne.add(expr=sum(model.x[j, i] for j in model.nodes if i != j) == 1)
    # Add the in- and out-degree constraints for the depot
    model.depotOut = pyomo.Constraint(expr=sum(model.x[0, j] for j in model.nodes) == data['m'])
    model.depotIn = pyomo.Constraint(expr=sum(model.x[i, 0] for i in model.nodes) == data['m'])
    # Add the lifte MTZ sub tour elimination constraints for all pairs (i,j) of customers
    model.MTZ = pyomo.ConstraintList()
    for i in model.customers:
        for j in model.customers:
            model.MTZ.add(
                expr=model.u[i] - model.u[j] + data['Q']*model.x[i, j]
                     + (data['Q']-data['q'][i]-data['q'][j])*model.x[j, i] <= data['Q'] - data['q'][j]
            )
    # return the model object
    return model


def solveModel(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory('gurobi')
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
