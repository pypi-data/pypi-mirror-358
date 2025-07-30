
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
#from tilingPuzzles.games.stone import Stone
import numpy as np

class Visualize():

    def __init__(self,figure=None,ax=None):
        self.n =0
        if ax is None:
            ax=plt.subplot()
            ax.set_aspect("equal")
        
        self.figure=figure
        self.ax: Axes=ax
        

    def add_stone(self,stone,fill=None):
        if fill is None:
            fill=self.get_nth_color()
        
        for tile in stone:

            rc=Rectangle(tile,1,1,edgecolor="black",facecolor=fill,lw=1.5)
            self.ax.add_patch(rc)
            self.ax.autoscale_view()

    def update_stones(self,stones):
        for stone in stones:
            self.add_stone(stone=stone)

    def get_nth_color(self,n=None):
        if n is None:
            n=self.n 
            self.n+=1

        pi=np.pi
        sin=np.sin
        shift=2
        color=[ sin(shift*n+pi/4*i)**2 for i in range(3)  ]
        s=sum(color)
        color = [c/s for c in color]
        color= "#"+"".join(f"{int(c*16**2):02x}" for c in color)
        return color



    def draw_stone(st):
        st=st.shift_positive()
        msk=st.to_mask()

        plt.imshow(msk)
        plt.show()

        pass

    def render(self):
        plt.show()

