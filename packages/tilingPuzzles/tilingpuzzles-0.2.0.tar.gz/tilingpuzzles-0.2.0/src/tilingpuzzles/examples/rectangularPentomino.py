
from tilingpuzzles.games.komino import Komino



def _nxm(n,m):

    res =set()
    for i in range(n):
        for j in range(m):
            res.add((i,j))

    return Komino(res,k=5)


class rectangularPentomino():

    

    def P6x10() -> Komino:
        return _nxm(6,10)
    
    def P5x12() -> Komino:
        return _nxm(5,12)
        pass

    def P4x15() -> Komino:
        return _nxm(4,15)
        pass

    def P3x20()-> Komino:
        return _nxm(3,20)
        pass

    DICT={
        "P6x10":P6x10,
        "P5x12":P5x12,
        "P4x15":P4x15,
        "P3x20":P3x20,
    }