# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation of a knapsack problem with 10 items and only one constraint
# The IP solved is given by
# max   sum ( i in 0..9 ) p[i]*x[i]
# s.t.  sum ( i in 0..9 ) c[i]*x[i] <= B
#       x[i] in {0,1} for all i=0,...,9
# where p[i] is the prize for packing item i, c[i] is the cost of item i, and B is budget available
# The readData(...) functions has an argument for a file name. This is not used in this simple example! The data
# is simply hard coded in readData(...)
import pyomo.environ as pyomo


def readData(filename: str) -> dict:
    # implementation of function
    data = dict()
    data['p'] = [26, 98, 85, 98, 82, 76, 75, 46, 33, 34]
    data['c'] = [20, 34, 48, 52, 74, 50, 37, 20, 19, 25]
    data['B'] = 125
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create the model object
    model = pyomo.ConcreteModel()
    # Copy the data to the model object
    model.p = data['p']
    model.c = data['c']
    model.B = data['B']
    model.items = range(0,len(data['p']))
    # Define the variables
    model.x = pyomo.Var(model.items,within=pyomo.Binary, bounds=(0,1))
    # Define the objective function
    model.obj = pyomo.Objective(expr=sum( model.p[i]*model.x[i] for i in model.items), sense=pyomo.maximize)
    # Add the constraint
    model.budgetCst = pyomo.Constraint ( expr=sum( model.c[i]*model.x[i] for i in model.items) <= model.B)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    # Print solution information to prompt
    print('Optimal objective function value =', pyomo.value(model.obj))
    print('Optimal values for the x-variables')
    xVal =[]
    for i in model.items:
        print('x[{}]={}'.format(i, pyomo.value(model.x[i])))

def main():
    data = readData('pathToTheDataFile')
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    main()
