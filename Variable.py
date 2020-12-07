'''
This class represents a Variable in a CSP. Thus, a Variable can have a domain,
but if none is passed in during initialization, the domain is set to empty.
'''

class Variable:
    '''Class for defining CSP variables. On initialization the variable object
    should be given a name, and optionally a list of domain values.
    '''

    def __init__(self, name, domain=[]):
        '''Create a variable object, specifying its name (a string). Optionally
        specify the initial domain.
        '''
        self.name = name
        self.dom = list(domain)
        self.curdom = [True] * len(domain)
        self.assignedValue = None

    def domain(self):
        '''return the variable's (permanent) domain'''
        return(list(self.dom))

    def prune_value(self, value):
        '''Remove value from CURRENT domain'''
        self.curdom[self.value_index(value)] = False

    def unprune_value(self, value):
        '''Restore value to CURRENT domain'''
        self.curdom[self.value_index(value)] = True

    def cur_domain(self):
        '''Return list of values in CURRENT domain (if assigned only assigned
        value is viewed as being in current domain)'''
        vals = []
        if self.is_assigned():
            vals.append(self.get_assigned_value())
        else:
            for i, val in enumerate(self.dom):
                if self.curdom[i]:
                    vals.append(val)
        return vals

    def in_cur_domain(self, value):
        '''check if value is in CURRENT domain (without constructing list) if
        assigned only assigned value is viewed as being in current domain'''
        if not value in self.dom:
            return False
        if self.is_assigned():
            return value == self.get_assigned_value()
        else:
            return self.curdom[self.value_index(value)]

    def cur_domain_size(self):
        '''Return the size of the variables domain (without construcing list)'''
        if self.is_assigned():
            return 1
        else:
            return(sum(1 for v in self.curdom if v))

    def restore_curdom(self):
        '''return all values back into the current domain'''
        for i in range(len(self.curdom)):
            self.curdom[i] = True

    def is_assigned(self):
        return self.assignedValue != None

    def assign(self, value):
        '''When we assign we remove all other values values from curdom. We save
        this information so that we can reverse it on unassign'''

        if self.is_assigned() or not self.in_cur_domain(value):
            print("ERROR: trying to assign variable", self,
                  "that is already assigned or illegal value (not in curdom)")
            return

        self.assignedValue = value

    def unassign(self):
        '''Used by bt_search. Unassign and restore old current domain'''
        if not self.is_assigned():
            print("ERROR: trying to unassign variable", self, " not yet assigned")
            return
        self.assignedValue = None

    def get_assigned_value(self):
        '''return assigned value. Returns None if is unassigned'''
        return self.assignedValue

    def value_index(self, value):
        '''Domain values need not be numbers, so return the index
           in the domain list of a variable value'''
        return self.dom.index(value)

    def __repr__(self):
        return("Var-{}".format(self.name))

    def __str__(self):
        return("Var--{}".format(self.name))
