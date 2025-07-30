from __future__ import annotations
#from .game import Game
#from .stone import Stone
from random import choice
#from .tile import Tile
from logging import info, warning



#from logger import Logger
# 
from . import stone, tile ,game

class Komino(game.Game):


    def __init__(self,TilesToFill,k=5):
        super().__init__(TilesToFill)
        self.k=k

    @classmethod
    def generate(cls,M,k=5,return_solution=False):
        # TODO return used stones Dictionary
        from . import tile # Why ???

        boundary={tile.Tile((0,0))}
        T=set()
        solution:list[stone.Stone]=[]
        while boundary and M:
            c=choice(list(boundary))
            boundary.remove(c)
            toCheck={c}

            tilesFound :set[tile.Tile]=set()

            while toCheck and len(tilesFound)<k:
                front : tile.Tile= toCheck.pop()
                #toCheck.remove(front)
                if front in T or front in tilesFound:
                    continue
                toCheck.update(front.get_neighbores())
                tilesFound.add(front)

            tilesFound=stone.Stone(tilesFound)
            if len(tilesFound)==k:
                T|=tilesFound
                solution.append(tilesFound)

                neig: set[tile.Tile]=set()
                for tile  in tilesFound:
                    neig.update(tile.get_neighbores())
                neig -= T
                neig -= tilesFound
                boundary.update(neig)
                M-=1

        usedStones={}
        for st in solution:
            norm=st.normalize()
            if norm in usedStones:
                usedStones[st.normalize()]+=1
            else:
                usedStones[norm]=1

        if return_solution:
            return Komino(TilesToFill=T,k=k),usedStones,solution
        else:
            return Komino(TilesToFill=T,k=k),usedStones

        pass

  
    def unique_stones(self,_k=None) -> set[stone.Stone]:
        if _k is None:
            _k=self.k
        if _k==1:
            return {stone.Stone(((0,0),))}
        
        prev=self.unique_stones(_k-1)

        res=set()

        for s in prev:
            s:stone.Stone
            bound=s.outer_bound()

            for t in bound:
                s_new=stone.Stone(s | {t})
                s_new=s_new.normalize()
                res.add(s_new)
        return res


        
    
    def unique_stones_dict(self,N):
        """
        dictionary that says >>all stones are N times available<<
        """
        res={}
        for s in self.unique_stones():
            res[s]=N
        return res
        
    pass

    def find_solution(self,limits:dict[stone.Stone]|int=None,display=True):
        from tilingpuzzles.solvers import kominoSolver
        from tilingpuzzles.visualize import visualize
        
        if limits is None:
            #TODO
            assert False, "not implemented"
        if isinstance(limits,int):
            limits=self.unique_stones_dict(limits)
        
        solver=kominoSolver.KominoSolverLimited(self,limits)
        res=solver.solve()

        if display:
            vz =visualize.Visualize()
            vz.add_stone(self.T)

            for st in res:
                vz.add_stone(st)
            
            vz.render()


        return res
  
        pass 

    def count_solutions(self,limits:dict[stone.Stone]|int=None,progressLevel=1):
        from tilingpuzzles.solvers import kominoSolver

        if limits is None:
            solver = kominoSolver.KominoSolverUnlimted(self, k=self.k)
            res = solver.solve(progressLevel)
            return res 
        
        else:
            #TODO count limited
            assert False, "counting with limitations not implemented yet"


        pass
