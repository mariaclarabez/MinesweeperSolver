'''
This class represents the backtracking backtracking algorithm. It takes
propagator and CSP as arguments so that basic backtracking, forward-checking or
GAC can be executed depending on the propagator used.
'''

import time

class BT:
    '''Backtracking class to handle the backtracking algorithm and its
    associated methods'''

    def __init__(self, csp):
        '''Initialization, csp == CSP object specifying the CSP to be solved'''

        self.csp = csp

        # nDecisions is the number of variable assignments made during search
        self.nDecisions = 0
        # nPrunings is the number of value prunings during search
        self.nPrunings  = 0
        # used to track unassigned variables
        unasgn_vars = list()
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
        '''Remove variable with minimum sized current domain from list of
           unassigned vars.
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
        '''Try to solve the CSP using specified propagator routine. The
        propagator returns True/False and a list of (Variable, Value) pairs.
        Return is False if a deadend has been detected by the propagator.
        In this case bt_search will backtrack, otherwise return is true if we
        can continue.
       '''

        self.clear_stats()
        stime = time.process_time()

        self.restore_all_variable_domains()

        self.unasgn_vars = []
        for v in self.csp.vars:
            if not v.is_assigned():
                self.unasgn_vars.append(v)

        # initial propagate no assigned variables.
        status, prunings = propagator(self.csp)
        self.nPrunings = self.nPrunings + len(prunings)

        if self.TRACE:
            print(len(self.unasgn_vars), " unassigned variables at start of search")
            print("Root Prunings: ", prunings)

        if status == False:
            print("CSP{} detected contradiction at root".format(
                self.csp.name))
        else:
            status = self.bt_recurse(propagator, 1)


        self.restoreValues(prunings)
        if status == False:
            print("CSP{} unsolved. Has no solutions".format(self.csp.name))
        if status == True:
            print("CSP {} solved. CPU Time used = {}".format(self.csp.name,
                                                             time.process_time()
                                                             - stime))
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

    def bt_search_MS(self,propagator):
        '''This is modified from bt_search function that is modified for
        Minesweeper. The changes are as follows:
        1. Keep assigned value for variables.
        2. Use bt_recurse_MS instead of bt_recurse
        '''

        self.clear_stats()
        stime = time.process_time()

        self.unasgn_vars = []
        for v in self.csp.vars:
            if not v.is_assigned():
                self.unasgn_vars.append(v)

        # initial propagate no assigned variables.
        status, prunings = propagator(self.csp)
        self.nPrunings = self.nPrunings + len(prunings)

        if self.TRACE:
            print(len(self.unasgn_vars), " unassigned variables at start of search")
            print("Root Prunings: ", prunings)

        if status == False:
            print("CSP{} detected contradiction at root".format(
                self.csp.name))
        else:
            status = self.bt_recurse_MS(propagator, 1)


        self.restoreValues(prunings)
        if status == False:
            print("CSP{} unsolved. Has no solutions".format(self.csp.name))

        return self.nDecisions

    def bt_recurse_MS(self, propagator, level):
        '''This is modified from bt_recurse function.
        1. Using extractMRVvar_MS() instead of extractMRVvar()

        Return true if found solution. False if still need to search.
        If top level returns false--> no solution'''

        if self.TRACE:
            print('  ' * level, "bt_recurse level ", level)

        if not self.unasgn_vars:
            # all variables assigned
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
        '''Remove variable from list of unassigned variables. The variable with
        cur_domain size 1 or it's the only unassigned variable in a constraint.
        '''
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
