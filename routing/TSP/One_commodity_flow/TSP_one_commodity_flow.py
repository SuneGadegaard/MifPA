# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Author: Sune Lauth Gadegaard
# Implementation of a Traveling Salesman Problem (TSP) between n-customers nodes and a depot (labeled 0)
# The implementation uses a one commmodity flow formulation akin to the model presented by Gavish and Graves in
# "THE TRAVELLING SALESMAN PROBLEM AND RELATED PROBLEMS" (1978).
# The IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1, for all j=0,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1, for all i=0,..,n
#       f[i][j] <= n*x[i][j],                  for all i,j=0,...,n
#       f[i][j] >= min(1,i)*x[i][j],           for all i,j=0,...,n
#       sum ( j in 0..n ) f[i][j] == sum ( j in 0..n ) f[j][i] +1,  for all i=1,...,n
#       x[i][j] binary,                        for all i,j in 0..n
#       f[i][j] >= 0,                          for all i,j in 0..n
# where d[i][j] is the distance between location i and location j and f[i][j] equals the position of node i on the TSP
# route if x[i][j] = 1 otherwise f[i][j] = 0 and has no interpretation.
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
    for i in model.nodes:
        # Out of node i
        model.sumToOne.add(expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1)
        # Into node i
        model.sumToOne.add(expr=sum(model.x[j, i] for j in model.nodes if i != j) == 1)
    # Add descriptive comments here
    model.GeneralizedBounds = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            model.GeneralizedBounds.add(expr=model.f[i, j] <= data['n']*model.x[i, j])
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
    print('Solution value is:', pyomo.value(model.obj))
    # Print solution information to prompt
    print('Objective function value =', pyomo.value(model.obj))
    print('Optimal tour is')
    curNode = 0
    print(curNode, '->', end='')
    KeepOn = True
    counter = 0
    # flag for testing if coordinates are present in the data
    coordinatesPresent = 'xCord' in data and 'yCord' in data
    if coordinatesPresent:
        displayX = [data['xCord'][0]]
        displayY = [data['yCord'][0]]
        labels = [0]
    # Find the route from the x[i,j] values
    while KeepOn:
        counter = counter + 1
        # Find next on route
        for i in model.nodes:
            if i != curNode and pyomo.value(model.x[curNode, i]) == 1:
                if coordinatesPresent:
                    displayX.append(data['xCord'][i])
                    displayY.append(data['yCord'][i])
                if i > 0:
                    print(i, '->', end='')
                    if coordinatesPresent:
                        labels.append(i)
                else:
                    print(i, end='')
                tmpCurNode = i
        curNode = tmpCurNode
        if curNode < 1:
            break
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
    main('bigger_tsp_data')
