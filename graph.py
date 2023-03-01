import matplotlib.pyplot as plt
from copy import deepcopy

font = {
    "family": "Microsoft YaHei",
    "style": "oblique",
    "weight": "bold",
    "color": "black",
    "size": 14
}

font_task = deepcopy(font)
font_task['color'] = 'black'

font_setup = deepcopy(font)
font_setup['color'] = 'r'

# bar color
colormap = plt.get_cmap('Paired')


def gantt_set_figure():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示中文标签
    plt.rcParams["figure.figsize"] = (25, 2)


def add_lot_bar(lot, yaxis):
    st = lot.startt
    pt = lot.processt
    color = colormap(lot.ltype)
    plt.barh(y=yaxis, width=pt, left=st, edgecolor="black", color=color)


def add_setup_bar(yaxis, lot, tt):
    xaxis = lot.startt + lot.processt
    plt.barh(y=yaxis, width=tt, left=xaxis, edgecolor='black', color='w')


def get_lot_type(lots, i):
    return lots[i].ltype


def add_lot_text(seq, lot, yaxis):
    idx = lot.idx
    ltp = lot.ltype
    at = lot.arrivet
    st = lot.startt
    pt = lot.processt

    # lot information
    plt.text(y=yaxis + 0.3 if seq % 2 == 0 else yaxis + 0, x=st + 0.1,
             s='lot_%i: t%i, %i' % (idx, ltp, at), fontdict=font_task)
    # process information
    plt.text(y=yaxis + 0.15 if seq % 2 == 0 else yaxis - 0.15, x=st + 0.1,
             s='        [%i, %i]' % (round(st), round(st) + pt), fontdict=font_task)


def add_setup_text(yaxis, lot, t1, t2, tt):
    xaxis = lot.startt + lot.processt
    plt.text(y=yaxis - 0.2, x=xaxis + 0.2, s='type:%i->%i' % (t1, t2), fontdict=font_setup)
    plt.text(y=yaxis - 0.35, x=xaxis + 0.2, s='time:%i' % tt, fontdict=font_setup)


def single_machine_setup_gantt(lots, tt_matrix):
    # gantt chart setting
    gantt_set_figure()

    # add lot bar
    for idx, lot in enumerate(lots):
        add_lot_bar(lot, 1)
        add_lot_text(idx, lot, 1)

    # add setup time bar
    for idx, lot in enumerate(lots[:-1]):
        t1, t2 = get_lot_type(lots, idx), get_lot_type(lots, idx + 1)
        if t1 == t2:
            continue

        tt = tt_matrix[t1][t2]
        add_setup_bar(1, lot, tt)
        add_setup_text(1, lot, t1, t2, tt)

    plt.title("甘特图")
    plt.xlabel("加工时间 /h")
    plt.ylabel("Machine")

    plt.show()
