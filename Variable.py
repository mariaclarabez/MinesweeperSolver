class Variable:

    '''Class for defining CSP variables.  On initialization the
       variable object should be given a name, and optionally a list of
       domain values. Later on more domain values an be added...but
       domain values can never be removed.

       The variable object offers two types of functionality to support
       search.
       (a) It has a current domain, implimented as a set of flags
           determining which domain values are "current", i.e., unpruned.
           - you can prune a value, and restore it.
           - you can obtain a list of values in the current domain, or count
             how many are still there

       (b) You can assign and unassign a value to the variable.
           The assigned value must be from the variable domain, and
           you cannot assign to an already assigned variable.

           You can get the assigned value e.g., to find the solution after
           search.

           Assignments and current domain interact at the external interface
           level. Assignments do not affect the internal state of the current domain
           so as not to interact with value pruning and restoring during search.

           But conceptually when a variable is assigned it only has
           the assigned value in its current domain (viewing it this
           way makes implementing the propagators easier). Hence, when
           the variable is assigned, the 'cur_domain' returns the
           assigned value as the sole member of the current domain,
           and 'in_cur_domain' returns True only for the assigned
           value. However, the internal state of the current domain
           flags are not changed so that pruning and unpruning can
           work independently of assignment and unassignment.
           '''
    #
    #set up and info methods
    #
    def __init__(self, name, domain=[]):
        '''Create a variable object, specifying its name (a
        string). Optionally specify the initial domain.
        '''
        self.name = name                #text name for variable
        self.dom = list(domain)         #Make a copy of passed domain
        self.curdom = [True] * len(domain)      #using list
        #for bt_search
        self.assignedValue = None

    def domain(self):
        '''return the variable's (permanent) domain'''
        return(list(self.dom))

    #
    #methods for current domain (pruning and unpruning)
    #

    def prune_value(self, value):
        '''Remove value from CURRENT domain'''
        self.curdom[self.value_index(value)] = False

    def unprune_value(self, value):
        '''Restore value to CURRENT domain'''
        self.curdom[self.value_index(value)] = True

    def cur_domain(self):
        '''return list of values in CURRENT domain (if assigned
           only assigned value is viewed as being in current domain)'''
        vals = []
        if self.is_assigned():
            vals.append(self.get_assigned_value())
        else:
            for i, val in enumerate(self.dom):
                if self.curdom[i]:
                    vals.append(val)
        return vals

    def in_cur_domain(self, value):
        '''check if value is in CURRENT domain (without constructing list)
           if assigned only assigned value is viewed as being in current
           domain'''
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
        '''return all values back into CURRENT domain'''
        for i in range(len(self.curdom)):
            self.curdom[i] = True

    #
    #methods for assigning and unassigning
    #

    def is_assigned(self):
        return self.assignedValue != None

    def assign(self, value):
        '''Used by bt_search. When we assign we remove all other values
           values from curdom. We save this information so that we can
           reverse it on unassign'''

        if self.is_assigned() or not self.in_cur_domain(value):
            print("ERROR: trying to assign variable", self,
                  "that is already assigned or illegal value (not in curdom)")
            return

        self.assignedValue = value

    def unassign(self):
        '''Used by bt_search. Unassign and restore old curdom'''
        if not self.is_assigned():
            print("ERROR: trying to unassign variable", self, " not yet assigned")
            return
        self.assignedValue = None

    def get_assigned_value(self):
        '''return assigned value...returns None if is unassigned'''
        return self.assignedValue

    #
    #internal methods
    #

    def value_index(self, value):
        '''Domain values need not be numbers, so return the index
           in the domain list of a variable value'''
        return self.dom.index(value)

    def __repr__(self):
        return("Var-{}".format(self.name))

    def __str__(self):
        return("Var--{}".format(self.name))
