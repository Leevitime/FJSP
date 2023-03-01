import xlwt
import numpy as np
import copy

from Lot import Lot
import single_machine_setup_cp as cp


def write_to_xls(lots, ttmatrix):
    lots.sort(key=lambda lot: lot.idx)
    work_book = xlwt.Workbook()
    worksheet_data = work_book.add_sheet('lot_data')

    # write lot information
    worksheet_data.write(0, 0, 'lot_id')
    worksheet_data.write(0, 1, 'arrive_time')
    worksheet_data.write(0, 2, 'process_time')
    worksheet_data.write(0, 3, 'type')

    for idx, lot in enumerate(lots):
        worksheet_data.write(idx + 1, 0, lot.idx)
        worksheet_data.write(idx + 1, 1, lot.arrivet)
        worksheet_data.write(idx + 1, 2, lot.processt)
        worksheet_data.write(idx + 1, 3, lot.ltype)

    # write setup time for type transformation
    worksheet_setup_matrix = work_book.add_sheet('setup_matrix')
    for i in range(len(ttmatrix)):
        for j in range(len(ttmatrix[0])):
            worksheet_setup_matrix.write(i, j, ttmatrix[i][j])

    # save excel
    work_book.save('data/%i.xls' % len(lots))


def generate_data(nlot):
    ntype = min(int(nlot / 3), 10)
    if ntype <= 1:
        ntype = 3

    lots = []
    ttmatrix = np.zeros((ntype, ntype))

    # set type transformation matrix
    for i in range(ntype):
        for j in range(i + 1, ntype):
            ttmatrix[i][j] = np.random.randint(1, 5)
            ttmatrix[j][i] = ttmatrix[i][j]

    # random generate lot
    for i in range(nlot):
        lot = Lot(idx=i,
                  ltype=np.random.randint(ntype),
                  arrivet=np.random.randint(0, nlot * 6),
                  processt=np.random.randint(5, 11)
                  )
        lots.append(lot)

    cpmdl = cp.SingleSetupOrtoolsCP(lots, ttmatrix)
    cpmdl.build_model()
    cpmdl.solve()
    cpmdl.print_status_result_statistics()
    cpmdl.show_gantt_chart()
    if cpmdl.has_solution():
        write_to_xls(lots, ttmatrix)
    else:
        generate_data(nlot)


for n in range(2, 10):
    generate_data(n)

for n in range(10, 100, 10):
    generate_data(n)

for n in range(100, 501, 50):
    generate_data(n)