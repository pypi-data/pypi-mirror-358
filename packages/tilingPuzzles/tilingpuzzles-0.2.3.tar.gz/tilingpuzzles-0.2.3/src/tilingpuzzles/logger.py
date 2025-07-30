
import logging

class Logger():



    def __init__(self,other):
        self.LogOff=True
        self.other=other
        pass
    
    def WARN(self,*args,**kwargs):
         if self.LogOff:
             return
         else:
             msg,*args=args
             logging.warning(f"obj {self.other} says:\n\t{msg}")
         
    def INFO(self,*args,**kwargs):
         if self.LogOff:
             return
         else:
             msg,*args=args
             logging.INFO(f"obj {self.other} says:\n\t{msg}")
    
    def with_loging(f):
        
        def new_f(other,*args,**kwarsg):
            other.LOG.OFF=False
            res=f(other,*args,**kwarsg)
            other.LOG.OFF=True
            return res 
        return  new_f
            



         
