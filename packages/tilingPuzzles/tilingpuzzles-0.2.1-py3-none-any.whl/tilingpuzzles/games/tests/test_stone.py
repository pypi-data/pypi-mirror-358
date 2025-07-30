
import sys
sys.path.insert(0, '.')
from tqdm import tqdm

from tilingpuzzles.games.stone import Stone, Stone_Symetries
from tilingpuzzles.games.tile import Tile
from tilingpuzzles.logUtils.callGraph import GTracker
from tilingpuzzles.games.komino import Komino
from tilingpuzzles.visualize.visualize import Visualize

from logging import info
from time import sleep


def test_stone():
    n=10
    A=set([(i//2,i) for i in range(10)])
    s=Stone(A)
    msk=s.to_mask(n,n)
    
    assert msk.any()
    assert s==A
    
    s=Stone(((1,1),))
    s2=s.shift(4,4)

    assert s.bounding_Box == ((1,1),(1,1))
    assert s.bounding_Box == ((1,1),(1,1))



def test_boundary():

    s=Stone(((0,0),))

    assert s.outer_bound() == frozenset(((1,0),(-1,0),(0,1),(0,-1)))
    assert s.inner_bound()==s



def test_substones():
    seed=Tile((0,0))
    s=Stone((seed,))

    for i in range(2):
        s=Stone(s | s.outer_bound())
        n=len(s)
        subs=s.get_k_stone_on_tile(seed,n)
        assert s == list(subs)[0]


def test_normalize():
    st=Stone(
        [
            (2,3),
            (4,5),
            (3,4),
            (22,5)
        ]
    )

    norm=st.normalize()
    assert len(st) == len(norm)

    for i in range(1,10):
        norm2=st.shift(i,i).normalize()
        assert norm==norm2
        

def test_symetries():
    st=Stone([(0,0)])
    get_symetries=Stone_Symetries()

    sym=get_symetries(st)

    assert len(sym)==1

    st=Stone([(0,1),(0,0)])
    sym=get_symetries(st)
    assert len(sym)==2

    st=Stone([(2,1),(1,1),(0,1),(0,0)])
    sym=get_symetries(st)
    assert len(sym)==8



def test_clip_to_Bounds():
    N=10
    s=Stone(((i,i) for i in range(N)))

    s2=s.clip_to_bounds(0,N,0,N)
    assert s == s2 

    for i in range(N):

        s3=s.clip_to_bounds(0,i-1,0,i-1)
        assert len(s3)==i


def test_split_point():
    # test if method finds the split point
    sstring="""
        #########################
        ######splitpoint#########
                    v
        #########################
        #########################
    """
    s:Stone=Stone.from_string(sstring)
    #s.display()
    split_tile= s.good_cut_point()
    new_stone=Stone(s-{split_tile})
    componets=new_stone.ConectedComponents()
    assert len(componets)==2


def test_split_point_random():
    for i in tqdm(range(100)):
        
        k,_=Komino.generate(30,5)
        s=k.T
        assert s
        assert s.isConected()
        loop_runs=False
        while(s and s.isConected()):
            last_size=len(s)
            p=s.good_cut_point(perc=0.5,offset=3)

            match p:
                case (int(), int()):
                    pass
                case _:
                    assert False

            s=Stone(s-{p})
            assert len(s)==last_size -1
            loop_runs=True
        assert loop_runs
    #return
    #visual
    # test spliting of random generated stones
    for i in tqdm(range(10)):
        
        k,_=Komino.generate(100,5)
        s=k.T
        assert s
        assert s.isConected()
        loop_runs=False
        vz=Visualize()
        vz.add_stone(s)
        while(s and s.isConected()):
            last_size=len(s)
            p=s.good_cut_point(perc=0.5,offset=3)
            vz.add_stone(Stone({p}))
            

            match p:
                case (int(), int()):
                    pass
                case _:
                    assert False

            s=Stone(s-{p})
            assert len(s)==last_size -1
            loop_runs=True
        vz.render()
        assert loop_runs
        


