import numpy as np
import xlrd
import xlwt

from Lot import Lot
import single_machine_setup_cp as cp
import single_machine_setup_lp as lp
import single_machine_setup_copt as cop


class SingleMachineExperiment:

    def __init__(self):
        self.lots = None
        self.ttmatrix = None
        self.orcpbook = xlwt.Workbook()
        self.orlpbook = xlwt.Workbook()
        self.coptbook = xlwt.Workbook()

    def read_excel(self, name):
        wbook = xlrd.open_workbook(name)

        # read lot information
        lots = []
        ltable = wbook.sheet_by_name('lot_data')

        for i in range(1, ltable.nrows):
            r = ltable.row(i)
            lots.append(Lot(idx=int(r[0].value),
                            arrivet=int(r[1].value),
                            processt=int(r[2].value),
                            ltype=int(r[3].value)
                            )
                        )
            print(lots[-1])
        self.lots = lots

        # read type transformation information
        ttable = wbook.sheet_by_name('setup_matrix')

        ntype = ttable.nrows
        ttmatrix = np.zeros((ntype, ntype))

        for i in range(ntype):
            for j in range(ntype):
                ttmatrix[i][j] = int(ttable.cell(i, j).value)

        self.ttmatrix = ttmatrix
        print(ttmatrix)

    def ortools_cp_experiments(self):
        wbook = self.orcpbook
        wtbale = wbook.add_sheet('ortools_cp_experiment')
        wtbale.write(0, 0, 'size')
        wtbale.write(0, 1, 'time')
        wtbale.write(0, 2, 'objv')
        wtbale.write(0, 3, 'status')

        rowcount = 1
        for n in range(2, 10):
            self.ortools_cp_single_experiment(n, rowcount, wtbale)
            rowcount += 1

        for n in range(10, 100, 10):
            self.ortools_cp_single_experiment(n, rowcount, wtbale)
            rowcount += 1

        for n in range(100, 501, 50):
            self.ortools_cp_single_experiment(n, rowcount, wtbale)
            rowcount += 1

    def ortools_cp_single_experiment(self, size, row, table):
        filename = 'data/%i.xls' % size
        self.read_excel(filename)
        mdl = cp.SingleSetupOrtoolsCP(self.lots, self.ttmatrix)
        mdl.main(300)
        time = mdl.get_solve_time()
        status = mdl.get_solve_status()
        obj = mdl.get_objective_value()

        table.write(row, 0, size)
        table.write(row, 1, time)
        table.write(row, 2, obj)
        table.write(row, 3, status)

    def save_ortools_cp_result(self):
        self.orcpbook.save('data/result.xls')

    def ortools_lp_experiments(self):
        wbook = self.orlpbook
        wtbale = wbook.add_sheet('ortools_lp_experiment')
        wtbale.write(0, 0, 'size')
        wtbale.write(0, 1, 'time')
        wtbale.write(0, 2, 'objv')
        wtbale.write(0, 3, 'status')

        rowcount = 1
        for n in range(2, 10):
            self.ortools_lp_single_experiment(n, rowcount, wtbale)
            rowcount += 1

        for n in range(10, 100, 10):
            self.ortools_lp_single_experiment(n, rowcount, wtbale)
            rowcount += 1

        for n in range(100, 501, 50):
            self.ortools_lp_single_experiment(n, rowcount, wtbale)
            rowcount += 1

    def ortools_lp_single_experiment(self, size, row, table):
        filename = 'data/%i.xls' % size
        self.read_excel(filename)
        mdl = lp.SingleSetupOrtoolsLP(self.lots, self.ttmatrix)
        mdl.main(300)
        time = mdl.get_solve_time()
        status = mdl.get_solve_status()
        obj = mdl.get_objective_value()

        table.write(row, 0, size)
        table.write(row, 1, time)
        table.write(row, 2, obj)
        table.write(row, 3, status)

    def save_ortools_lp_result(self):
        self.orlpbook.save('data/result1.xls')

    def copt_experiments(self):
        wbook = self.coptbook
        wtbale = wbook.add_sheet('ortools_copt_experiment')
        wtbale.write(0, 0, 'size')
        wtbale.write(0, 1, 'time')
        wtbale.write(0, 2, 'objv')
        wtbale.write(0, 3, 'status')

        rowcount = 1
        for n in range(2, 10):
            self.copt_single_experiment(n, rowcount, wtbale)
            rowcount += 1

        for n in range(10, 100, 10):
            self.copt_single_experiment(n, rowcount, wtbale)
            rowcount += 1

        for n in range(100, 501, 50):
            self.copt_single_experiment(n, rowcount, wtbale)
            rowcount += 1

    def copt_single_experiment(self, size, row, table):
        filename = 'data/%i.xls' % size
        self.read_excel(filename)
        mdl = cop.SingleSetupCOPT(self.lots, self.ttmatrix)
        mdl.main(300)
        time = mdl.get_solve_time()
        status = mdl.get_solve_status()
        obj = mdl.get_objective_value()

        table.write(row, 0, size)
        table.write(row, 1, time)
        table.write(row, 2, obj)
        table.write(row, 3, status)

    def save_copt_result(self):
        self.coptbook.save('data/result2.xls')


if __name__ == '__main__':
    exp = SingleMachineExperiment()
    exp.copt_experiments()
    exp.save_copt_result()
