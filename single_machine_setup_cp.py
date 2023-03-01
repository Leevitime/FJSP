"""Minimize single lot-process machine's schedule with setup time constraint."""
import collections
from Lot import Lot
from graph import single_machine_setup_gantt

from ortools.sat.python import cp_model

"""Test Date"""
# (arrive, duration, type)
lot_data = [(0, 3, 0), (11, 2, 1), (28, 2, 2), (0, 2, 2), (2, 1, 1), (19, 4, 0), (1, 4, 0), (2, 3, 1),
            (10, 3, 0), (20, 2, 1), (21, 2, 1)]
type_transform_matrix = [
    [0, 1, 2],
    [1, 0, 3],
    [2, 3, 0]
]


def create_lots_from_tuplelist(lot_data):
    ats = [lot[0] for lot in lot_data]
    pts = [lot[1] for lot in lot_data]
    tps = [lot[2] for lot in lot_data]
    return create_lots(ats, pts, tps)


def create_lots(ats, pts, tps):
    lots = []
    for i in range(len(ats)):
        at = ats[i]
        pt = pts[i]
        tp = tps[i]
        lots.append(Lot(idx=i, arrivet=at, processt=pt, ltype=tp))
    return lots


def calculate_horizon(lots):
    return sum(lot.processt for lot in lots) * 3


def get_tt(lots, i, j, tt_matrix):
    ti = lots[i].ltype
    tj = lots[j].ltype
    return int(tt_matrix[ti][tj])


def add_obj_constraints(model, obj, t, lots):
    nlot = len(lots)
    for i in range(nlot):
        model.Add(obj >= t[i] + lots[i].processt)


def print_lot_schedule(lots, objv):
    output = ''
    sol_line_tasks = 'Machine ' + ': '
    sol_line = '         '

    for lot in lots:
        i = lot.idx
        tp = lot.ltype
        at = lot.arrivet
        st = lot.startt
        pt = lot.processt

        name = 'lot_%i:t%i' % (i, tp)
        # Add spaces to output to align columns.
        sol_line_tasks += '%-15s' % name

        sol_tmp = '[%i(%i)->%i]' % (st, at, st + pt)
        # Add spaces to output to align columns.
        sol_line += '%-15s' % sol_tmp

    sol_line += '\n'
    sol_line_tasks += '\n'
    output += sol_line_tasks
    output += sol_line

    print(f'Optimal Objective: {objv}')
    print(output)


class SingleSetupOrtoolsCP:

    def __init__(self, lots, ttmatrix):
        self.lots = lots
        self.ttmatrix = ttmatrix
        self.nlot = len(lots)

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.t = None
        self.obj = None
        self.status = None
        self.objv = None

    def add_setup_constraint(self):
        model = self.model
        t = self.t
        lots = self.lots
        ttmatrix = self.ttmatrix

        nlot = len(lots)
        for i in range(nlot):
            for j in range(i + 1, nlot):
                x_ij = model.NewBoolVar('x_%i%i' % (i, j))  # precedence: i -> j
                ti, tj = t[i], t[j]
                di, dj = lots[i].processt, lots[j].processt
                tt = get_tt(lots, i, j, ttmatrix)
                model.Add(tj + dj + tt <= ti).OnlyEnforceIf(x_ij.Not())
                model.Add(ti + di + tt <= tj).OnlyEnforceIf(x_ij)

    def build_model(self):
        # data
        lots = self.lots
        model = self.model
        nlot = self.nlot
        horizon = calculate_horizon(lots)  # upper bound of time variables

        # define variables
        obj = model.NewIntVar(0, horizon, 'obj')
        t = [model.NewIntVar(lot.arrivet, horizon, 't_%i' % lot.idx) for lot in lots]
        interval = [model.NewIntervalVar(t[i], lots[i].processt, t[i] + lots[i].processt, 'interval_%i' % i) for i in
                    range(nlot)]
        # save variables to object
        self.t = t
        self.obj = obj

        # add constraints
        add_obj_constraints(model, obj, t, lots)
        model.AddNoOverlap(interval)
        self.add_setup_constraint()

        # set objective function
        model.Minimize(obj)

    def set_solve_time(self, t):
        self.solver.parameters.max_time_in_seconds = t

    def solve(self):
        print('Start Solving...\n...')
        model = self.model
        solver = self.solver

        # solve and save the result
        self.status = solver.Solve(model)

        print('Solve Complete.')
        # save the result
        if self.has_solution():
            self.save_result()

    def save_result(self):
        nlot = self.nlot
        solver = self.solver
        t = self.t

        for i in range(nlot):
            self.lots[i].startt = solver.Value(t[i])

        self.objv = solver.Value(self.obj)
        # sort lots by sequence
        self.lots.sort(key=lambda lot: lot.startt)

    def print_status_result_statistics(self):
        self.show_solve_status_and_result()
        self.show_solve_statistics()

    def has_solution(self):
        if self.get_solve_status() in ('OPTIMAL', 'FEASIBLE'):
            return True
        else:
            return False

    def show_solve_status_and_result(self):
        print('Solution Status: ' + self.get_solve_status())
        if self.has_solution():
            print_lot_schedule(self.lots, self.objv)

    def show_solve_statistics(self):
        solver = self.solver
        # Statistics.
        print('Statistics')
        print('  - conflicts: %i' % solver.NumConflicts())
        print('  - branches : %i' % solver.NumBranches())
        print('  - wall time: %f s' % solver.WallTime())

    def show_gantt_chart(self):
        if self.has_solution():
            single_machine_setup_gantt(self.lots, self.ttmatrix)
        else:
            print('No gantt chart to show!')

    def get_solve_status(self):
        status = ''
        if self.status == cp_model.OPTIMAL:
            status = 'OPTIMAL'
        elif self.status == cp_model.FEASIBLE:
            status = 'FEASIBLE'
        elif self.status == cp_model.INFEASIBLE:
            status = 'INFEASIBLE'
        elif self.status == cp_model.MODEL_INVALID:
            status = 'MODEL_INVALID'
        elif self.status == cp_model.UNKNOWN:
            status = 'UNKNOWN'
        return status

    def get_solve_time(self):
        return self.solver.WallTime()

    def get_objective_value(self):
        return self.objv

    def main(self, solvetime=10):
        self.build_model()
        self.set_solve_time(solvetime)
        self.solve()
        self.print_status_result_statistics()
        self.show_gantt_chart()


if __name__ == '__main__':
    lots1 = create_lots_from_tuplelist(lot_data)
    ttmatrix = type_transform_matrix

    ssocp = SingleSetupOrtoolsCP(lots1, ttmatrix)
    print('nlot:' + str(ssocp.nlot))
    ssocp.main()
