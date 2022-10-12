Pyomo example for the course "Modellering inden for Prescriptive Analytics" at Aarhus University, Fall 2022 

Implementation of an master production scheduling problem where a production plan over T periods has to obtimized for $k=1,\dots,K$ products. 
For each period $t$ in $1,..,T$ there is a unit production cost per product $k$, a fixed cost for starting production for each produckt $k$, 
and a unit cost for putting product $k$ in the inventory ( $p_t^k$, $q_t^k$, and $h_t^k$, respectively).
In this example, there shared resources in the number of products that can be produced per day, and there is a shared resource in the inventory
capacity. The max production per day is denoted $P^{\max}$ and the inventory capacity is denoted $I^{\max}$. In this example, production of product
$k$ is made in baches of size $B^k > 0$.

In addition, there is known demand in each period and each product denoted by $d_t^k$.

The IP solved is given by

$$
  \\begin{align}
    \min        \ & \sum_{t=1}^T \sum_{k=1}^K (p_t^kB^kx_t^k + q_t^ky^k_t+h^k_ts^k_t)\\
    \text{s.t.:}\ & s_{t-1}^k + B^kx_t^k = d_t^k + s_t^k,  &&\forall t=1,\dots, T, k=1,\dots,K\\
                \ & x_t^k\leq My_t^k,&&\forall t=1,\dots,T, k=1,\dots,K\\
                \ & \sum_{k=1}^K B^kx_t^k \leq P^{\max}, && \forall t=1,\dots,T\\
                \ & \sum_{k=1}^K s_t^k \leq I^{\max}, && \forall t=1,\dots,T\\
                \ & x_t^k, s_t^k\in\mathbb{Z}^{T},&&\forall t=1,\dots,T,k=1,\dots,K\\
                \ & y_t^k\text{ binary }    &&\forall t=1,\dots,T, k=1,\dots,K
  \\end{align}
$$


Here $x_t^k$ denotes the number of batches produced in periode $t$ of product $k$, $y_t^k=1$ if $x_t^k>0$, and $s_t^k$ denotes the number of products 
in inventory ultimo period $t$ of product $k$.
The idea of having shared resources can be generalized by introducing $I$ shared ressources, index by $i=1,\dots,I$. For each combination of product $k$ and resource $i$, three additional parameters are needed: $\alpha^{ik}$ is the amount of ressource $i$ used when producing one batch of product $k$, $\beta^{ik}$ is the amount of resource $i$ consumed when starting the production of product $k$, and $\gamma^{ik}$ is the amount of resource $i$ used when one unit of product $k$ is put in inventory. Finally, the amount of resource $i$ available at time $t$ is denoted $L^i_t$. The production and inventory capacities can then be generalized by the constraints

$$
\begin{equation}
  \sum_{k=1}^K \left( \alpha^{ik}x_t^k + \beta^{ik}y_t^k + \gamma^{ik}s_t^k \right)\leq L^i_k\quad \forall i=1,\dots,I, t=1,\dots,T
\end{equation}
$$

The readData(...) function uses the readAndWriteJson.py` file to read data from a Json file in the form

```
"products": [list of names for each product],
"periods": [list of strings with names for the periods]
"demands": [list of lists of demands for each period and each product. d[k][t] is the demand for product k in period t]
"var_cost": [list of lists of per batch production costs. var_cost[k][t] is the batch production costs for product k in period t]
"fixed_cost": [list of lists of fixed costs associated with starting production in each period. fixed_cost[k][t] is fixed cost for product k in period t]
"inv_cost": [unit inventory cost for each period. Note, does not depend on product in this example]
"max_prod": number indicating the maximum number of units that can be produced in each period
"max_inv": number indicating the maximum number of units that can be in inventory in each period
"batch_size" : number indicating the batch size of product k. Note, that it does not depend on the product in this small example
```
