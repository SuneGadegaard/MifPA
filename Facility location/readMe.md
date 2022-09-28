# Facility location problems

This folder contains codes for solving discrete facility location problems in Python. For all the problems, Pyomo is used for modelling the problems 
as mixed integer linear proogramming (MILP) problems and then a solver is used for solving the models. In most examples, the solver `cbc`is used, but 
basically any MILP solver can be used (`glpk`, `cplex`, `gurobi` or any other).

All model files uses a structure with a `main()` function defined as
```
def main(instance_file_name):
    data = readData(instance_file_name)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    instance_file_name = 'theNameOfTheDataFile'
    main(instance_file_name)
```

In the `readData`-functions, the code in `readAndWriteJson.py` is used to read the data from a Json file. 
