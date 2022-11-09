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


def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    model = pyomo.ConcreteModel()
    model.numOfNodes = data['n']+1
    # Add descriptive comments here
    model.nodes = range(0, model.numOfNodes)
    model.customers = range(1, model.numOfNodes)
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    model.f = pyomo.Var(model.nodes, model.nodes, within=pyomo.NonNegativeReals)
    # Add descriptive comments here
    for i in model.nodes:
        model.x[i, i].fix(0)
    # Add descriptive comments here
    model.obj = pyomo.Objective(
        expr=sum(data['dist'][i][j]*model.x[i, j] for i in model.nodes for j in model.nodes if i != j)
    )
    # Add descriptive comments here
    model.sumToOne = pyomo.ConstraintList()
    for i in model.customers:
        # Out of node i
        model.sumToOne.add(expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1)
        # Into node i
        model.sumToOne.add(expr=sum(model.x[j, i] for j in model.nodes if i != j) == 1)
    # Add descriptive comments here
    model.depotOut = pyomo.Constraint(expr=sum(model.x[0, j] for j in model.nodes) == data['m'])
    model.depotIn = pyomo.Constraint(expr=sum(model.x[i, 0] for i in model.nodes) == data['m'])
    # Add descriptive comments here
    model.GeneralizedBounds = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            model.GeneralizedBounds.add(expr=model.f[i, j] <= data['S']*model.x[i, j])
            model.GeneralizedBounds.add(expr=model.f[i, j] >= min(i, 1)*model.x[i, j])
    # Add descriptive comments here
    model.flowConservation = pyomo.ConstraintList()
    for i in model.customers:
        model.flowConservation.add(
            expr=sum(model.f[i, j] for j in model.nodes) == sum(model.f[j, i] for j in model.nodes) + 1
        )
    return model


def solveModel(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory('gurobi')
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel(), data: dict):
    # Print total length of tours
    print('Total length of tours:', pyomo.value(model.obj))
    # Find a tour for each vehicle
    lastRouteStarter = 0
    coordinatesPresent = 'xCoord' in data and 'yCoord' in data
    for vehicle in range(1, data['m']+1):
        print('Bil nummer', vehicle, "printes nu")
        if coordinatesPresent:
            displayX = [data['xCoord'][0]]
            displayY = [data['yCoord'][0]]
            labels = [0]
        # Find the customer, that starts the next route
        currentNode = 0
        for j in model.customers:
            if j > lastRouteStarter and pyomo.value(model.x[0, j]) >= 0.9999:
                currentNode = j
                if coordinatesPresent:
                    displayX.append(data['xCoord'][currentNode])
                    displayY.append(data['yCoord'][currentNode])
                    labels.append(currentNode)
                break
        lastRouteStarter = j
        print('The route for vehicle', vehicle, 'is:')
        print('0->', currentNode, end='')
        # Build the route from currenNode back to the depot
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
            # Start plotting the solution to a coordinate system
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
    main('bigger_mtsp_data')
