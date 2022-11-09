# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Author: Sune Lauth Gadegaard
# Implementation of a Traveling Salesman Problem (TSP) between n-customers nodes and a depot (labeled 0)
# The implementation uses a lifted version of MTZ-based formulation.
# This lifting will usually improve solution times considerably compared to the original version of the constraints.
# The  IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1, for all j=1,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1, for all i=1,..,n
#       sum ( j in 1..n ) x[0][j] == m,
#       sum ( i in 1..n ) x[i][0] == m,
#       1 <= u[i] <= n,                        for all i=1,...,n
#       u[i] - u[j] + S*x[i][j] + (S-2)*x[j][i] <= n-1,        for all i,j=1,...,n
#       x[i][j] are all binary
# where d[i][j] is the distance between location i and location j and u[i]=k means that customer i is the k'th visit
# on one of the routes route. S is the maximum number of customers that can be serviced on a route, and m is the
# number of vehicles available for dispatching.
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
    model.u = pyomo.Var(model.customers, within=pyomo.NonNegativeReals, bounds=(1, data['S']))
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
    model.MTZ = pyomo.ConstraintList()
    for i in model.customers:
        for j in model.customers:
            model.MTZ.add(
                expr=model.u[i] - model.u[j] + data['S']*model.x[i, j] + (data['S']-2)*model.x[j, i] <= data['S'] - 1
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
    coordinatesPresent = 'xCord' in data and 'yCord' in data
    for vehicle in range(1, data['m']+1):
        if coordinatesPresent:
            displayX = [data['xCord'][0]]
            displayY = [data['yCord'][0]]
            labels = [0]
        # Find the customer, that starts the next route
        currentNode = 0
        for j in model.customers:
            if j > lastRouteStarter and pyomo.value(model.x[0, j]) >= 0.9999:
                currentNode = j
                if coordinatesPresent:
                    displayX.append(data['xCord'][currentNode])
                    displayY.append(data['yCord'][currentNode])
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
                        displayX.append(data['xCord'][currentNode])
                        displayY.append(data['yCord'][currentNode])
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
    main('small_mtsp_data')
