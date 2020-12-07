'''
This class represents a constraint satisfaction problem. Thus, it has
functionality for adding, maintaining, and accessing variables and constraints.
'''

from Variable import *
from Constraint import *

class CSP:
    '''Class for packing up a set of variables into a CSP problem. The variables
    of the CSP can be added later or on initialization. The constraints must be
    added later'''

    def __init__(self, name, vars=[]):
        '''create a CSP object. Specify a name (a string) and optionally a set
        of variables'''

        self.name = name
        self.vars = []
        self.cons = []
        self.vars_to_cons = dict()
        for v in vars:
            self.add_var(v)

    def add_var(self,v):
        '''Add variable object to CSP while setting up an index to obtain the
        constraints over this variable'''
        if not type(v) is Variable:
            print("Trying to add non variable ", v, " to CSP object")
        elif v in self.vars_to_cons:
            print("Trying to add variable ", v, " to CSP object that already has it")
        else:
            self.vars.append(v)
            self.vars_to_cons[v] = []

    def add_constraint(self,c):
        '''Add constraint to CSP. Note that all variables in the
        constraints scope must already have been added to the CSP'''
        if not type(c) is Constraint:
            print("Trying to add non constraint ", c, " to CSP object")
        else:
            for v in c.scope:
                if not v in self.vars_to_cons:
                    print("Trying to add constraint ", c, " with unknown variables to CSP object")
                    return
                self.vars_to_cons[v].append(c)
            self.cons.append(c)

    def get_all_cons(self):
        '''return list of all constraints in the CSP'''
        return self.cons

    def get_cons_with_var(self, var):
        '''return list of constraints that include var in their scope'''
        return list(self.vars_to_cons[var])

    def get_all_vars(self):
        '''return list of variables in the CSP'''
        return list(self.vars)


    def print_soln(self):
        print("CSP", self.name, " Assignments = ")
        for v in self.vars:
            print(v, " = ", v.get_assigned_value(), "    ", end='')
        print("")
