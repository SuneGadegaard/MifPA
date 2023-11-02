# Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2023
# Author: Sune Lauth Gadegaard
# Implementation of a capacitated vehicle routing problem between n-customers nodes and a depot (labeled 0)
# The implementation uses a one commodity flow formulation akin to the model presented by Gavish and Graves in
# "THE TRAVELLING SALESMAN PROBLEM AND RELATED PROBLEMS" (1978).
# The IP solved is given by
# min   sum ( i in 0..n ) sum( j in 0..n) c[i][j]*x[i][j]
# s.t.  sum ( i in 0..n : i!=j ) x[i][j] == 1,                          for all j=1,..,n
#       sum ( j in 0..n : i!=j ) x[i][j] == 1,                          for all i=1,..,n
#       sum ( j in 1..n ) x[0][j] == m,
#       sum ( i in 1..n ) x[i][0] == m,
#       f[i][j] <= (Q-q[j])*x[i][j],                                    for all i,j=0,...,n
#       f[i][j] >= q[i]*x[i][j],                                        for all i,j=0,...,n
#       sum ( j in 0..n ) f[i][j] == sum ( j in 0..n ) f[j][i] + q[i],  for all i=1,...,n
#       x[i][j] in {0,1},                                               for all i,j in 0..n
#       f[i][j] >= 0,                                                   for all i,j in 0..n
# Here c[i][j] is the cost incurred by travelling directly from node i to node j.
# The binary x-variables indicates if a vehicle travels directly from i to j (x[i][j]=1) or not (x[i][j]=0).
# If x[i][j] == 1, then f[i][j] equals the amount of demand served on a route from the depot to and including
# node i, otherwise f[i][j] == 0.
# Q is the maximum number demand a vehicle can serve and q[i] is the demand a node i. By convention, q[0]=0.
# m is the number of vehicles available for dispatching.
# The readData(...) function uses the readAndWriteJson file to read data from a Json file

import pyomo.environ as pyomo  # Used to model the IP
import readAndWriteJson as rwJson  # Used for reading the data file in Json format
import matplotlib.pyplot as plt  # Used for plotting the result
import math  # Used for generating a distance matrix, if it is not present


def makeDistanceMatrix(data: dict) -> list:
    """ Function creating a distance matrix based on rounded euclidean distances between points in 2D
    Args:
        data (dict)
            Dictionary containing a list of x-coordinates named 'xCoord' and a list of y-coordinates named 'yCoord'
    Returns:
        dist (list)
            A list of lists where dist[i][j] gives the rounded euclidean distance between point i and point j
    """

    numNodes = len(data['xCoord'])
    dist = []
    for i in range(numNodes):
        dist.append([])
        for j in range(numNodes):
            tmpDist = (data['xCoord'][i] - data['xCoord'][j]) ** 2 + (data['yCoord'][i] - data['yCoord'][j]) ** 2
            dist[i].append(round(math.sqrt(tmpDist)))
    return dist


def readData(filename: str) -> dict:
    """ Reads a data file using the readAndWriteJson package
        Args:
            filename (str)
                String with relative/absolute path to a data fil for the CVRP. The data file must include the following entries:
                n = number of customers as an int
                m = number of vehicles as an int
                Q = capacity of the vehicles as an int
                q = list of demands of length n+1
                The data file must include either
                    xCoord = list of x-coordinates of length n+1
                    yCoord = list of y-coordinates of length n+1
                or
                    dist = list of lists containing a distance matrix of size (n+1) x (n+1).
                or both
        Returns:
            data (dict)
                Dictionary containing the data for the CVRP instance that should be solved
        """

    data = rwJson.readJsonFileToDictionary(filename)
    if 'dist' not in data:
        data['dist'] = makeDistanceMatrix(data)
        newFileName = filename + '_new'
        rwJson.saveDictToJsonFile(data, newFileName)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    """ Builds the Pyomo model for the CVRP and returns a ConcreteModel object
    Args:
        data (dict)
            Dictionary containing the data for the CVRP instance that should be solved
    Returns:
        model (ConcreteModel object)
            ConcreteModel (in the Pyomo sense) containing a model for the CVRP
    """

    model = pyomo.ConcreteModel()  # Create a model object
    model.numOfNodes = data['n'] + 1  # Number of nodes in the problem (number of customers (n) + 1 for the depot)
    model.nodes = range(0, model.numOfNodes)  # Range over all nodes: 0,1,2,3,...,n
    model.customers = range(1, model.numOfNodes)  # Range over all customer nodes: 1,2,3,...,n
    model.x = pyomo.Var(model.nodes, model.nodes, within=pyomo.Binary)  # Binary x-variables.
    model.f = pyomo.Var(model.nodes, model.nodes, within=pyomo.NonNegativeReals, bounds=(0, data['Q']))  # Continuous f-variables
    # Remove the diagonal of the x-variable matrix
    for i in model.nodes:
        model.x[i, i].fix(0)
        model.f[i, i].fix(0)
    # Add the objective function minimizing the total costs/distance
    model.obj = pyomo.Objective(
        expr=sum(data['dist'][i][j] * model.x[i, j] for i in model.nodes for j in model.nodes if i != j),
        sense=pyomo.minimize
    )
    # Add in- and out-degree constraints for all the customers
    model.sumToOne = pyomo.ConstraintList()
    for i in model.customers:
        # Out of node i
        model.sumToOne.add(expr=sum(model.x[i, j] for j in model.nodes if i != j) == 1)
        # Into node i
        model.sumToOne.add(expr=sum(model.x[j, i] for j in model.nodes if i != j) == 1)
    # Add in- and out-degree constraints for the depot
    model.depotOut = pyomo.Constraint(expr=sum(model.x[0, j] for j in model.nodes) == data['m'])
    model.depotIn = pyomo.Constraint(expr=sum(model.x[i, 0] for i in model.nodes) == data['m'])
    # Add the constraints f[i,j]<=(Q-q[j])*x[i,j] and f[i,j]>=q[i]*x[i,j] for all pairs of nodes i and j
    model.GeneralizedBounds = pyomo.ConstraintList()
    for i in model.nodes:
        for j in model.nodes:
            model.GeneralizedBounds.add(expr=model.f[i, j] <= (data['Q']-data['q'][j])*model.x[i, j])
            model.GeneralizedBounds.add(expr=model.f[i, j] >= data['q'][i]*model.x[i, j])
    # Add the flow conservation constraints
    # sum(f[i,j] for j in nodes) == sum(f[j,i] for j in nodes) + q[i] for all customers
    model.flowConservation = pyomo.ConstraintList()
    for i in model.customers:
        model.flowConservation.add(
            expr=sum(model.f[i, j] for j in model.nodes) == sum(model.f[j, i] for j in model.nodes) + data['q'][i]
        )
    # Return the model object
    return model


def solveModel(model: pyomo.ConcreteModel()):
    """ Solve the model contained in the parsed ConcreteModel object
    Args:
        model (ConcreteModel object)
            ConcreteModel object (in the Pyomo sense) containing a full model for the CVRP
    """

    solver = pyomo.SolverFactory('cplex')
    solver.solve(model, tee=True)


def displaySolution(model: pyomo.ConcreteModel(), data: dict):
    """Solve the model contained in the parsed ConcreteModel object
    Args:
        model (ConcreteModel object)
            ConcreteModel object (in the Pyomo sense) containing a full model for the CVRP
        data (dict)
            Dictionary containing the data defining the CVRP instance solved
    """

    # Print total length of tours
    print('Total length of tours:', pyomo.value(model.obj))
    # Find a tour for each vehicle
    lastRouteStarter = 0
    coordinatesPresent = 'xCoord' in data and 'yCoord' in data  # Create a boolean flag that signals coordinates
    for vehicle in range(1, data['m'] + 1):  # Loop through all vehicles and construct a tour for each
        print('Bil nummer', vehicle, "printes nu")
        if coordinatesPresent:  # If data file contains coordinates, then initialize a list with the depot coordinates
            displayX = [data['xCoord'][0]]
            displayY = [data['yCoord'][0]]
            labels = [0]
        # Find the customer, that starts the next route
        currentNode = 0
        for j in model.customers:  # Loop through all the customer nodes
            if j > lastRouteStarter and pyomo.value(
                    model.x[0, j]) >= 0.9999:  # If j starts new route, record j in currentNode
                currentNode = j
                if coordinatesPresent:
                    displayX.append(data['xCoord'][currentNode])
                    displayY.append(data['yCoord'][currentNode])
                    labels.append(currentNode)
                break
        lastRouteStarter = currentNode
        print('The route for vehicle', vehicle, 'is:')
        print('0->', currentNode, end='')
        # Build the route from currenNode back to the depot
        while currentNode != 0:
            for j in model.nodes:
                if currentNode != j and pyomo.value(model.x[currentNode, j]) >= 0.9999:
                    print('->', j, end='')
                    currentNode = j
                    if coordinatesPresent:
                        displayX.append(data['xCoord'][currentNode])
                        displayY.append(data['yCoord'][currentNode])
                        labels.append(currentNode)
                    break
        print('\n')
        if coordinatesPresent:
            # Start plotting the solution to a coordinate system
            if coordinatesPresent:
                plt.plot(displayX, displayY, '-o')
                for i, label in enumerate(labels):
                    plt.annotate(label, (displayX[i], displayY[i]))
    plt.show()


def main(filename: str):
    """ Simple main function implementing the logic: read data -> build model -> solve model -> display the solution
    Args:
        filename (str)
            String specifying the relative/absolute path to a data file for an CVRP
    """

    data = readData(filename)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model, data)
    print('Objective value: ' + str(pyomo.value(model.obj)))


if __name__ == '__main__':
    main('CVRP_data/cvrpDataFile_n_5.json')
