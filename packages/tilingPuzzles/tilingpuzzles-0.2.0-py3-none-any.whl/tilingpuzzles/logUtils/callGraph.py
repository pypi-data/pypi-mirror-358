
from graphviz import Digraph
from functools import wraps



class GTracker():

    call_graph = Digraph(comment='Function Call Graph')

    stk=["__main__"]

    MAX_CNT=200
    cnt=0


    #@classmethod
    def track_calls(func):
        def wrapper(*args, **kwargs):
            caller = GTracker.stk[-1]
            callee = func.__name__ +f"\n{args =}\n {kwargs =}"
            GTracker.stk.append(callee)

            # Add nodes and edges to graph
            GTracker.call_graph.node(caller)
            GTracker.call_graph.node(callee)
            GTracker.call_graph.edge(caller, callee)
            #break after a certain number of iterations

            GTracker.cnt+=1 
            if GTracker.cnt>=GTracker.MAX_CNT:
                GTracker.render()
                assert False, 'Maximum number of tracked calls reached'
            res= func(*args,**kwargs)
            GTracker.stk.pop()
            return res
        return wrapper
    
    #@classmethod
    def render():
        GTracker.call_graph.render(view=True,engine='dot')

    def clear():
        GTracker.call_graph = Digraph(comment='Function Call Graph')

        GTracker.stk=["__main__"]

