import time

'''Constraint Satisfaction Routines
   A) class Variable

      This class allows one to define CSP variables.

      On initialization the variable object can be given a name, and
      an original domain of values. This list of domain values can be
      added but NOT deleted from.

      To support constraint propagation, the class also maintains a
      set of flags to indicate if a value is still in its current domain.
      So one can remove values, add them back, and query if they are
      still current.

    B) class constraint

      This class allows one to define constraints specified by tables
      of satisfying assignments.

      On initialization the variables the constraint is over is
      specified (i.e. the scope of the constraint). This must be an
      ORDERED list of variables. This list of variables cannot be
      changed once the constraint object is created.

      Once initialized the constraint can be incrementally initialized
      with a list of satisfying tuples. Each tuple specifies a value
      for each variable in the constraint (in the same ORDER as the
      variables of the constraint were specified).

    C) Backtracking routine---takes propagator and CSP as arguments
       so that basic backtracking, forward-checking or GAC can be
       executed depending on the propagator used.

'''
########################################################
# Backtracking Routine                                 #
########################################################

class BT:
    '''use a class to encapsulate things like statistics
       and bookeeping for pruning/unpruning variabel domains
       To use backtracking routine make one of these objects
       passing the CSP as a parameter. Then you can invoke
       that objects's bt_search routine with the right
       kind or propagator function to obtain plain backtracking
       forward-checking or gac'''

    def __init__(self, csp):
        '''csp == CSP object specifying the CSP to be solved'''

        self.csp = csp
        self.nDecisions = 0 #nDecisions is the number of variable
                            #assignments made during search
        self.nPrunings  = 0 #nPrunings is the number of value prunings during search
        unasgn_vars = list() #used to track unassigned variables
        self.TRACE = False
        self.runtime = 0


    def clear_stats(self):
        '''Initialize counters'''
        self.nDecisions = 0
        self.nPrunings = 0
        self.runtime = 0

    def print_stats(self):
        print("Search made {} variable assignments and pruned {} variable values".format(
            self.nDecisions, self.nPrunings))

    def restoreValues(self,prunings):
        '''Restore list of values to variable domains
           each item in prunings is a pair (var, val)'''
        for var, val in prunings:
            var.unprune_value(val)

    def restore_all_variable_domains(self):
        '''Reinitialize all variable domains'''
        for var in self.csp.vars:
            if var.is_assigned():
                var.unassign()
            var.restore_curdom()

    def extractMRVvar(self):
        '''Remove variable with minimum sized cur domain from list of
           unassigned vars. Would be faster to use heap...but this is
           not production code.
        '''

        md = -1
        mv = None
        for v in self.unasgn_vars:
            if md < 0:
                md = v.cur_domain_size()
                mv = v
            elif v.cur_domain_size() < md:
                md = v.cur_domain_size()
                mv = v
        self.unasgn_vars.remove(mv)
        return mv

    def restoreUnasgnVar(self, var):
        '''Add variable back to list of unassigned vars'''
        self.unasgn_vars.append(var)

    def bt_search(self,propagator):
        '''Try to solve the CSP using specified propagator routine

           propagator == a function with the following template
           propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

           csp is a CSP object---the propagator can use this to get access
           to the variables and constraints of the problem.

           newly_instaniated_variable is an optional argument.
           if newly_instantiated_variable is not None:
               then newly_instantiated_variable is the most
               recently assigned variable of the search.
           else:
               progator is called before any assignments are made
               in which case it must decide what processing to do
               prior to any variables being assigned.

           The propagator returns True/False and a list of (Variable, Value) pairs.
           Return is False if a deadend has been detected by the propagator.
             in this case bt_search will backtrack
           return is true if we can continue.

           The list of variable values pairs are all of the values
           the propagator pruned (using the variable's prune_value method).
           bt_search NEEDS to know this in order to correctly restore these
           values when it undoes a variable assignment.

           NOTE propagator SHOULD NOT prune a value that has already been
           pruned! Nor should it prune a value twice'''

        self.clear_stats()
        stime = time.process_time()

        self.restore_all_variable_domains()

        self.unasgn_vars = []
        for v in self.csp.vars:
            if not v.is_assigned():
                self.unasgn_vars.append(v)

        status, prunings = propagator(self.csp) #initial propagate no assigned variables.
        self.nPrunings = self.nPrunings + len(prunings)

        if self.TRACE:
            print(len(self.unasgn_vars), " unassigned variables at start of search")
            print("Root Prunings: ", prunings)

        if status == False:
            print("CSP{} detected contradiction at root".format(
                self.csp.name))
        else:
            status = self.bt_recurse(propagator, 1)   #now do recursive search


        self.restoreValues(prunings)
        if status == False:
            print("CSP{} unsolved. Has no solutions".format(self.csp.name))
        if status == True:
            print("CSP {} solved. CPU Time used = {}".format(self.csp.name,
                                                             time.process_time() - stime))
            self.csp.print_soln()

        print("bt_search finished")
        self.print_stats()

    def bt_recurse(self, propagator, level):
        '''Return true if found solution. False if still need to search.
           If top level returns false--> no solution'''

        if self.TRACE:
            print('  ' * level, "bt_recurse level ", level)

        if not self.unasgn_vars:
            #all variables assigned
            return True
        else:
            var = self.extractMRVvar()

            if self.TRACE:
                print('  ' * level, "bt_recurse var = ", var)

            for val in var.cur_domain():

                if self.TRACE:
                    print('  ' * level, "bt_recurse trying", var, "=", val)

                var.assign(val)
                self.nDecisions = self.nDecisions+1

                status, prunings = propagator(self.csp, var)
                self.nPrunings = self.nPrunings + len(prunings)

                if self.TRACE:
                    print('  ' * level, "bt_recurse prop status = ", status)
                    print('  ' * level, "bt_recurse prop pruned = ", prunings)

                if status:
                    if self.bt_recurse(propagator, level+1):
                        return True

                if self.TRACE:
                    print('  ' * level, "bt_recurse restoring ", prunings)
                self.restoreValues(prunings)
                var.unassign()

            self.restoreUnasgnVar(var)
            return False

    #########################################
    #########################################
    #######                          ########
    ####### modified for minesweeper ########
    #######                          ########
    #########################################
    #########################################

    def bt_search_MS(self,propagator):
        '''This is modified from bt_search function.
        1. Keep assigned value for variables.
        2. Use bt_recurse_MS instead of bt_recurse
        '''

        self.clear_stats()
        stime = time.process_time()

        #self.restore_all_variable_domains()

        self.unasgn_vars = []
        for v in self.csp.vars:
            if not v.is_assigned():
                self.unasgn_vars.append(v)

        status, prunings = propagator(self.csp) #initial propagate no assigned variables.
        self.nPrunings = self.nPrunings + len(prunings)

        if self.TRACE:
            print(len(self.unasgn_vars), " unassigned variables at start of search")
            print("Root Prunings: ", prunings)

        if status == False:
            print("CSP{} detected contradiction at root".format(
                self.csp.name))
        else:
            status = self.bt_recurse_MS(propagator, 1)   #now do recursive search


        self.restoreValues(prunings)
        if status == False:
            print("CSP{} unsolved. Has no solutions".format(self.csp.name))
        # if status == True:
        #     print("CSP {} solved. CPU Time used = {}".format(self.csp.name,
        #                                                      time.process_time() - stime))
        #     self.csp.print_soln()

        #print("bt_search finished")
        #self.print_stats()
        return self.nDecisions

    def bt_recurse_MS(self, propagator, level):
        '''This is modified from bt_recurse function.
        1. Using extractMRVvar_MS() instead of extractMRVvar()

        Return true if found solution. False if still need to search.
        If top level returns false--> no solution'''

        if self.TRACE:
            print('  ' * level, "bt_recurse level ", level)

        if not self.unasgn_vars:
            #all variables assigned
            return True
        else:
            var = self.extractMRVvar_MS()
            if not var:
                return True
            if self.TRACE:
                print('  ' * level, "bt_recurse var = ", var)

            for val in var.cur_domain():

                if self.TRACE:
                    print('  ' * level, "bt_recurse trying", var, "=", val)

                var.assign(val)
                self.nDecisions = self.nDecisions+1

                status, prunings = propagator(self.csp, var)
                self.nPrunings = self.nPrunings + len(prunings)

                if self.TRACE:
                    print('  ' * level, "bt_recurse prop status = ", status)
                    print('  ' * level, "bt_recurse prop pruned = ", prunings)

                if status:
                    if self.bt_recurse_MS(propagator, level+1):
                        return True

                if self.TRACE:
                    print('  ' * level, "bt_recurse restoring ", prunings)
                self.restoreValues(prunings)
                var.unassign()

            self.restoreUnasgnVar(var)
            return False

    def extractMRVvar_MS(self):
        '''Remove variable from list of unassigned vars. The variable with cur_domain size 1 or
        it's the only unassign variable in a constraint.
        Would be faster to use heap...but this is not production code.
        '''
        #print(self.unasgn_vars)
        for var in self.unasgn_vars:
            if var.cur_domain_size() == 1:
                self.unasgn_vars.remove(var)
                return var

        for con in self.csp.get_all_cons():
            if con.get_n_unasgn() == 0:
                continue
            if con.get_n_unasgn() == 1:
                mv = con.get_unasgn_vars()[0]
                self.unasgn_vars.remove(mv)
                return mv
        return None
