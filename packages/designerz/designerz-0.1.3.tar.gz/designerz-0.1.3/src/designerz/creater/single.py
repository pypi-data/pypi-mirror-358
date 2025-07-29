""" 单例模式 """

class Singleton():
    # 全局只初始化一次 一个类只能存在一个实例 底层内存共享
    def __init__(self,class_name:str = "Init"):
        self.p = f"""
class {class_name}:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,value = None):
        # 只有第一次初始化时设置值，后续的初始化调用不会更改实例的值
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.value = value

setting = {class_name}()
del {class_name}

"""
    def __repr__(self):
        return self.p