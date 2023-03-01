import collections

from coptpy import *
import single_machine_setup_cp as cp
from graph import single_machine_setup_gantt

"""Test Date"""
# (arrive, duration, type)
lot_data = [(0, 3, 0),
            (11, 2, 1), (28, 2, 2), (0, 2, 2),
            (2, 1, 1), (19, 4, 0), (1, 4, 0),
            (2, 3, 1), (10, 3, 0), (20, 2, 1),
            (21, 2, 1)]
type_transform_matrix = [
    [0, 1, 2],
    [1, 0, 3],
    [2, 3, 0]
]


class SingleSetupCOPT:

    def __init__(self, lots, ttmatrix):
        self.lots = lots
        self.ttmatrix = ttmatrix
        self.nlot = len(lots)

        self.envr = Envr()
        self.model = self.envr.createModel()
        self.t = None
        self.x = None
        self.obj = None
        self.objv = None
        self.status = None

    def add_obj_constraints(self):
        mdl = self.model
        obj = self.obj
        t = self.t
        lots = self.lots
        nlot = self.nlot
        for i in range(nlot):
            mdl.addConstr(obj >= t[i] + lots[i].processt)

    def add_precedence_constraint(self):
        lots = self.lots
        nlot = self.nlot
        ttmatrix = self.ttmatrix
        mdl = self.model
        x = self.x
        t = self.t

        # 采用COPT.infinity会产生错误：生成的结果不符合要求
        # M = 1e+6
        M = 1e+5
        for i in range(nlot):
            for j in range(i + 1, nlot):
                pi, pj = lots[i].processt, lots[j].processt
                tt = cp.get_tt(lots, i, j, ttmatrix)
                # Add Non-overlap constraint
                mdl.addConstr(t[i] + pi + tt <= t[j] + M * (1 - x[i, j]))
                mdl.addConstr(t[j] + pj + tt <= t[i] + M * x[i, j])

    def build_model(self):
        # data
        lots = self.lots
        nlot = self.nlot
        mdl = self.model

        # define variables
        self.obj = mdl.addVar(vtype=COPT.CONTINUOUS)
        self.t = mdl.addVars(nlot, lb=[lot.arrivet for lot in lots], vtype=COPT.CONTINUOUS, nameprefix='t')
        self.x = mdl.addVars(nlot, nlot, vtype=COPT.BINARY, nameprefix='x')

        # add constraints
        self.add_obj_constraints()
        self.add_precedence_constraint()

        # set objective function
        mdl.setObjective(self.obj, COPT.MINIMIZE)

    def set_solve_time(self, t):
        self.model.setParam(COPT.Param.TimeLimit, t)

    def solve(self):
        print('Start Solving...\n...')
        model = self.model
        # solve the problem
        model.solve()
        self.status = model.status
        print('Solve Complete.')
        if self.has_solution():
            self.save_result()

    def has_solution(self):
        if self.model.hasmipsol:
            return True
        else:
            return False

    def get_solve_status(self):
        status = ''
        if self.status == COPT.OPTIMAL:
            status = 'OPTIMAL'
        elif self.has_solution():
            status = 'FEASIBLE'
        elif self.status == COPT.INFEASIBLE:
            status = 'INFEASIBLE'
        elif self.status == COPT.UNBOUNDED:
            status = 'UNBOUNDED'
        elif self.status == COPT.NODELIMIT:
            status = 'NODELIMIT'
        elif self.status == COPT.TIMEOUT:
            status = 'TIMEOUT'
        else:
            status = 'NOT_SOLVED'
        return status

    def save_result(self):
        nlot = self.nlot
        lots = self.lots
        model = self.model
        t = self.t

        # save the result
        for i in range(nlot):
            lots[i].startt = t[i].x
            print('%i: ' % i + str(t[i].x))

        self.objv = model.objval
        # sort lots by sequence
        lots.sort(key=lambda lot: lot.startt)

    def print_status_result_statistics(self):
        self.show_solve_status_result()
        # self.show_solve_statistics()

    def show_solve_status_result(self):
        print('Solution Status: ' + self.get_solve_status())
        if self.has_solution():
            cp.print_lot_schedule(self.lots, self.objv)

    # def show_solve_statistics(self):
    #     # Statistics.
    #     print('---------------------')
    #     print(self.get_solve_status())
    #     print(self.get_solve_time())

    def show_gantt_chart(self):
        if self.has_solution():
            single_machine_setup_gantt(self.lots, self.ttmatrix)
        else:
            print('No gantt chart to show!')

    def get_solve_time(self):
        return self.model.solvingTime

    def get_objective_value(self):
        return self.objv

    def main(self, solvetime=10):
        self.build_model()
        self.set_solve_time(solvetime)
        self.solve()
        self.print_status_result_statistics()
        self.show_gantt_chart()


if __name__ == '__main__':
    lots1 = cp.create_lots_from_tuplelist(lot_data)
    ttmatrix = type_transform_matrix

    ssolp = SingleSetupCOPT(lots1, ttmatrix)
    ssolp.main()
