import pyomo.environ as pyomo
import readAndWriteJson as rwJson
import matplotlib.pyplot as plt
import numpy as np


def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Define model object
    model = pyomo.ConcreteModel()
    # Copy data to model object
    model.period_labels = data['periods']
    model.periods = range(0, len(model.period_labels))
    model.periods_and_zero = range(-1, len(model.period_labels))
    model.demands = data['demands']
    model.p = data['var_cost']
    model.q = data['fixed_cost']
    model.h = data['inv_cost']
    model.bigM = sum(model.demands)
    # Add variables to the model
    model.x = pyomo.Var(model.periods, within=pyomo.NonNegativeIntegers, bounds=(0, data['max_prod']))
    model.y = pyomo.Var(model.periods, within=pyomo.Binary)
    model.s = pyomo.Var(model.periods_and_zero, within=pyomo.NonNegativeIntegers,bounds=(0, data['max_inv']))
    # Add objective function
    model.obj = pyomo.Objective(
        expr=sum( (model.p[t]*model.x[t] + model.q[t]*model.y[t] + model.h[t]*model.s[t]) for t in model.periods )
    )
    # Add flow conservation constraints
    model.flow = pyomo.ConstraintList()
    for t in model.periods:
        model.flow.add(expr=model.s[t-1] + model.x[t] == model.s[t] + model.demands[t])
    # Add x[t] <= M*y[t] constraints
    model.indicators = pyomo.ConstraintList()
    for t in model.periods:
        model.indicators.add(expr=model.x[t] <= model.bigM*model.y[t])
    # Set starting inventory to zero
    model.s[-1].setub(0)
    return model




def solveModel(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory('cbc')
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    print('Optimal cost is:', pyomo.value(model.obj))
    fig = plt.figure()
    # Number of periods - used to control placement on the x-axis
    numPeriods = len(model.period_labels)
    # Position of bars on x-axis
    pos = np.arange(numPeriods)
    # Extract the optimal variable values
    s_values = [pyomo.value(model.s[t]) for t in model.periods]
    x_values = [pyomo.value(model.x[t]) for t in model.periods]
    # Width of a bar
    width = 0.4
    # Add the three plots to the fig-figure
    plt.bar(pos, model.demands, width, label='Demands',color='blue')
    plt.bar(pos + width, s_values, width, label='Inventory level',color='grey')
    plt.plot ( pos, x_values, color='darkred', label='Production level')
    # Set the ticks on the x-axis
    plt.xticks(pos + width / 2, model.period_labels)
    # Labels on axis
    plt.xlabel('Periods to plan')
    plt.ylabel('Demand')
    plt.title('Optimal production plan. Optimal cost is: ' + str(pyomo.value(model.obj)))
    # Show the figure
    plt.show()


def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    filename = 'ulsDataFile'
    print(filename)
    main(filename)