#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.  

'''This file will contain different constraint propagators to be used within 
   bt_search.

A propagator is a function with the following template:
    propagator(csp, newly_instaniated_variable=None)
        ...
        returns (True/False, [(Variable, Value),(Variable,Value),...])
        
    csp is a CSP object, which the propagator can use to get access to
    the variables and constraints of the problem
    
    newly_instaniated_variable is an optional argument;
        if it is not None, then:
            newly_instaniated_variable is the most recently assigned variable
        else:
            the propagator was called before any assignment was made
    
    the prop returns True/False and a list of variable-value pairs;
        the former indicates whether a DWO did NOT occur,
        and the latter specifies each value that was pruned
     
The propagator SHOULD NOT prune a value that has already been pruned
or prune a value twice

In summary, this is what the propagator must do:

    If newly_instantiated_variable = None
      
        for plain backtracking;
            we do nothing...return true, []

        for forward checking;
            we check all unary constraints of the CSP
            
        for gac;
            we establish initial GAC by initializing the GAC queue
            with all constaints of the CSP


     If newly_instantiated_variable = a variable V
      
         for plain backtracking;
            we check all constraints with V that are fully assigned
            (use csp.get_cons_with_var)

         for forward checking;
            we check all constraints with V that have one unassigned variable

         for gac;
            we initialize the GAC queue with all constraints containing V
   '''

def prop_BT(csp, newVar=None):
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0: # for C in C: BOUND(C)
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals): # if VIOLATED(C)
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    if not newVar:
        # check all unary constraints of the CSP
        pruned = []
        for c in csp.get_all_cons():
            vars = c.get_scope()
            if len(vars) == 1: 
                # c is unary
                var = vars[0]
                for val in var.cur_domain():
                    # check all value in var's domain
                    if not c.check([val]):
                        # this val doesn't work; we prune
                        var.prune_value(val)
                        pruned.append([var, val])
                        if var.cur_domain_size() == 0:
                            # DWO!
                            return False, pruned
        # finsihed checking all constraints
        return True, pruned
    
    # check all constraints with V that have one unassigned variable
    pruned = []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 1: 
            # c is almost bound
            var = c.get_unasgn_vars()[0]
            for val in var.cur_domain():
                if not c.has_support(var, val):
                    var.prune_value(val)
                    pruned.append([var, val])
                    if var.cur_domain_size() == 0:
                        return False, pruned
    return True, pruned

def prop_GAC(csp, newVar=None):
    if not newVar:
        # establish initial GAC by initializing the GAC queue
        # with all constaints of the CSP
        pruned = []
        Q = []
        for all_con in csp.get_all_cons():
            Q.append(all_con)
        while Q:
            c = Q.pop(0)
            vars = c.get_scope()
            for var in vars:
                for val in var.cur_domain():
                    if not c.has_support(var, val):
                        var.prune_value(val)
                        pruned.append([var, val])
                        if var.cur_domain_size() == 0:
                            return False, pruned
                        else:
                            for new_c in csp.get_cons_with_var(var):
                                if new_c != c and new_c not in Q and var in new_c.get_scope():
                                    Q.append(new_c)
        return True, pruned
    # initialize the GAC queue with all constraints containing V
    pruned = []
    Q = []
    for c in csp.get_cons_with_var(newVar):
        Q.append(c)
    while Q:
        c = Q.pop(0)
        vars = c.get_scope()
        for var in vars:
            for val in var.cur_domain():
                if not c.has_support(var, val):
                    var.prune_value(val)
                    pruned.append([var, val])
                    if var.cur_domain_size() == 0:
                        return False, pruned
                    else:
                        for new_c in csp.get_cons_with_var(newVar):
                            if new_c != c and newVar in new_c.get_scope() and new_c not in Q:
                                Q.append(new_c)
    return True, pruned
