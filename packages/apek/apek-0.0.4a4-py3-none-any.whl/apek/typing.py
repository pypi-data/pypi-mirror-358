# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring



import time as _time



class BuiltIn():
    NoneType = type(None)



class ApekRoot():
    def __init__(self, *__0, **__1):
        self._createdTime = str(round(_time.time(), 4))
        self.selfname = f"{__name__}.{type(self).__name__}"
    
    def __repr__(self):
        return f"<class {self.selfname} created at {self._createdTime}>"
    
    def __bool__(self):
        return True



class Object(ApekRoot):
    pass

class Number(ApekRoot):
    pass



class Null(Object):
    def __repr__(self):
        return f"<class {self.selfname}>"
    
    def __bool__(self):
        return False
