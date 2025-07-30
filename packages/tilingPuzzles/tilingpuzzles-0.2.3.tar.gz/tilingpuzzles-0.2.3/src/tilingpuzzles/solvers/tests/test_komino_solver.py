
from tilingpuzzles.games import komino as _komio
from src.tilingpuzzles.solvers.kominoSolver import KominoSolverLimited
from tilingpuzzles.games.stone import Stone

from logging import info



def test_KominoSolverLimited():
    Komino=_komio.Komino

    N=15

    for k in range(2,6):
        komino,stonesAllowed=Komino.generate(N,k)

        solver=KominoSolverLimited(komino,stonesAllowed)
        solution = solver.solve()
        info(f"{solution = }")
        assert solution

        res=set()
        for st in solver.solution:
            res |= st
        res = Stone(res)
        assert res == komino.T

def test_KominSolverUnlimited():
    assert False, "not implementet test !"