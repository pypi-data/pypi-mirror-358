#!/usr/bin/env python

import pandas as pd
from time import time
from tilingpuzzles.examples import rectangularPentomino
from tilingpuzzles.examples import scaledStones
from src.tilingpuzzles.solvers.kominoSolver import KominoSolverLimited
from src.tilingpuzzles.solvers.kominoSolver import KominoSolverUnlimted
from tilingpuzzles.games.komino import Komino
from tilingpuzzles.benchmark.git_state import get_git_state
import platform
import cpuinfo
from time import ctime
#from tilingPuzzles.benchmark.timeout import with_timeout
from timeout_decorator import timeout, TimeoutError

timeout_time=300

@timeout(timeout_time)
def _benchmark_unlimited(k:Komino):
    try:
        solver=KominoSolverUnlimted(k)
        t_start=time()
        res=solver.solve()
        t_end=time()
        dt=t_end -t_start
        return dt
    except TimeoutError:
        res=f"timed out after {timeout_time}s"
        print(f"\t>{res}")
        return res
    
@timeout(timeout_time)
def _benchmark_limited(k:Komino):
    try:
        solver=KominoSolverLimited(k,k.unique_stones_dict(1))
        t_start=time()
        res=solver.solve()
        t_end=time()
        dt=t_end -t_start
        return dt
    except TimeoutError:
        res=f"timed out after {timeout_time}s"
        print(f"\t>{res}")
        return res


def _main():
    up_to_date,git_HEAD =get_git_state()
    assert up_to_date, "commit and push before benchmark"
    df=pd.read_csv("./data/timingResulsts.csv",index_col=False)
    #df =pd.DataFrame()
    casesDict={}
    casesDict.update(rectangularPentomino.rectangularPentomino.DICT)
    casesDict.update(scaledStones.scaledStones.DICT)
    for name,gen in casesDict.items():
        print(f"solving {name} unlimeted")
        series=pd.Series({
            "problem name" : name,
            "type":"count solutions",
            "available stones": "unlimited",
            "solver" : KominoSolverUnlimted.__name__,
            "time":_benchmark_unlimited(gen()),
            "date":ctime(time()),
            "cpu" : cpuinfo.get_cpu_info()["brand_raw"],
            "platform" : platform.platform(),
            "git state" : git_HEAD,
             
        })
        new_stuff=pd.DataFrame([series])
        df=pd.concat([df,new_stuff],ignore_index=True)
        


        print(f"solving {name} limited")
  
        series=pd.Series({
            "problem name" : name,
            "type": "find solution",
            "available stones": "limited",
            "solver" : KominoSolverLimited.__name__,
            "time":_benchmark_limited(gen()),
            "date":ctime(time()),
            "cpu" : cpuinfo.get_cpu_info()["brand_raw"],
            "platform" : platform.platform(),
            "git state" : git_HEAD,
             
        })
        new_stuff=pd.DataFrame([series])
        df=pd.concat([df,new_stuff],ignore_index=True)
         

    df.to_csv("./data/timingResulsts.csv",index=None)





if __name__=="__main__":
    _main()
    




