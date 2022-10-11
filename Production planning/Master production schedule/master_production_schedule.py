import pyomo.environ as pyomo
import readAndWriteJson as rwJson
import matplotlib.pyplot as plt
import numpy as np


def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    model = pyomo.ConcreteModel()
    model.period_labels = data['periods']
    model.product_names = data['products']
    model.periods = range(0, len(model.period_labels))
    model.products = range(0, len(model.product_names))
    model.periods_and_zero = range(-1, len(model.period_labels))
    model.demands = data['demands']
    model.p = data['var_cost']
    model.q = data['fixed_cost']
    model.h = data['inv_cost']
    model.batch = data['batch_size']
    model.bigM = [sum(model.demands[k])/model.batch for k in model.products]
    # Add variables to the model
    model.x = pyomo.Var(model.products, model.periods, within=pyomo.NonNegativeIntegers)
    model.y = pyomo.Var(model.products, model.periods, within=pyomo.Binary)
    model.s = pyomo.Var(model.products, model.periods_and_zero, within=pyomo.NonNegativeIntegers)
    # Add objective function
    model.obj = pyomo.Objective(
        expr=sum(model.p[k][t]*model.batch* model.x[k, t] + model.q[k][t] * model.y[k, t] + model.h[t] * model.s[k, t]
                 for t in model.periods for k in model.products)
    )
    # Add flow conservation constraints
    model.flow = pyomo.ConstraintList()
    for t in model.periods:
        for k in model.products:
            model.flow.add(expr=model.s[k, t-1] + model.batch*model.x[k, t] == model.demands[k][t] + model.s[k, t])
    # Add the indicator constraints
    model.indicators = pyomo.ConstraintList()
    for t in model.periods:
        for k in model.products:
            model.indicators.add(expr=model.x[k, t] <= model.bigM[k]*model.y[k, t])
    # Set max size on production and inventory (in one go)
    model.sharedResources = pyomo.ConstraintList()
    for t in model.periods:
        model.sharedResources.add(expr=sum(model.batch*model.x[k, t] for k in model.products) <= data['max_prod'])
        model.sharedResources.add(expr=sum(model.s[k, t] for k in model.products) <= data['max_inv'])
    model.s[0, -1].setub(0)
    model.s[1, -1].setub(0)
    return model


def solveModel(model: pyomo.ConcreteModel()):
    solver = pyomo.SolverFactory('cbc')
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel()):
    print('Optimal cost is:', pyomo.value(model.obj))
    # Number of periods - used to control placement on the x-axis
    numPeriods = len(model.period_labels)
    # Position of bars on x-axis
    pos = np.arange(numPeriods)



    plt.figure(1)
    # For each product, plot the production plan
    for k in model.products:
        plt.subplot(3, 1, k+1)
        # Extract the optimal variable values
        s_values = [pyomo.value(model.s[k,t]) for t in model.periods]
        x_values = [model.batch*pyomo.value(model.x[k,t]) for t in model.periods]
        # Width of a bar
        width = 0.4
        # Add the three plots to the fig-figure
        plt.bar(pos, model.demands[k], width, label='Demands', color='blue')
        plt.bar(pos + width, s_values, width, label='Inventory level', color='grey')
        plt.plot(pos, x_values, color='darkred', label='Production level')
        # Set the ticks on the x-axis
        plt.xticks(pos + width / 2, model.period_labels)
        # Labels on axis
        plt.xlabel('Periods to plan')
        plt.ylabel('Demand')
        plt.legend()

    # Plot the aggregate production plan
    plt.subplot(3, 1, 3)
    # Extract the optimal variable values
    s_values = [sum(pyomo.value(model.s[k, t]) for k in model.products) for t in model.periods]
    x_values = [sum(model.batch * pyomo.value(model.x[k, t]) for k in model.products ) for t in model.periods]
    d_values = [sum(model.demands[k][t] for k in model.products ) for t in model.periods]
    # Width of a bar
    width = 0.4
    # Add the three plots to the fig-figure
    plt.bar(pos, d_values, width, label='Demands', color='blue')
    plt.bar(pos + width, s_values, width, label='Inventory level', color='grey')
    plt.plot(pos, x_values, color='darkred', label='Production level')
    # Set the ticks on the x-axis
    plt.xticks(pos + width / 2, model.period_labels)
    # Labels on axis
    plt.xlabel('Periods to plan')
    plt.ylabel('Demand')
    plt.legend()


    # Show the figure
    plt.show()


def main(filename: str):
    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    filename = 'mpsDataFile'
    main(filename)
