#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = warehouse_binary_ne_grid(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the warehouse.

The grid-only models do not need to encode the cage constraints.

1. warehouse_binary_ne_grid
    - A model of the warehouse problem w/o room constraints built using only 
      binary not-equal constraints for the row/column constraints.

2. warehouse_nary_ad_grid
    - A model of the warehouse problem w/o room constraints built using only n-ary 
      all-different constraints for the row/column constraints. 

3. warehouse_full_model
    - A model of the warehouse problem built using either the binary not-equal or n-ary
      all-different constraints for the row/column constraints.
'''
from cspbase import *
import itertools

def sudoku(grid):
    N = 9
    dom_V = range(1, N + 1)
    var_array = []
    csp = CSP("Sudoku_CSP")
    tuples = list(itertools.permutations(range(1, N + 1), 2))
    blocks = [[] for x in range(N)]
    for Y in range(1, N+1):
        ver_pos = (Y-1) // 3
        row = []
        for X in range(1, N+1):
            hor_pos = (X-1) // 3
            block_num = ver_pos * 3 + hor_pos
            var = Variable(str(Y) + str(X), dom_V)
            if grid[Y-1][X-1] in dom_V:
                var.assign(grid[Y-1][X-1])
            row.append(var)
            csp.add_var(var)
            blocks[block_num].append(var)
        var_array.append(row)

    for i1 in range(N):
        for j1 in range(N):
            var1 = var_array[i1][j1]
            for j2 in range(j1 + 1, N):
                var2 = var_array[i1][j2] #var2 is on the right of var1
                con = Constraint("R{}_{}{}".format(i1 + 1, j1 + 1, j2+ 1), [var1, var2])
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
            for i2 in range(i1 + 1, N):
                var2 = var_array[i2][j1] #var2 is on the bottom of var1
                con = Constraint("C{}_{}{}".format(j1 + 1, i1 + 1, i2+ 1), [var1, var2])
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
            ver_pos_in_block = i1 % 3
            hor_pos_in_block = j1 % 3
            if ver_pos_in_block == 2:
                continue
            if hor_pos_in_block == 0:
                indices_not_in_col = [j1 + 1, j1 + 2]
            elif hor_pos_in_block == 1:
                indices_not_in_col = [j1 + 1, j1 - 1]
            else:
                indices_not_in_col = [j1 - 1, j1 - 2]
            if ver_pos_in_block < 2:
                var3 = var_array[i1 + 1][indices_not_in_col[0]]
                var4 = var_array[i1 + 1][indices_not_in_col[1]]
                block_con1 = Constraint("B{}{}_{}{}_{}{}".format(i1//3, j1//3, i1, j1, i1+1, indices_not_in_col[0]), [var1, var3])
                block_con2 = Constraint("B{}{}_{}{}_{}{}".format(i1//3, j1//3, i1, j1, i1+1, indices_not_in_col[1]), [var1, var4])
                block_con1.add_satisfying_tuples(tuples)
                block_con2.add_satisfying_tuples(tuples)
                csp.add_constraint(block_con1)
                csp.add_constraint(block_con2)
            if ver_pos_in_block == 0:
                var3 = var_array[i1 + 2][indices_not_in_col[0]]
                var4 = var_array[i1 + 2][indices_not_in_col[1]]
                block_con1 = Constraint("B{}{}_{}{}_{}{}".format(i1//3, j1//3, i1, j1, i1+2, indices_not_in_col[0]), [var1, var3])
                block_con2 = Constraint("B{}{}_{}{}_{}{}".format(i1//3, j1//3, i1, j1, i1+2, indices_not_in_col[1]), [var1, var4])
                block_con1.add_satisfying_tuples(tuples)
                block_con2.add_satisfying_tuples(tuples)
                csp.add_constraint(block_con1)
                csp.add_constraint(block_con2)
    return csp, var_array
