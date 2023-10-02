# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2023
# Implementation of a fixed charge transportation problem where a set of suppliers
# {0,1,2,..,n-1} is given along with a set of customers {0,1,2,..,m-1}.
# A cost for sending one unit of flow from supplier i to customer j is given by c[i][j]
# and a fixed cost for sending a positive flow from i to j is given by f[i][j].
# In addition, each customer has a demand of d_j units of a product and each supplier can supply s_i units of the
# product
# With continuous flow variables, x[i,j], indicating the amount of flow from i to j and binary
# indicator variables, y[i, j], defined by the implication x[i, j]>0 => y[i, j]=1 a MILP formulation of the
# problem is given by
# min  sum ( i in 0..n-1 ) sum( i in 0..m-1 ) c[i][j]*x[i][j] + sum ( i in 0..n-1 ) sum ( j in 0..m-1 )  f[i][j]*y[i, j]
# s.t. sum ( i in 0..n-1 ) x[i][j] >= d[j],               for all j=0..m-1
#      sum ( j in 0..m-1 ) x[i][j] <= s[i],               for all i=0..n-1
#      x[i][j] <= M[i][j]*y[i][j],                           for all i in 0..n-1 and all j in 0..m-1
#      y[i][j] in {0,1}                                      for all i in 0..n-1
#      x[i][j] >= 0                                       for all i in 0..n-1 and j in 0..m-1
# Here, M[i][j] = min { d[j], s[i] } provides a valid value for the big-M's.
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


# Reads a data file passed as an argument. Returns a dict containing the data
def readData(filename: str)->dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


# Builds the fixed charge transportation MILP model. Returns a pyomo ConcreteModel object
def buildModel(data: dict)->pyomo.ConcreteModel:
    model = pyomo.ConcreteModel()
    #Copy data to the model object
    model.n = data['num_supply']
    model.m = data['num_demand']
    model.supplies = data['supplies']
    model.demands = data['demands']
    model.suppliers = range(model.n)
    model.customers = range(model.m)
    model.c = data['c']
    model.f = data['f']
    # Variables
    model.x = pyomo.Var(model.suppliers, model.customers, within=pyomo.NonNegativeReals)
    model.y = pyomo.Var(model.suppliers, model.customers, within=pyomo.Binary)
    # Objective function
    model.obj = pyomo.Objective(
        expr=sum(model.c[i][j]*model.x[i, j] for i in model.suppliers for j in model.customers)
        + sum(model.f[i][j]*model.y[i, j] for i in model.suppliers for j in model.customers)
    )
    # Demand constraints
    model.demandCsts = pyomo.ConstraintList()
    for j in model.customers:
        model.demandCsts.add(expr=sum(model.x[i, j] for i in model.suppliers) >= model.demands[j])
    # Supply constraints
    model.supplyCsts = pyomo.ConstraintList()
    for i in model.suppliers:
        model.supplyCsts.add(expr=sum(model.x[i, j] for j in model.customers) <= model.supplies[i])
    # Indicator constraints
    model.indicatorCsts = pyomo.ConstraintList()
    for i in model.suppliers:
        for j in model.customers:
            model.indicatorCsts.add(expr=model.x[i, j] <= min(model.demands[j], model.supplies[i]) * model.y[i, j])
    return model


# Solves the model passed as an argument.
def solveModel(model: pyomo.ConcreteModel):
    # Initialise a solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model)


# Prints information from the optimal solution to the prompt.
def displaySolution(model: pyomo.ConcreteModel):
    print('Optimal objective function value:', pyomo.value(model.obj))
    for i in model.suppliers:
        for j in model.customers:
            value = pyomo.value(model.x[i, j])
            if value > 0:
                print(Fore.RED + str(pyomo.value(model.x[i, j])), end=Fore.WHITE + ' | ')
            else:
                print(Fore.WHITE + str(pyomo.value(model.x[i, j])), end=Fore.WHITE + ' | ')
        print('')


# Main function defining the flow-logic of the file. Takes a string with a file name as argument.
def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    dataFileName = 'fctp.json'
    main(dataFileName)

