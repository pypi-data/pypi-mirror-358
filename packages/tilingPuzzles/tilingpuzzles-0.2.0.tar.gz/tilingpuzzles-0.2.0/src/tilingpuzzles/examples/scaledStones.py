
from tilingpuzzles.games.stone import Stone
from tilingpuzzles.games.komino import Komino

def _scale(stone:Stone)->Stone:
    res=set()
    for tile in stone:
        x,y=tile
        for dx in range(3):
            for dy in range(3):
                res.add((3*x+dx,3*y+dy))
    return Stone(res)

_F="""

 ##
##
 #

"""

_L="""

#
#
#
##

"""

_N="""

 #
##
#
#

"""

_P="""

##
##
#

"""

_Y="""

 #
##
 #
 #

"""

_T="""

###
 #
 #

"""

_U="""

# #
###

"""

_V="""

#
#
###

"""

_W="""

#
##
 ##

"""

_Z="""

##
 #
 ##

"""

class scaledStones():

    def F_shape():
        s=Stone.from_string(_F)
        s=_scale(s)
        return Komino(s,5)
    
    def L_shape():
        s=Stone.from_string(_L)
        s=_scale(s)
        return Komino(s,5)
    
    def N_shape():
        s=Stone.from_string(_N)
        s=_scale(s)
        return Komino(s,5)

    def P_shape():
        s=Stone.from_string(_P)
        s=_scale(s)
        return Komino(s,5)
    
    def Y_shape():
        s=Stone.from_string(_Y)
        s=_scale(s)
        return Komino(s,5)

    def T_shape():
        s=Stone.from_string(_T)
        s=_scale(s)
        return Komino(s,5)

    def U_shape():
        s=Stone.from_string(_U)
        s=_scale(s)
        return Komino(s,5)

    def V_shape():
        s=Stone.from_string(_V)
        s=_scale(s)
        return Komino(s,5)


    
    def W_shape():
        s=Stone.from_string(_W)
        s=_scale(s)
        return Komino(s,5)
    
    def Z_shape():
        s=Stone.from_string(_Z)
        s=_scale(s)
        return Komino(s,5)

    DICT={
        "F_shape":F_shape,
        "L_shape":L_shape,
        "N_shape":N_shape,
        "P_shape":P_shape,
        "Y_shape":Y_shape,
        "T_shape":T_shape,
        "U_shape":U_shape,
        "V_shape":V_shape,
        "W_shape":T_shape,
        "Z_shape":Z_shape,
    }
        
        
