
from . import stone

import logging


class Game:

    def __init__(self,tilesToFill):
        self.T=stone.Stone(tilesToFill)

        pass
    
    def to_mask(self):
        s=self.T
        s=s.shift_positive()
        
        return s.to_mask()

    pass