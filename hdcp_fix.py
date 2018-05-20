import pickle
import sys
from os import listdir, makedirs
from os.path import isfile, join, exists
import pdb
import king_classic_pkling
from king_classic_pkling import PlayGolf, Player


def hdcp_fix():
    allfiles = [f for f in listdir('pkl_files/') if isfile(join('pkl_files/', f))]
    for pf in allfiles:
        with open('pkl_files/' + pf, 'rb') as f:
            golfer = pickle.load(f)
            golfer.courses["Whirlwind - Devil's Claw"][1][1] = 17

        with open('pkl_files/' + pf, 'wb') as f:
            pickle.dump(golfer, f)


if __name__ == '__main__':
    hdcp_fix()
