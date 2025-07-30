
from __future__ import annotations
import numpy as np

from tilingpuzzles.visualize.visualize import Visualize
from tilingpuzzles.logUtils.callGraph import GTracker
import queue

from . import stone,tile

from logging import info



class Stone_Symetries(list):

    def __init__(self,symertries=None):
        super().__init__()

        if symertries is None:
            symertries=[

                Stone_Symetries.rotate,
                Stone_Symetries.flip
            ]
        self+=symertries    
        

    def __call__(self,stone:Stone):
        res=set()
        checkStack=[stone.shift_positive()]
        while checkStack:
            front=checkStack.pop()
            if front in res:
                continue
            res.add(front)
            for sym in self:
                new_st:Stone=sym(front)
                checkStack.append(new_st.shift_positive())
        return res

        pass


    def rotate(stone:Stone) -> Stone:
        new_tiles=[ (ty,-tx) for (tx,ty) in stone]
        return Stone(new_tiles)
    
    def flip(stone:Stone) -> Stone:
        new_tiles=[(tx,-ty) for (tx,ty) in stone]
        return Stone(new_tiles) 
    
    pass

class Stone_config():
    K_STONE_MAX_LAYER_SIZE=1000
    # Maximum number of stones in a layer until a assertion error is trown
    SYMS=Stone_Symetries()
    MaxCacheStoneSize:int=0

class Stone(frozenset):
    """
    Frozen set of tiles
    All sets of tiles are considered as a stone
    """
    # change to frozenset to make it hashable

    _NormalizeCache={}

    def __new__(cls,*tiles):
        tiles=map(tile.Tile,*tiles)
        return super(Stone,cls).__new__(cls,tiles)
    
    def __init__(self,*tiles):
        super().__init__()
        pass

    
    def normalize(self) -> Stone:
        #TODO Optimize, use bounding first, avoid generating all symetries at all cost
        # Use dictionary to cache

        #WARNING slow
        if len(self)<=Stone_config.MaxCacheStoneSize:
            positive=self.shift_positive()
            if positive in Stone._NormalizeCache:
                return Stone._NormalizeCache[positive]
            #BUG not done jet
        syms=self.get_symetries()
        syms=list(syms)
        syms.sort(key=hash)
        res=syms[0]
        if len(self)<Stone_config.MaxCacheStoneSize:
            Stone._NormalizeCache.update({sym:res for sym in syms})
        assert syms
        return res
 
    
    #@GTracker.track_calls
    def shift_positive(self):
        # TODO use self.shift
        sx=[t[0] for t in self]
        sx=np.array(sx)
        sy=[t[1] for t in self]
        sy=np.array(sy)
        
        sy-=min(sy)
        sx-=min(sx)

        return Stone(zip(sx,sy))
    
    def shift(self,dx,dy) -> Stone :
        # TODO ditch numpy
        """
        Creates a new stone that is shiftet dx and dy
        """
        sx=[t[0] for t in self]
        sx=np.array(sx)
        sy=[t[1] for t in self]
        sy=np.array(sy)
        sx+=dx
        sy+=dy
        return Stone(zip(sx,sy))

    @property
    def bounding_Box(self):
        """
        upper bounds not included
        (xmin,ymin),(xmax,ymax)
        """
        assert self
        for t in self:
            min_vals=list(t)
            max_vals=list(t)
            break       

        for tile in self:
            for i,cord in enumerate(tile):
                min_vals[i]=min(min_vals[i],cord)
                max_vals[i]=max(max_vals[i],cord)

        return tuple(min_vals),tuple(max_vals)


    def to_mask(self,n=None ,m=None):
        sx=[t[0] for t in self]
        sy=[t[1] for t in self]
         
        if n==None:
            n=max(sx)+1
        if m== None:
            m=max(sy)+1
        mask=np.zeros((n,m))
        mask[sx,sy]=1
        return mask
    

    def display(self):
        Visualize.draw_stone(st=self)
    # make it default for ipynb
    def _ipython_display_(self):
        self.display()


    def splitConnected(self) -> tuple[Stone,Stone]:
        # Flood fill
        #TODO Stone -> isConected

        toCheck:list[tile.Tile]=[self.get_any_tile()]
        found:set[tile.Tile]=set()
        
        while toCheck:
            front=toCheck.pop()
            if front in found:
                continue
            found.add(front)
            toCheck+=list(front.get_neighbores() & self)

        connected=Stone(found)
        reminder=Stone(self - connected)

        return connected, reminder

        pass

    def isConected(self) -> bool:
        if not self:
            return True
        _,reminder=self.splitConnected()
        return not reminder
    
    def ConectedComponents(self) -> set[Stone]:
        reminder=self
        res=set()
        while reminder:
            split,reminder=reminder.splitConnected()
            res.add(split)
        return res    



    #@GTracker.track_calls
    def outer_bound(self,allow_diag=False) -> Stone:
        res=set()
        for t in self:
            res.update(stone.Stone.get_neighbores(t,allow_diag=allow_diag))

        res -=self
        return Stone(res)
    
    #@GTracker.track_calls
    def inner_bound(self) -> Stone:

        res=set()

        for t in self:
            t:tile.Tile
            if not t.get_neighbores() <= self:
                res.add(t)
        
        return Stone(res)

    
    #@GTracker.track_calls
    def get_k_stone_on_tile(self,t,k=5) -> set[Stone]:
        res = self._k_stone_subtree(Stone({t}),Stone(tuple()),Stone(tuple()),k=k)
        return set(res)

        
    
    def _layer_wise_expansion(self,t,k=5):

        # coplexity replaced by _k_stone_subtree
        # Solution recursive Decision Tree
        #  - in Substone, not in Substone

        res=set()
        if not t in self:
            return res
        
        cur_layer={Stone((t,))}

        for i in range(1,k):
            next_layer=set()
            for cur in cur_layer:
                cur:Stone
                for boundTile in cur.outer_bound():
                    if boundTile in self:
                        next_layer.add(Stone(cur | {boundTile} ))

            assert  len(next_layer)<=Stone_config.K_STONE_MAX_LAYER_SIZE,'COMPLEXITY !!! To many possible stones'
            cur_layer=next_layer


        return cur_layer
    
    def _k_stone_subtree(self,inSubtree:Stone,notInSutree:Stone,bound:Stone,k=5):
        if len(inSubtree)==k:
            return [inSubtree]
        if not bound:
            bound=inSubtree.outer_bound()
            bound&=self
            bound-=notInSutree
            bound=Stone(bound)
        if not bound:
            return []
        
        expPoint=bound.get_any_tile()
        res=[]
        new_bound=Stone(bound-{expPoint})

        # All Stones that contain the expansion Point
        res+=self._k_stone_subtree(
            Stone(inSubtree |{expPoint} ),
            notInSutree,
            new_bound,
            k
        )
        # All Stones that dont contain the expansion Point
        res += self._k_stone_subtree(
            inSubtree,
            Stone(notInSutree | {expPoint}),
            new_bound,
            k
        )


        return res



    

    def get_symetries(self):
        return Stone_config.SYMS(self)
    
    def get_any_tile(self):
        for tile in self:
            return tile

    def getMinTile(self):
        assert self
        minTile= self.get_any_tile()

        for t in self:
            if t<minTile:
                minTile= t
        return minTile

    def from_string(s:str) -> Stone:
        lines=s.splitlines()
        res=set()

        for i, l in enumerate(lines):
            for j,c in enumerate(l):
                if c.strip():
                    res.add((i,j))
        return Stone(res)
    

    def good_cut_point(self,epsi=0.1,perc=0.1,offset=1)-> tuple[int,int]:
        #TODO
        #if len(self)<15:
        #    return self.getMinTile()
        
        outerBound=self.outer_bound(allow_diag=True)
        delta=lambda a,b: int(abs(a-b)*perc/2+offset)
        split=lambda a,b: (a+delta(a,b),b-delta(a,b))

        ((xmin,ymin),(xmax,ymax))=outerBound.bounding_Box
        x_self_bound,y_self_bound=self.bounding_Box

        cases=(
            (split(xmin,xmax),(ymin,ymax)),
            ((xmin,xmax),split(ymin,ymax))
        )
        points_and_costs=[]
        for c in cases:
            (x1,x2),(y1,y2)=c
            #info(f" bounds = {c =} ")
            if not (x1<= x2 and y1 <= y2):
                continue
            substone=outerBound.clip_to_bounds(x1,x2,y1,y2)
            #substone.display()
            components =list(substone.ConectedComponents())
            assert components
            max_edge=[ (comp._max_edge_value() ,comp) for comp in components  ]
            min_edge=[ (comp._min_edge_value() ,comp) for comp in components  ]

            _,starts=max(max_edge)
            _,ends=min(min_edge)
            starts-=ends
            ends -= starts
            if not starts:
                #starts=stone.Stone(starts)
                info(f"{substone = }")
                substone.display()
                info(f"{self = }")
                self.display()
            assert starts
            assert ends


            #starts.display()
            #ends.display()
            pac=self._nearest_endpoint_from_inner_AStar(
                starts=starts,
                ends=ends,
                epsi_cost=epsi
                )
            cost,t =pac
            #happends somehow
            assert t in self
            points_and_costs.append(pac)
        #info(f"{points_and_costs = }")
        if not points_and_costs:
            return self.getMinTile()
        elif len(points_and_costs)==1:
            cost,t= points_and_costs[0]
            return t
        else:
            cost,t=min(*points_and_costs)
            return t

        


    
    def _nearest_endpoint_from_inner_AStar(
            self,
            starts:stone.Stone,
            ends:stone.Stone,
            epsi_cost=0.3,
            phase_change_cost=0.75,
            dist_center_of_mass_cost=1
            ) -> tuple[float,tuple]:
        """
        returns
        - end_tile 
            - optimal tile in ends
        - cost 
            - cost for making a cut from starts to ends
        epsi_cost: cost for moving outside the tile >0
        phase_change_cost: cost for going from outside to inside or inside to outside
        """
        assert starts
        assert ends

        xCenter=sum([x for x,y in self])
        yCenter=sum([y for x,y in self])
        xCenter/=len(self)
        yCenter/=len(self)
        (xmin,ymin),(xmax,ymax)=self.bounding_Box
        diameter=xmax-xmin+ymax-ymin



        
        pq=queue.PriorityQueue()

        for start in starts:
            pq.put((0,0,start,start))
        visited=set()
        min_dist= lambda x,y: epsi_cost*min([ abs(x -x_) +abs(y-y_) for x_,y_ in ends  ])
        distance_com_cost=lambda x,y: (abs(x -xCenter)+abs(y-yCenter))*dist_center_of_mass_cost/diameter
        min_steps=lambda min_dist,t: min(min_dist,int(abs(t[0]-xCenter))+int(abs(t[1]-yCenter)))
        heuristic_distance_com_cost=lambda steps:  steps*(steps+1)/2*dist_center_of_mass_cost/diameter
        while(pq.not_empty):
            front=pq.get()

            _,front_cost,front_item,prev=front # _ = heuristic
            if front_item in ends and tile.Tile(prev) in self:
                #TODO remove Tile this is why this Tile/tuple has to be split
                x,y=prev
                return   front_cost,(x,y)
            if front_item in ends:
                continue
            
            if front_item in visited:
                continue
            #info(f"{front}")
            visited.add(front_item)

            neighbores=stone.Stone.get_neighbores(front_item)
            for neigbore in neighbores:
                if neigbore in visited:
                    continue
                front_in_stone=front_item in self
                next_in_stone=neigbore in self
                
                #TODO add distance cost, reduces number of stones visited

                next_cost=front_cost + distance_com_cost(*neigbore)
                match (front_in_stone,next_in_stone):
                    case (True,True):
                        next_cost+=1
                    case (False,False):
                        next_cost+=epsi_cost
                    case (True,False):
                        next_cost+=phase_change_cost+epsi_cost
                    case (False,True):
                        next_cost+=1
                    case _:
                        assert False, "Unreachable"
                dst=min_dist(*neigbore)
                steps=min_steps(dst,neigbore)
                next_heuristic=next_cost+dst+ heuristic_distance_com_cost(dst)
                #Todo min cost for distance cost
                assert next_heuristic>=0
                pq.put((next_heuristic,next_cost,neigbore,front_item))

        assert False ,"Unreachable"
            


    def clip_to_bounds(self,xmin,xmax,ymin,ymax)-> Stone:
        """
        returns a stone cliped to bounds
        """
        res =set()
        #TODO
    
        for t in self:
            t:tile.Tile
            x,y=t 
            inBounds=xmin <= x and x <= xmax
            inBounds &= ymin <= y and y <= ymax
            if inBounds:
                res.add(t)
        return Stone(res)
    
            
  
    def get_neighbores(tile:tuple,lowerB=None,upperB=None,allow_diag=False) -> stone.Stone:
        res=[]
        x,y=tile
        if not allow_diag:
            delta_neig=(
            (1,0),(-1,0),(0,1),(0,-1)       
            )
        else:
            delta_neig=(
                (1,0),(-1,0),(0,1),(0,-1),
                (1,1),(-1,-1),(1,-1),(-1,1)       
            )

        for dx,dy in delta_neig:
            res.append((x+dx,y+dy))

        return stone.Stone(res)
    
    def _min_edge_value(self):
        x,y =self.get_any_tile()
        res=x+y
     
        for x,y in self:
            res=min(res,x+y)
        return res
    
    def _max_edge_value(self):
        x,y =self.get_any_tile()
        res=x+y
     
        for x,y in self:
            res=max(res,x+y)
        return res










