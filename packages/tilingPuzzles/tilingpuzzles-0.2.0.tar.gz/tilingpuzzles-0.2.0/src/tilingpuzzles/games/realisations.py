
from __future__ import annotations
import logging

from . import stone

class Realisations():
    """
    Used to genrate Mixed Integer Program for solving with highs Algorithm
    not needed for now
    """
    # FIXME outdated
    
    def __init__(self,msk):
        assert msk
        self.msk=stone.Stone(msk)
        self.indexToReal={}
        self.stoneToReal={}
    


    def add_stone(self,stone: stone.Stone):

        # if realisation already exists do nothing
        if stone in self.stoneToReal:
            return
        

        stone=stone.shift_positive()
        logging.info(f"{self.stoneToReal = }")
        self.stoneToReal[stone]=[]
        logging.info(f"{ stone = }")
        
        # FIXME use actual Symetries, stone.get_symetries
        
        symetries=[stone]

        symetries.sort()


        (X_min,Y_min),(X_max,Y_max)=self.msk.bounding_Box

        logging.info(f"\n mask bounding box = {self.msk.bounding_Box}")

        
        for sym in symetries:
            sym=sym.shift_positive()
            (x_min,y_min),(x_max,y_max)=sym.bounding_Box

            logging.info(f"\nBounding box symetrie = {sym.bounding_Box}")
            


            for dx in range(X_min -x_min,X_max-x_max+1):
                for dy in range(Y_min-y_min,Y_max-y_max+1):
                    new_stone=sym.shift(dx,dy)
                    if not new_stone <= self.msk:
                         continue
                    n=len(self.indexToReal)
                    self.indexToReal[n]=new_stone
                    self.stoneToReal[stone].append(new_stone)
        return
    


    def to_matrix(self):
            pass

                
            

            

            




