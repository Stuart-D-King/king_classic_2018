import pandas as pd
import numpy as np
import pickle
import sys

class inviteList(object):

    def __init__(self, init=False):
        if init:
            self.df = pd.DataFrame(data=[],columns=['name', 'attending', 'notes'])
        else:
            self.df = pd.read_pickle('kc_guest_list.pkl')

    def add_row(self, list_add):
        n_arr = np.array(list_add).reshape(1, len(list_add))
        cols = self.df.columns
        pds = pd.DataFrame(n_arr, columns=cols)
        self.df = self.df.append(pds, ignore_index=True)
        # self.df.index = np.arange(1, len(self.df) + 1)
        self.df.index = self.df.index + 1
        return self.df

    def save(self):
        self.df.to_pickle('kc_guest_list.pkl')
        print('guest list saved')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            gl = inviteList(True)
    else:
        gl = inviteList()
