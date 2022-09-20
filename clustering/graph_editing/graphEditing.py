# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a graph editing problem where only edges can be deleted/added - that is, no alteration of the
# nodes Let G=(V,E) be a graph with node set V, |V| = n, and edge set E. The problem solved here is to
# minimize a weighted sum of the number of added and deleted edges, respectively, necessary for the graph G to be be
# partitioned into disjoint clusters containing no less than l nodes and no more than u nodes. The IP solved is given
# by
# min   sum ( i in 0..n-1 ) sum( j in 0..n-1) ( w1*x[i][j] - w2(1-x[i][j]) )*z[i][j]
# s.t.  z[i][j] + z[j][k] - 1 <= z[i][k],               for all i,j,k=0,..,n-1
#       l-1 <= sum ( j in 0..n-1 : j!= i ) z[i][j],     for all i=0..n-1
#       u-1 >= sum ( j in 0..n-1 : j!= i ) z[i][j],     for all i=0..n-1
#       z[i][j] in {0,1},                               for all i,j=0..n-1
#
# Here x[i][j]=1 if there is an arc from node i to node j in G. Furthermore, w1 and w2 are weights defining the
# relative importance of removing and adding arcs, repsectively.
# As we state that z[i][j]=1 indicate that node i is adjacent to node j, it means that j is also adjacent to node i
# Hence, we help the solver by adding the redundant, but helpful, constraints z[i][j]==z[j][i]
# The readData(...) function uses the readAndWriteJson file to read data from a Json file. The data file should store
# the adjacency matrix x[i][j] and a list of node-labels

import pyomo.environ as pyomo   # Used for modelling the IP
import readAndWriteJson as rwJson  # Used to read data from Json file
from displayGraph import displayGraph

def readData(graphData: str) -> dict():
    data = rwJson.readJsonFileToDictionary(graphData)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create model
    model = pyomo.ConcreteModel()
    # Copy data to model object
    model.X = data['X']
    model.labels = data['labels']
    model.nrNodes = len(data['labels'])
    model.lower = data['l']
    model.upper = data['u']
    model.nodes = range(0, model.nrNodes)
    model.removeW = 10
    model.addW = 1
    # Define variables
    model.z = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)
    # Add objective
    model.obj = pyomo.Objective(expr=sum(((model.removeW+model.addW)*model.X[i][j]-model.addW)*model.z[i, j]
                                         for i in model.nodes for j in model.nodes),sense=pyomo.maximize)
    # Add triangle inequalities
    model.triangle = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            for k in model.nodes:
                model.triangle.add(expr=model.z[i, j] + model.z[j, k] - 1 <= model.z[i, k])
    # Add lower bound on group sizes
    model.lowerSize = pyomo.ConstraintList()
    for i in model.nodes:
        model.lowerSize.add(expr=sum(model.z[i,j] for j in model.nodes if i != j) >= model.lower-1)
    # Add upper bound on group sizes
    model.upperSize = pyomo.ConstraintList()
    for i in model.nodes:
        model.upperSize.add(expr=sum(model.z[i, j] for j in model.nodes if i != j) <= model.upper-1)
    # Help the solver
    model.help = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            model.help.add(expr=model.z[i, j] == model.z[j, i])

    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('gurobi')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    isInGroup = [0]*model.nrNodes
    groupCount = 1
    print("HEJ MOR")
    for i in model.nodes:
        if isInGroup[i] == 0:
            isInGroup[i] = 1
            print('========================================')
            print('Group number', groupCount, 'consists of:')
            print(model.labels[i], '| ', end='')
            for j in model.nodes:
                if isInGroup[j] == 0 and pyomo.value(model.z[i,j]) == 1:
                    print(model.labels[j], '| ', end='')
                    isInGroup[j] = 1
            print('\n')
            groupCount = groupCount + 1


def main(clusterDataFile: str):
    data = readData(clusterDataFile)
    displayGraph(data['labels'], data['X'])
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)
    adjacency = []
    for i in model.nodes:
        adjacency.append([])
        for j in model.nodes:
            adjacency[i].append(pyomo.value(model.z[i, j]))
    displayGraph(data['labels'], adjacency)


if __name__ == '__main__':
    theDataFile = "data2022"
    main(theDataFile)
