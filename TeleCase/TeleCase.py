# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022
# Implementation og the "Tele Case" from the mini-cases document produced by Lars Relunds Nielsen and
# SUne Lauth Gadegaard for the "Operations Management" course also at Aarhus University.
# The LP solved is given by
# max   20*x1 + 10*x2
# s.t.:    x1 +    x2 <= 120
#          x1 +    x2 <= 90
#          x1         <= 70
#                  x2 <= 50
#          x1,     x2 >= 0
# The readData(...) functions has an argument for a file name. This is not used in this simple example! The data
# is simply hard coded in readData(...)
import pyomo.environ as pyomo


def readData(filename: str) -> dict:
    # implementation of function
    data = dict()
    data['c'] = [20, 10]
    data['A'] = [[1, 2], [1, 1]]
    data['b'] = [120, 90]
    data['boundX1'] = 70
    data['boundX2'] = 50
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Create the model object
    model = pyomo.ConcreteModel()
    # Copy the data to the model object
    model.c = data['c']
    model.A = data['A']
    model.b = data['b']
    model.boundX1 = data['boundX1']
    model.boundX2 = data['boundX2']
    # Define the variables
    model.x1 = pyomo.Var(within=pyomo.NonNegativeReals, bounds=(0,model.boundX1))
    model.x2 = pyomo.Var(within=pyomo.NonNegativeReals, bounds=(0,model.boundX2))
    # Define the objective function
    model.obj = pyomo.Objective(expr=model.c[0]*model.x1 + model.c[1]*model.x2, sense=pyomo.maximize)
    # Add the constraints
    model.cst1 = pyomo.Constraint(expr=model.A[0][0]*model.x1 + model.A[0][1]*model.x2 <= model.b[0])
    model.cst2 = pyomo.Constraint(expr=model.A[1][0]*model.x1 + model.A[1][1]*model.x2 <= model.b[1])
    return model


def solveModel(model: pyomo.ConcreteModel()):
    # Set the solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    # Print solution information to prompt
    print("Optimal objective function value =", pyomo.value(model.obj))
    print("Optimal value for x1 =", pyomo.value(model.x1))
    print("Optimal value for x2 =", pyomo.value(model.x2))
    print("Slack for cst1",model.cst1.uslack())
    print("Slack for cst2", model.cst2.uslack())

def main():
    data = readData('pathToTheDataFile')
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    main()
