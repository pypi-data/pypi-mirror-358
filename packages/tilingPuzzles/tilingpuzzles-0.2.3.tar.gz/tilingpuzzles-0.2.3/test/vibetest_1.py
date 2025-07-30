#!/usr/bin/env python

import sys
sys.path.insert(0, '.')

from tilingPuzzles.games.stone import Stone
from tilingPuzzles.visualize.visualize import Visualize

def vibetest():
    s=Stone(((1,2),(2,2),(3,2),(3,4)))
    Visualize.draw_stone(stone=s)

    pass


if __name__=="__main__":
    vibetest()