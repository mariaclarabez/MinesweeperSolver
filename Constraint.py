'''
This class represents a Minesweeper constraint. This class allows one to define
constraints specified by tables of satisfying assignments.
'''

class Constraint:
    '''Class for defining constraints variable objects specifes an
       ordering over variables.'''

    def __init__(self, name, scope):
        '''Initialization function. Consraints are implemented as storing a set
        of satisfying tuples.
        '''

        self.scope = list(scope)
        self.name = name
        self.sat_tuples = dict()

        # list of satisfying tuples that contain a particular variable/value
        self.sup_tuples = dict()

    def add_satisfying_tuples(self, tuples):
        '''We specify the constraint by adding its complete list of satisfying
        tuples to sup_tuples.'''
        for x in tuples:
            t = tuple(x)  # ensure we have an immutable tuple
            if not t in self.sat_tuples:
                self.sat_tuples[t] = True

            # now put t in as a support for all of the variable values in it
            for i, val in enumerate(t):
                var = self.scope[i]
                if not (var,val) in self.sup_tuples:
                    self.sup_tuples[(var,val)] = []
                self.sup_tuples[(var,val)].append(t)

    def get_scope(self):
        '''get list of variables the constraint is over'''
        return list(self.scope)

    def get_n_unasgn(self):
        '''return the number of unassigned variables in the constraint's scope'''
        n = 0
        for v in self.scope:
            if not v.is_assigned():
                n = n + 1
        return n

    def get_unasgn_vars(self):
        '''return list of unassigned variables in constraint's scope. Note
           more expensive to get the list than to then number'''
        vs = []
        for v in self.scope:
            if not v.is_assigned():
                vs.append(v)
        return vs

    def has_support(self, var, val):
        '''Test if a variable value pair has a supporting tuple (a set
           of assignments satisfying the constraint where each value is
           still in the corresponding variables current domain
        '''
        if (var, val) in self.sup_tuples:
            for t in self.sup_tuples[(var, val)]:
                if self.tuple_is_valid(t):
                    return True
        return False

    def tuple_is_valid(self, t):
        '''Internal routine. Check if every value in tuple is still in
           corresponding variable domains'''
        for i, var in enumerate(self.scope):
            if not var.in_cur_domain(t[i]):
                return False
        return True

    def __str__(self):
        return("{}({})".format(self.name,[var.name for var in self.scope]))
