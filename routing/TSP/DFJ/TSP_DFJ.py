# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Author: Sune Lauth Gadegaard
# Implementation of a Traveling Salesman Problem (TSP) between n-customers nodes and a depot (labeled 0)
# The implementation uses the full DFJ formulation - with all subsets of {0..n} enumerated and all sub-tour constraitns
# added up front.
# This is a hopeless approach for solving the TSP and is only implemented for educational purposes!
# The  IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1, for all j=0,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1, for all i=0,..,n
#       sum ( i in S ) sum ( j in S ) x[i][j] <= |S| - 1           for all S \subset {0..n}: 2 <= |S| <= n
#       x[i][j] are all binary
# where d[i][j] is the distance between location i and location j
#
# The readData(...) function uses the readAndWriteJson file to read data from a Json file

import pyomo.environ as pyomo       # Used to model the IP
import readAndWriteJson as rwJson   # Used for reading the data file in Json format
import matplotlib.pyplot as plt     # Used for plotting the result


# Returns all subsets of a list which has no less than 2 elements and no more than len(s)-1
def powerset(s: list) -> list:
    x = len(s)
    allSubSets = []
    for i in range(1 << x):
        nextList = [s[j] for j in range(x) if (i & (1 << j))]
        nextListLength = len(nextList)
        if 2 <= nextListLength <= x - 1:
            allSubSets.append(nextList)
    return allSubSets


def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    data['allSubSets'] = powerset(list(range(0, data['n'])))
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    model = pyomo.ConcreteModel()
    # Add descriptive comments here
    model.nodes = range(0, data['n']+1)
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
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

    # Add all the sub-tour elimination constraints
    model.SECs = pyomo.ConstraintList()
    for set in data['allSubSets']:
        model.SECs.add(expr=sum(model.x[i, j] for i in set for j in set if i != j) <= len(set)-1)
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


def displaySolutionSimple(model: pyomo.ConcreteModel(), data: dict):
    currentNode = 0
    # Find first on tour:
    for j in model.nodes:
        if pyomo.value(model.x[currentNode, j]) >= 0.9999:
            print('0 ->', j, end='')
            currentNode = j
            break
    # Find the remaining nodes of the tour
    while currentNode != 0:
        # Find the next node
        for j in model.nodes:
            if pyomo.value(model.x[currentNode, j]) >= 0.9999:
                print('->', j, end='')
                currentNode = j
                break


def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model, data)


if __name__ == '__main__':
    main('small_tsp_data')