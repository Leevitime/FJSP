'''Lot: type at pt st'''


class Lot():

    def __init__(self, idx, ltype, arrivet, processt, startt=-1):
        self.idx = idx
        self.ltype = ltype
        self.arrivet = arrivet
        self.processt = processt
        self.startt = startt

    def gettype(self):
        return self.ltype

    def __repr__(self):
        return 'Lot: {},Type: {},arrive at {}, process {} mins.'.format(self.idx, self.ltype,
                                                                        self.processt, self.arrivet)
