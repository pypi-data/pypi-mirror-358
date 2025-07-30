
from ..scaledStones import scaledStones


def test():
    for name,pent in scaledStones.DICT.items():
        assert len(pent().T)==3*3*5, f"check {name}"
    