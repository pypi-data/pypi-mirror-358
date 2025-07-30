

# New core data structure
# Wrapp Frozenset


class Core():
    
    def __init__(self,tiles):

        self.tiles=frozenset(tiles)
        pass

    def __hash__(self):
        return hash(self.tiles)
        pass

    def __eq__(self, other):
        return self.tiles ==other.tiles
        pass
    
    def __add__(self,other):
        pass

    def __or__(self, value):
        pass

    def __and__(self,other):
        pass

    def __le__(self,other):
        pass

    def __ge__(self,other):
        pass

    def __sub__(self,other):
        pass

    def __repr__(self):
        return f"Stone({self.tiles})"
        pass






