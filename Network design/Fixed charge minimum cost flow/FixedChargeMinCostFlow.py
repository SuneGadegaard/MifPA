# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2023
# Implementation of a fixed charge minimum cost problem where a graph G=(V,E), a source node s and a sink node t
# is given.
# A cost for sending one unit of flow from node i to node j in G is given by c[i][j]
# and a fixed cost for sending a positive flow from i to j is given by f[i][j].
# The sink node, t, demands d_t units of flow
# With continuous flow variables, x[i,j], indicating the amount of flow sent from node i to node j and binary
# indicator variables, y[i, j], defined by the implication x[i, j]>0 => y[i, j]=1 a MILP formulation of the
# problem is given by
# min  sum ( (i,j) in E) ) c[i][j]*x[i][j] + sum ( (i,j) in E )  f[i][j]*y[i, j]
# s.t. sum ( (i,j) in E : i=s ) x[i, j] == d_t,
#      sum ( (i,j) in E : j=t ) x[i, j] == d_t,
#      sum( (i,j) in E : i=l ) x[i, j] == sum( (i,j) in E : j=l) x[i,j],  for all l in V\{s,t}
#      y[i][j] in {0,1}                                                   for all (i,j) in E
#      x[i][j] >= 0                                                       for all (i,j) in E
# Here, M[i][j] = d_t provides a valid value for the big-M's.
# The readData(...) function uses the readAndWriteJson file to read data from a Json file in the form
# "num_supply": integer giving the number of suppliers
# "num_demand": integer giving the number customers/demand points
# "supplies": [list of supplies for each supplier]
# "demands": [list of demands for each customer]
# "c": [list of lists. c[i][j] is the per unit cost of flow from i to j]
# "f": [list of lists. f[i][j] is the fixed cost incurred if y[i, j]=1 ]


import pyomo.environ as pyomo  # For creating the mathematical model
import readAndWriteJson as rwJson  # For reading files in json format
from colorama import Fore  # Used for coloring the non-zero entries in the flow matrix
import displayGraph as dispGraph


# Reads a data file passed as an argument. Returns a dict containing the data
def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    dispGraph.displayGraph([str(i) for i in range(data['numNodes'])], data['adjacency_matrix'])
    data['edges'] = {(i, j) for i in range(data['numNodes']) for j in range(data['numNodes']) if
                     data['adjacency_matrix'][i][j] == 1}
    return data


# Builds the fixed charge transportation MILP model. Returns a pyomo ConcreteModel object
def buildModel(data: dict) -> pyomo.ConcreteModel:
    model = pyomo.ConcreteModel()
    # Copy data to the model object
    model.edges = data['edges']
    model.nodes = range(data['numNodes'])
    model.source = data['source']
    model.sink = data['sink']
    model.c = data['var_costs']
    model.f = data['fixed_costs']
    model.demand = data['demand']
    # Variables
    model.x = pyomo.Var(model.edges, within=pyomo.NonNegativeReals)
    model.y = pyomo.Var(model.edges, within=pyomo.Binary)
    # Objective function
    model.obj = pyomo.Objective(
        expr=sum(model.c[i][j] * model.x[(i, j)] for (i, j) in model.edges)
             + sum(model.f[i][j] * model.y[(i, j)] for (i, j) in model.edges)
    )
    # Correct flow out of source
    model.sourceCst = pyomo.Constraint(
        expr=sum(model.x[(i, j)] for (i, j) in model.edges if i == model.source) == model.demand
    )
    # Correct flow into sink
    model.sinkCst = pyomo.Constraint(
        expr=sum(model.x[(i, j)] for (i, j) in model.edges if j == model.sink) == model.demand
    )
    # Correct inflow=out flow in all other nodes
    model.flowConservation = pyomo.ConstraintList()
    for l in model.nodes:
        if l not in {model.sink, model.source}:
            model.flowConservation.add(
                expr=sum(model.x[(i, j)] for (i, j) in model.edges if j == l) ==
                     sum(model.x[(i, j)] for (i, j) in model.edges if i == l)
            )
    # Indicator constraints enforcing x[i, j] > 0 => y[i, j] = 1
    model.GUB = pyomo.ConstraintList()
    for e in model.edges:
        model.GUB.add(expr=model.x[e] <= model.demand * model.y[e])
    return model


# Solves the model passed as an argument.
def solveModel(model: pyomo.ConcreteModel):
    # Initialise a solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)


# Prints information from the optimal solution to the prompt.
def displaySolution(model: pyomo.ConcreteModel):
    print(f'Optimal objective function value: {pyomo.value(model.obj)}')
    newAdjacencyMatrix = [[0 for i in model.nodes] for j in model.nodes]
    for (i, j) in model.edges:
        if pyomo.value(model.x[(i, j)]) >= 0.1:
            newAdjacencyMatrix[i][j] = 1
    dispGraph.displayGraph([str(i) for i in model.nodes], newAdjacencyMatrix)


# Main function defining the flow-logic of the file. Takes a string with a file name as argument.
def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    dataFileName = 'minCostNetworkFlow.json'
    main(dataFileName)
