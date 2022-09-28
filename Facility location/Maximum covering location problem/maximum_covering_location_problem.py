# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a minimum cost covering location problem where a set of potential facility
# sites {0,1,2,..,n-1} is given along with a set of customers {0,1,2,..,m-1}.
# A cost for opening a facility at site i is given by f_i. Furthermore, a binary matrix (a_ij) is given where
# a_ij = 1 if and only if a facility at site i can cover customer j. In this particular example, an integer p
# specifies the number of open facilities allowed in a fasible solution.
# Finally, for each customer an integer b_j specifies how many facilities should be "within reach" for customer j
# to be fully covered
#
# The IP solved is given by
# min   sum ( i in 0..n-1 ) f[i]*y[i]
# s.t.  sum ( i in 0..n-1 ) a[i][j]*y[i] >= b[j],   for all j=0..m-1
#       sum ( i in 0..n-1 ) y[i] <= p,
#       y[i] all binary
# Here y[i]=1 means a facility is opened at site i.
# The readData(...) function uses the readAndWriteJson file to read data from a Json file
# in the form
# "site_labels": [list of strings with labels for the sites. One for each site must be provided if any]
# "customer_labels": [list of strings with labels for the customers. One for each site must be provided if any]
# "cover_matrix": [list of list. cover_maxtrix[i][j]=1 if and only if facility i can cover customer j. 0 otherwise]
# "fixed_costs": [list of fixed opening costs]
# "b": [list of integers. b[j] specifies the number of facilities needed to cover customer j]
# "p": integer specifying the maximum number of facilities to open in an optimal solution

import pyomo.environ as pyomo  # Used for modelling the IP
import readAndWriteJson as rwJson  # Used to read data from Json file
from termcolor import colored



def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Define the model
    model = pyomo.ConcreteModel()
    # Copy data to model
    model.facilities = data['site_labels']
    model.customers = data['customer_labels']
    model.facilityRange = range(0, len(model.facilities))
    model.customerRange = range(0, len(model.customers))
    model.a = data['cover_matrix']
    model.b = data['b']
    model.p = data['p']
    # Define variables
    model.y = pyomo.Var(model.facilityRange, within=pyomo.Binary)
    model.z = pyomo.Var(model.customerRange, within=pyomo.Binary)
    # Define objective function
    model.obj = pyomo.Objective(expr=sum(model.z[j] for j in model.customerRange), sense=pyomo.maximize)
    # Add covering constraints
    model.coveringCsts = pyomo.ConstraintList()
    for j in model.customerRange:
        model.coveringCsts.add(expr=sum(model.a[i][j]*model.y[i] for i in model.facilityRange) >= model.b[j]*model.z[j])
    # Add cardinality constraint
    model.cardinality = pyomo.Constraint(expr=sum(model.y[i] for i in model.facilityRange) <= model.p)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Define a solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    # Print optimal objective function value
    print('Optimal objective function value is', pyomo.value(model.obj))
    print('The following facilities are open:')
    for i in model.facilityRange:
        if pyomo.value(model.y[i]) == 1:
            print(model.facilities[i], end=',')
    print('\nCustomers are covered as follows:')
    for j in model.customerRange:
        if pyomo.value(model.z[j]) == 1:
            print(colored(model.customers[j], 'green'),end='->\t')
        else:
            print(colored(model.customers[j], 'red'), end='->\t')
        for i in model.facilityRange:
            if model.a[i][j] == 1 and pyomo.value(model.y[i])==1:
                print(model.facilities[i], end=',')
        print('')
    # Print the open facilities


def main(instance_file_name):
    data = readData(instance_file_name)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    instance_file_name = 'maxCoverLocationData'
    main(instance_file_name)
