"""Minimize single lot-process machine's schedule with setup time constraint."""

from ortools.linear_solver import pywraplp
from Lot import Lot
from graph import single_machine_setup_gantt
import single_machine_setup_cp as cp

"""Test Date"""
# (arrive, duration, type)
lot_data = [(0, 3, 0), (11, 2, 1), (28, 2, 2), (0, 2, 2), (2, 1, 1), (19, 4, 0), (1, 4, 0), (2, 3, 1),
            (10, 3, 0), (20, 2, 1), (21, 2, 1)]
type_transform_matrix = [
    [0, 1, 2],
    [1, 0, 3],
    [2, 3, 0]
]


class SingleSetupOrtoolsLP:

    def __init__(self, lots, ttmatrix, solvername='SCIP'):
        self.lots = lots
        self.ttmatrix = ttmatrix
        self.nlot = len(lots)

        self.solver = pywraplp.Solver.CreateSolver(solvername)
        self.t = None
        self.x = None
        self.obj = None
        self.status = None
        self.objv = None

    def add_precedence_constraint(self):
        lots = self.lots
        nlot = self.nlot
        ttmatrix = self.ttmatrix
        solver = self.solver
        x = self.x
        t = self.t

        M = 1e5
        for i in range(nlot):
            for j in range(i + 1, nlot):
                pi, pj = lots[i].processt, lots[j].processt
                tt = cp.get_tt(lots, i, j, ttmatrix)
                # Add Non-overlap constraint
                solver.Add(t[i] + pi + tt <= t[j] + M * (1 - x[i][j]))
                solver.Add(t[j] + pj + tt <= t[i] + M * x[i][j])

    def build_model(self):
        # data
        lots = self.lots
        nlot = self.nlot
        solver = self.solver
        horizon = cp.calculate_horizon(lots)  # upper bound of time variables

        # define variables
        self.obj = solver.NumVar(0, horizon, 'obj')
        self.t = [solver.NumVar(lot.arrivet, horizon, 't_%i' % lot.idx) for lot in lots]
        self.x = [[solver.BoolVar('x_%i%i' % (i, j)) for j in range(nlot)] for i in range(nlot)]

        # add constraints
        cp.add_obj_constraints(solver, self.obj, self.t, lots)
        self.add_precedence_constraint()

        # set objective function
        solver.Minimize(self.obj)

    def set_solve_time(self, t):
        self.solver.SetTimeLimit(1000 * t)

    def solve(self):
        print('Start Solving...\n...')
        solver = self.solver
        # solve the problem
        self.status = solver.Solve()
        print('Solve Complete.')
        if self.has_solution():
            self.save_result()

    def has_solution(self):
        if self.get_solve_status() in ('OPTIMAL', 'FEASIBLE'):
            return True
        else:
            return False

    def print_status_result_statistics(self):
        self.show_solve_status_and_result()
        self.show_solve_statistics()

    def save_result(self):
        nlot = self.nlot
        lots = self.lots
        solver = self.solver
        t = self.t

        # save the result
        for i in range(nlot):
            lots[i].startt = t[i].solution_value()

        self.objv = solver.Objective().Value()
        # sort lots by sequence
        lots.sort(key=lambda lot: lot.startt)

    def show_solve_status_and_result(self):
        print('Solution Status: ' + self.get_solve_status())
        if self.has_solution():
            cp.print_lot_schedule(self.lots, self.objv)

    def show_solve_statistics(self):
        solver = self.solver
        # Statistics.
        print('\nAdvanced usage:')
        print('Problem solved in %f seconds' % (float(solver.wall_time()) / 1000.0))
        print('Problem solved in %d iterations' % solver.iterations())

    def show_gantt_chart(self):
        if self.has_solution():
            single_machine_setup_gantt(self.lots, self.ttmatrix)
        else:
            print('No gantt chart to show!')

    def get_solve_status(self):
        status = ''
        if self.status == pywraplp.Solver.OPTIMAL:
            status = 'OPTIMAL'
        elif self.status == pywraplp.Solver.FEASIBLE:
            status = 'FEASIBLE'
        elif self.status == pywraplp.Solver.INFEASIBLE:
            status = 'INFEASIBLE'
        elif self.status == pywraplp.Solver.UNBOUNDED:
            status = 'UNBOUNDED'
        elif self.status == pywraplp.Solver.ABNORMAL:
            status = 'ABNORMAL'
        elif self.status == pywraplp.Solver.MODEL_INVALID:
            status = 'MODEL_INVALID'
        elif self.status == pywraplp.Solver.NOT_SOLVED:
            status = 'NOT_SOLVED'
        return status

    def get_solve_time(self):
        return self.solver.wall_time() / 1000

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

    ssolp = SingleSetupOrtoolsLP(lots1, ttmatrix)
    ssolp.main()
