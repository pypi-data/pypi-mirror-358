# Count Solutions


# tilingPuzzles

## Finding a solution

``` python
from tilingpuzzles.games.stone import Stone
from tilingpuzzles.games.komino import Komino

# Degree of the stones
# k=5 => Pentomino
k=6

# The Universe of the Coverage problem
U="""
#######
#######
  ###
#######
#######
  ###
  ######
  #######
  #######
"""

U=Stone.from_string(U)

assert len(U)%k==0

display(U)

komi=Komino(U,k=k)
# limits: number of times a stone of a certain shape can be used.
komi.find_solution(limits=1)
```

![](README_files/figure-commonmark/cell-2-output-1.png)

![](README_files/figure-commonmark/cell-2-output-2.png)

    [frozenset({(7, 7), (8, 6), (8, 7), (8, 8), (9, 7), (9, 8)}),
     frozenset({(5, 2), (6, 2), (6, 3), (7, 2), (7, 3), (8, 2)}),
     frozenset({(6, 4), (7, 4), (7, 5), (7, 6), (8, 4), (8, 5)}),
     frozenset({(8, 3), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6)}),
     frozenset({(3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1)}),
     frozenset({(2, 3), (3, 3), (4, 3), (5, 3), (5, 4), (5, 5)}),
     frozenset({(2, 4), (3, 4), (4, 4), (4, 5), (4, 6), (5, 6)}),
     frozenset({(1, 3), (1, 4), (1, 5), (1, 6), (2, 5), (2, 6)}),
     frozenset({(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)})]

Calculate the number of Solutions if every Stone can be used a unlimited
amount of time

``` python
komi.count_solutions(limits=None,progressLevel=0)
```

    115373
