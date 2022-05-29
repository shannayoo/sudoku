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

def warehouse_binary_ne_grid(warehouse_grid):
    N = warehouse_grid[0][0]
    dom_V = range(1, N + 1)
    var_array = []
    csp = CSP("Warehouse_CSP_Binary")
    tuples = list(itertools.permutations(range(1, N + 1), 2))

    for Y in range(N, 0, -1):
        row = []
        for X in range(1, N + 1):
            var = Variable(str(X) + str(Y), dom_V)
            row.append(var)
            csp.add_var(var)
        var_array.append(row)

    for i1 in range(N):
        for j1 in range(N):
            var1 = var_array[i1][j1]
            for j2 in range(j1 + 1, N):
                var2 = var_array[i1][j2] #var2 is on the right of var1
                con = Constraint("R{}_{}{}".format(N - i1, j1 + 1, j2+ 1), [var1, var2])
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
            for i2 in range(i1 + 1, N):
                var2 = var_array[i2][j1] #var2 is on the bottom of var1
                con = Constraint("C{}_{}{}".format(j1 + 1, i1 + 1, i2+ 1), [var1, var2])
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)

    return csp, var_array
    

def warehouse_nary_ad_grid(warehouse_grid):
    N = warehouse_grid[0][0]
    dom_V = range(1, N + 1)
    csp = CSP("Warehouse_CSP_N_ary")
    var_array = []
    permutations = list(itertools.permutations(dom_V))
    for Y in range(N, 0, -1):
        row = []
        for X in range(1, N + 1):
            var = Variable(str(X) + str(Y), dom_V)
            row.append(var)
            csp.add_var(var)
        var_array.append(row)
        row_con = Constraint("R{}".format(Y), row)
        row_con.add_satisfying_tuples(permutations)
        csp.add_constraint(row_con)
    for X in range(N):
        col = []
        for Y in reversed(range(N)):
            col.append(var_array[Y][X])
        col_con = Constraint("C{}".format(X + 1), col)
        col_con.add_satisfying_tuples(permutations)
        csp.add_constraint(col_con)

    return csp, var_array

def warehouse_full_model(warehouse_grid):
    N = warehouse_grid[0][0]
    dom_V = range(1, N + 1)
    var_array = [[0]*N for i in range(N)]
    csp = CSP("Warehouse_CSP_Binary")
    tuples = list(itertools.permutations(range(1, N + 1), 2))

    for i in range(1, len(warehouse_grid)):
        building = warehouse_grid[i]
        op = building[len(building) - 2]
        tg = building[len(building) - 1]
        rooms = []
        for j in range(len(building) - 2):
            room_rep = building[j]
            x, y = room_rep // 10, room_rep % 10
            if (var_array[N - y][x - 1]) == 0:
                var = Variable("{}".format(str(room_rep)), dom_V)
                var_array[N - y][x - 1] = var
                csp.add_var(var)
                rooms.append(var)
        if op == 0: # equals constraint
            eq_con = Constraint("R{}_eq".format((rooms[0]).name), rooms)
            eq_con.add_satisfying_tuples([[tg]])
            csp.add_constraint(eq_con)
        elif op == 2: # min constraint
            tuples = []
            for k in range(tg, N + 1):
                tuples.append([k])
            for room in rooms:
                min_con = Constraint("R{}_min".format(str(room.name)), [room])
                min_con.add_satisfying_tuples(tuples)
                csp.add_constraint(min_con)
        elif op == 3: # maximum constraint
            tuples = []
            for k in range(1, tg+1):
                tuples.append([k])
            for room in rooms:
                max_con = Constraint("R{}_max".format(str(room.name)), [room])
                max_con.add_satisfying_tuples(tuples)
                csp.add_constraint(max_con)

    for i in range(1, len(warehouse_grid)):
        building = warehouse_grid[i]
        op = building[len(building) - 2]
        tg = building[len(building) - 1]
        rooms = []            
        if op == 1: # addition constraint
            add_con = Constraint("B{}_add".format(str(i)), rooms)
            tuples = []
            perms = itertools.permutations(list(range(1, N+1)) * int((len(rooms)) ** (1/2)), len(rooms))
            for perm in perms:
                if sum(perm) == tg:
                    tuples.append(perm)
            add_con.add_satisfying_tuples(tuples)
            csp.add_constraint(add_con)

    perms = list(itertools.permutations(range(1, N + 1), 2))
    for i1 in range(N):
        for j1 in range(N):
            var1 = var_array[i1][j1]
            for j2 in range(j1 + 1, N):
                var2 = var_array[i1][j2] #var2 is on the right of var1
                con = Constraint("R{}_{}{}".format(N - i1, j1 + 1, j2+ 1), [var1, var2])
                con.add_satisfying_tuples(perms)
                csp.add_constraint(con)
            for i2 in range(i1 + 1, N):
                var2 = var_array[i2][j1] #var2 is on the bottom of var1
                con = Constraint("C{}_{}{}".format(j1 + 1, i1 + 1, i2+ 1), [var1, var2])
                con.add_satisfying_tuples(perms)
                csp.add_constraint(con)
    
    return csp, var_array

# def warehouse_full_model(warehouse_grid):
#     N = warehouse_grid[0][0]
#     dom_V = range(1, N + 1)
#     var_array = [[0]*N for i in range(N)]
#     csp = CSP("Warehouse_CSP_Binary")
#     permutations = list(itertools.permutations(dom_V))

#     for i in range(1, len(warehouse_grid)):
#         building = warehouse_grid[i]
#         op = building[len(building) - 2]
#         tg = building[len(building) - 1]
#         rooms = []
#         for j in range(len(building) - 2):
#             room_rep = building[j]
#             x, y = room_rep // 10, room_rep % 10
#             if (var_array[N - y][x - 1]) == 0:
#                 var = Variable("{}".format(str(room_rep)), dom_V)
#                 var_array[N - y][x - 1] = var
#                 csp.add_var(var)
#                 rooms.append(var)
#         if op == 0: # equals constraint
#             eq_con = Constraint("R{}_eq".format((rooms[0]).name), rooms)
#             eq_con.add_satisfying_tuples([[tg]])
#             csp.add_constraint(eq_con)
#         elif op == 2: # min constraint
#             tuples = []
#             for k in range(tg, N + 1):
#                 tuples.append([k])
#             for room in rooms:
#                 min_con = Constraint("R{}_min".format(str(room.name)), [room])
#                 min_con.add_satisfying_tuples(tuples)
#                 csp.add_constraint(min_con)
#         elif op == 3: # maximum constraint
#             tuples = []
#             for k in range(1, tg+1):
#                 tuples.append([k])
#             for room in rooms:
#                 max_con = Constraint("R{}_max".format(str(room.name)), [room])
#                 max_con.add_satisfying_tuples(tuples)
#                 csp.add_constraint(max_con)
#         else: # addition constraint
#             add_con = Constraint("B{}_add".format(str(i)), rooms)
#             tuples = []
#             perms = itertools.permutations(list(range(1, N+1)) * int((len(rooms)) ** (1/2)), len(rooms))
#             for perm in perms:
#                 if sum(perm) == tg:
#                     tuples.append(perm)
#             add_con.add_satisfying_tuples(tuples)
#             csp.add_constraint(add_con)

#     for i1 in range(N):
#         row_con = Constraint("R{}".format(N - i1), var_array[i1])
#         row_con.add_satisfying_tuples(permutations)
#         csp.add_constraint(row_con)
#         col = []
#         for j1 in range(N):
#             col.append(var_array[j1][i1])
#         col_con = Constraint("C{}".format(i1 + 1), col)
#         col_con.add_satisfying_tuples(permutations)
#         csp.add_constraint(col_con)

#     return csp, var_array