
from tilingpuzzles.games.tile import Tile
import pytest

def test_tile():

    t=Tile((0,1))
    n=t.get_neighbores()
    assert len(n)==4, "this tile should have 4 neighbores"

    # 3D
    t=Tile((1,2,3))
    n=t.get_neighbores()
    assert len(n)==6, "3D => 6 faces"

    # trap
    t=Tile((0,0))
    n=t.get_neighbores(lowerB=(0,0),upperB=(1,1))
    assert len(n)==0, f"All blocked\n {n =}"