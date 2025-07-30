
from ..rectangularPentomino import rectangularPentomino

def test_P6x10():
    K=rectangularPentomino.P6x10()
    assert len(K.T) == 60


def test_P5x12():
    K=rectangularPentomino.P5x12()
    assert len(K.T) == 60
    pass



def test_P4x15():
    K=rectangularPentomino.P4x15()
    assert len(K.T) == 60
    pass

def test_P3x20():
    K=rectangularPentomino.P3x20()
    assert len(K.T) == 60
    pass