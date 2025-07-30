

from ..games import komino
from ..games import stone
from logging import info
from ..visualize import visualize
from tqdm.notebook import tqdm


class KominoSolverLimited():

    def __init__(self,komino:komino.Komino,stoneDict:dict[stone.Stone,int]):
        r"""
        sets up a Solver
         - komino
            komino game
         - stoneDict
            dictionary of `stones` to `int`
            how often a stone of a certain kind can be placed.
        """

        self.T = komino.T
        self.stoneDict= stoneDict
        k=None
        for st in stoneDict:
            k=len(st)
            break
        assert k
        self.k=k 
        self.solved = False 
        self.solution: list[stone.Stone]=[ ]


    def solve(self):
        """
        finds a solution fot the problem if one exists
        """
        stone.Stone_config.MaxCacheStoneSize=self.k
        self.solved=self._get_solution(self.T,self.stoneDict)
        return self.solution.copy()
        pass

    def _get_solution(self,T:stone.Stone,availableStones:dict[stone.Stone,int]) -> bool:
        #info(f"{self.solution = }")
        components=list(T.ConectedComponents())
        components.sort(key=len)
        expPoint=components[0].good_cut_point()
        candidates =T.get_k_stone_on_tile(expPoint,self.k)

        for candidate in candidates:
            norm=candidate.normalize()
            if norm not in availableStones:
                continue
            next_T=stone.Stone(T-candidate)
            self.solution.append(candidate)
            if not next_T:
                return True

            comp=next_T.ConectedComponents()
            compSizesModK=map(lambda x:len(x) % self.k,comp)
            allZero=all(size==0 for size in compSizesModK)
            if not allZero:
                self.solution.pop()
                continue

            next_dict=availableStones.copy()
            next_dict[norm]-=1
            if not next_dict[norm]:
                del(next_dict[norm])
            res=self._get_solution(next_T,next_dict)
            if res:
                return True
            self.solution.pop()

        return False
    

    def get_solution_viz(self):
        """
        visualization of the solution process
        """
        #WARNING outdatet
        self.solved=self._get_solution_viz(self.T,self.stoneDict)
        return self.solution.copy()
        pass

    def _get_solution_viz(self,T:stone.Stone,availableStones:dict[stone.Stone,int]) -> bool:
        #info(f"{self.solution = }")

        expPoint=T.getMinTile()
        assert expPoint in T,f" {expPoint = } should be in T"
        print(f"{expPoint = }")
        print(f"{ availableStones = }")
        candidates =T.get_k_stone_on_tile(expPoint,self.k)

        print(f"{candidates = }")

        vz = visualize.Visualize()

        vz.add_stone(self.T)

        for st in self.solution:
            vz.add_stone(st)
        vz.render()

        for candidate in candidates:
            norm=candidate.normalize()
            if norm not in availableStones:
                continue
            next_T=stone.Stone(T-candidate)
            self.solution.append(candidate)
            if not next_T:
                return True

            comp=next_T.ConectedComponents()
            compSizesModK=map(lambda x:len(x) % self.k,comp)
            allZero=all(size==0 for size in compSizesModK)
            if not allZero:
                self.solution.pop()
                continue

            next_dict=availableStones.copy()
            next_dict[norm]-=1
            if not next_dict[norm]:
                del(next_dict[norm])
            res=self._get_solution_viz(next_T,next_dict)
            if res:
                return True
            self.solution.pop()

        return False


    def count_solutions(self):
        pass

class KominoSolverUnlimted():

    def __init__(self,kom:komino.Komino,k=5):
        """
        counts number of solutions if unlimited numbers of stones are given

        uses Dynammic Programming 
        """
        #TODO
        self.T = kom.T
        self.k=kom.k
        stone.Stone_config.MaxCacheStoneSize=self.k
        self.DP={}

    def solve(self,ProgressLevel=1,displayBelow=0) -> int:
        #TODO
        self.ProgressLevel=ProgressLevel
        self.displayBelow=displayBelow
        return self._solve(self.T)

    def _solve(self,st:stone.Stone,curLevel=0):
        #TODO
        """
        responsible for normalization
        """
        # Base Case
        if not st:
            return 1

        st=st.normalize()
        if st in self.DP:
            return self.DP[st]
        expPoint=st.good_cut_point()
        candidates=st.get_k_stone_on_tile(expPoint,self.k)

        if curLevel<self.ProgressLevel:
            candidates=tqdm(candidates,desc=f"Level {curLevel}",position=curLevel,leave=(curLevel==0))
        if curLevel<self.displayBelow:
            st.display()
        res=0
        for candidate in candidates:
            remainder=stone.Stone(st-candidate)
            components=remainder.ConectedComponents()
            compSizesModK=map(lambda x:len(x) % self.k,components)
            allZero=all(mod==0 for mod in compSizesModK)
            if not allZero:
                continue
            base=1
            for component in components:
                base*=self._solve(component,curLevel=curLevel+1)
            res+=base
        self.DP[st]=res
        return res
        pass

