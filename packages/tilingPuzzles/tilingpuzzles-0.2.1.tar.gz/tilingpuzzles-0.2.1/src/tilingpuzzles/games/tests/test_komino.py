
from tilingpuzzles.games.komino import Komino

import logging

def test_komino():
    Komino(TilesToFill={(1,0),(0,1)})
    Komino.generate(M=10)
    pass
    


def test_generate():

    for i in range(2,4):
        for j in range(2,4):
            game,used =Komino.generate(i,j)
            assert len(game.T)==i*j


def test_mask():

    komi,used=Komino.generate(5,5)

    assert komi.to_mask().sum().sum() == len(komi.T), "tiles should be preserved"


def test_unique_stones():
    k =Komino(())
    assert len(k.unique_stones())==12