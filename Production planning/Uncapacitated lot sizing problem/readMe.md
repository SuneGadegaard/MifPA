Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022 

Implementation of an uncapacitated lot sizing problem where a production plan over T periods has to obtimized. 
For each period $t$ in {$1,..,T$} there is a unit production cost, a fixed cost for starting production, and a unit cost for putting
products in the inventory ($p_t$, $q_t$, and $h_t$, respectively). In addition, there is known demand in each period denoted by $d_t$.
The IP solved is given by

$$
  \\begin{align}
    \min        \ & \sum_{t=1}^T (p_tx_t+q_ty_t+h_ts_t)\\
    \text{s.t.:}\ & s_{t-1} + x_t = d_t + s_t,&&\forall t=1,\dots, T\\
                \ & x_t\leq My_t,&&\forall t=1,\dots,T\\
                \ & x_t, s_t\in\mathbb{Z}^{T},&&\forall t=1,\dots,T\\
                \ & y_t\text{ binary for all }t
  \\end{align}
$$


Here $x_t$ denotes the number of units produced in periode $t$, $y_t=1$ if $x_t>0$, and $s_t$ denotes the number of products in inventory ultimo period $t$.
Upper and lower bounds on the production and the inventory level may be set as wel (it is in the example in this folder).

The readData(...) function uses the readAndWriteJson file to read data from a Json file in the form

```
"periods": [list of strings with names for the periods]
"demands": [list of demands for each period]
"var_cost": [list of unit production costs]
"fixed_cost": [list of fixed costs associated with starting production in each period]
"inv_cost": [unit inventory cost for each period]
"max_prod": number indicating the maximum number of units that can be produced in each period
"max_inv": number indicating the maximum number of units that can be in inventory in each period
```
