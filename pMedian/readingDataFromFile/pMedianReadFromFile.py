# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a p median problem with 5 potential facility sites and 5 customers
# The IP solved is given by
# max   sum ( i in 0..4 ) sum( j in 0..4) c[i][j]*x[i][j]
# s.t.  sum ( i in 0..4 ) x[i][j] == 1, for all j=0,..,4
#       x[i][j] <= y[i],                for all i=0,..,4 j=0,..,4
#       sum ( i in 0..4 ) y[i] == p
#       x[i][j], y[i] are all binary
# where c[i][j] is the cost of servicing customer j from location i and p is the number of facilities to place
# The readData(...) function has an argument for a file name. This is not used in this simple example! The data
# is simply hard coded in readData(...)
import pyomo.environ as pyomo
import readAndWriteJson as rwJson

def readData(filename: str) -> dict:
    # implementation of readData
    data = rwJson.readJsonFileToDictionary('pMedianDataFile')
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create the model object
    model = pyomo.ConcreteModel()
    # Copy the data to the model object
    model.p = data['p']
    model.n = data['n']
    model.m = data['m']
    model.c = data['c']
    model.locations = range(0, model.n)
    model.customers = range(0,model.m)
    # Define the x-variables
    model.x = pyomo.Var(model.locations, model.customers, within=pyomo.Binary, bounds=(0, 1))
    # Define the y-variables
    model.y = pyomo.Var(model.locations, within=pyomo.Binary, bounds=(0,1))
    # Define the objective function
    model.obj = pyomo.Objective(expr=sum(model.c[i][j]*model.x[i, j] for i in model.locations for j in model.customers))
    # Add the "service all" constraints
    model.serviceAll = pyomo.ConstraintList()
    for j in model.customers:
        model.serviceAll.add(expr=sum( model.x[i, j] for i in model.locations) == 1)
    # Add the indicator constraints
    model.indicators = pyomo.ConstraintList()
    for i in model.locations:
        for j in model.customers:
            model.indicators.add(expr=model.x[i, j] <= model.y[i])
    # Add cardinality constraint
    model.cardinality = pyomo.Constraint(expr=sum(model.y[i] for i in model.locations) == model.p)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    # Print solution information to prompt
    print('Objective function value =', pyomo.value(model.obj))
    print('Optimal values for the y-variables')
    for i in model.locations:
        print('y[{}]={}'.format(i, pyomo.value(model.y[i])))
    for j in model.customers:
        for i in model.locations:
            xVal = pyomo.value(model.x[i, j])
            if xVal == 1.0:
                print ('Customer', j, 'is serviced from location', i)


def main():
    data = readData('pathToTheDataFile')
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    main()
