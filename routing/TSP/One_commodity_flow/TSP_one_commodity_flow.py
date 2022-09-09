# Author: Sune Lauth Gadegaard
# Date: 2022-09-07
# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a Traveling Salesman Problem (TSP) between n-customers nodes and a depot (labled 0)
# The IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) d[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1,                      for all j=0,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1,                      for all i=0,..,n
#       f[i][j] <= n*x[i][j],                                       for all i,j=0,...,n
#       sum ( j in 0..n ) f[i][j] = sum ( j in 0..n ) f[j][i] +1,   for all i=1,..,n
#       x[i][j] are all binary
# where d[i][j] is the distance between location i and location j
# The readData(...) function uses the readAndWriteJson file to read data from a Json file
import pyomo.environ as pyomo  # Used for modelling the TSP as an integer programming problem
import readAndWriteJson as rwJson  # Used for reading the instance file
import matplotlib.pyplot as plt  # Used for plotting the result


def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create the model object
    model = pyomo.ConcreteModel()
    # Copy the data to the model object
    model.n = data['n']
    model.dist = data['dist']
    model.customers = range(1, model.n + 1)
    model.nodes = range(0, model.n + 1)
    # Define the x-variables
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary, bounds=(0, 1))
    # Define the u-variables
    model.f = pyomo.Var(model.nodes, model.nodes, within=pyomo.NonNegativeReals, bounds=(0, model.n))
    # Define the objective function
    model.obj = pyomo.Objective(expr=sum(model.dist[i][j] * model.x[i, j] for i in model.nodes for j in model.nodes))
    # Add the "visit all" constraints
    model.visitAll = pyomo.ConstraintList()
    for j in model.nodes:
        model.visitAll.add(expr=sum(model.x[i, j] for i in model.nodes if i != j) == 1)
    # Add the "leave all" constraints
    model.leaveAll = pyomo.ConstraintList()
    for i in model.nodes:
        model.leaveAll.add(expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1)
    # Add flow conservation constraints for f-variables
    model.flowConserve = pyomo.ConstraintList()
    for i in model.customers:
        model.flowConserve.add(expr=sum(model.f[i, j] for j in model.nodes) == sum(model.f[j, i] for j in model.nodes) + 1)
    # Add GUBs for all f-variables
    model.GUB = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            model.GUB.add(expr=model.f[i, j] <= model.n*model.x[i, j])
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('cplex')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel(), data: dict):
    # Print solution information to prompt
    print('Objective function value =', pyomo.value(model.obj))
    print('Optimal tour is')
    curNode = 0
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
        tmpCurNode = 0
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


def main(tspDataFileName: str):
    data = readData(tspDataFileName)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model, data)


if __name__ == '__main__':
    main("small_tsp_data")