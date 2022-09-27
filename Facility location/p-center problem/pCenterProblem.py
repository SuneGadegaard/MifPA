# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a p-median problem where a set of potential facility sites {0,1,2,..,n-1} is given along
# with a set of customers {0,1,2,..,m-1}. A cost for servicing customer j from facility site i is given by c_ij
# Furthermore, an integer p indicates how many facilities can be open in a feasible solution
# The IP solved is given by
# min   rhoMax
# s.t.  sum ( i in 0..n-1 ) x[i][j] == 1,   for all j=0..m-1
#       x[i][j] <= y[i],                    for all i in 0..n-1 and all j in 0..m-1
#       sum ( i in 0..n-1 ) y[i] <= p
#       sum ( i in 0..n-1 ) c[i][j]*x[i][j] <= rhoMax, for all j in 0..m-1
#       x[i][j] and y[i] are all binary
# Here y[i]=1 means a facility is opened at site i and x[i][j]=1 means that customer j is serviced from site i
# rhoMax will equal the largest cost across all customers
# The readData(...) function uses the readAndWriteJson file to read data from a Json file
# in the form
# "site_labels": [list of strings with labels for the sites. One for each site must be provided if any]
# "customer_labels": [list of strings with labels for the customers. One for each site must be provided if any]
# "costs": [list of lists with the costs matrix]
# "p": integer indicating how many facilities can be open in a feasible solution


import pyomo.environ as pyomo  # Used for modelling the IP
import readAndWriteJson as rwJson  # Used to read data from Json file


def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Define the model
    model = pyomo.ConcreteModel()
    # Copy data to the model
    model.site_labels = data['site_labels']
    model.customer_labels = data['customer_labels']
    model.costs = data['costs']
    model.p = data['p']
    model.sites = range(0, len(data['costs']))
    model.customers = range(0, len(data['costs'][0]))
    # Define x and y variables for the model
    model.x = pyomo.Var(model.sites, model.customers, within=pyomo.Binary)
    model.y = pyomo.Var(model.sites, within=pyomo.Binary)
    model.rhoMax = pyomo.Var(within=pyomo.NonNegativeReals)
    # Add the objective function to the model
    model.obj = pyomo.Objective(expr=model.rhoMax)
    # Add the "sum to one"-constraints
    model.sumToOne = pyomo.ConstraintList()
    for j in model.customers:
        model.sumToOne.add(expr=sum(model.x[i, j] for i in model.sites) == 1)
    # Add the "if x[i,j]==1 then y[i]=1" constraints
    model.GUB = pyomo.ConstraintList()
    for i in model.sites:
        for j in model.customers:
            model.GUB.add(expr=model.x[i, j] <= model.y[i])
    # Add cardinality constraint
    model.cardinality = pyomo.Constraint(expr=sum(model.y[i] for i in model.sites) == model.p)
    # Add the lower bounds on the rhoMax variables
    model.rhoMaxDefinition = pyomo.ConstraintList()
    for j in model.customers:
        model.rhoMaxDefinition.add(expr=sum(model.costs[i][j] * model.x[i, j] for i in model.sites) <= model.rhoMax)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Define a solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    # Print optimal objective function value
    print('Optimal objective function value is', pyomo.value(model.obj))
    # Print the open facilities
    for i in model.sites:
        if pyomo.value(model.y[i]) == 1:
            print(model.site_labels[i], 'is open and the following customers are serviced:')
            for j in model.customers:
                if pyomo.value(model.x[i, j]) == 1:
                    print(model.customer_labels[j], end=',')
            print('\n')


def main(instance_file_name: str):
    data = readData(instance_file_name)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    instance_file_name = '101citiesDenmark'
    main(instance_file_name)
