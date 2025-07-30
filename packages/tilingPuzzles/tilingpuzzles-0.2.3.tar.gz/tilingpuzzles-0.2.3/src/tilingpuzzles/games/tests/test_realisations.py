
from tilingpuzzles.games.komino import Komino
from tilingpuzzles.games.realisations import Realisations
from tilingpuzzles.games.stone import Stone

from logging import info 



def test_realisations():

    M=5
    k=5
    komino,used=Komino.generate(M,k)

    # Single tile stone
    s=Stone(((1,1),))

    r=Realisations(komino.T)
    r.add_stone(s)

    # should equal the number of tiles
    info(f"{komino.T = }")
    info(f"{r.indexToReal.values() = }")
    assert len(set(r.indexToReal.values()))== len(komino.T)
    assert len(r.indexToReal) == len(komino.T)

    pass