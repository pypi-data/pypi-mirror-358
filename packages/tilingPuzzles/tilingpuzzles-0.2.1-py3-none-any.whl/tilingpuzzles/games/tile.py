from __future__ import annotations
import logging

#from .stone import Stone as Stone

from . import stone



class Tile(tuple):
    #WARNING performance, remove this use plain tuples
    
    def __new__(cls,*cords):
        cords=tuple(map(int,*cords))
    
        return super(Tile,cls).__new__(cls,cords)
        
    
    def __init__(self,*cords):
        pass

    #TODO change to `stone.Stone.get_neigbores(tuple)-> Stone`
    def get_neighbores(self,lowerB=None,upperB=None) -> stone.Stone:
        res=[]
        n=len(self)

        for i in range(n):
            new_cords=[ self[j]+ (i==j) for j in range(n)]
            if upperB is None or new_cords[i]<upperB[i]:
                res.append(Tile(new_cords))
            new_cords=[ self[j]- (i==j) for j in range(n)]
            if lowerB is None or new_cords[i]>=lowerB[i]:
                res.append(Tile(new_cords))

        return stone.Stone(res)
    

    

