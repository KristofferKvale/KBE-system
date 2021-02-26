# Imports


# Rules class
class Rule():
    def __init__(self,func, limit, param_descriptor, descriptor):
        self.func = func
        self.limit = limit
        self.param_descriptor = param_descriptor
        self.descriptor = descriptor
    
    def __str__(self):
        return self.descriptor
    
    def eval(self, params):
        param = params[self.param_descriptor]
        if self.func == "LT":
            return param <= self.limit
        elif self.func == "lt":
            return param < self.limit
        elif self.func == "GT":
            return param >= self.limit
        elif self.func == "gt":
            return param > self.limit


chair_rules = [Rule("GT", 50, "sitting_height", "Lower limit of sitting height"),
               Rule("LT", 80, "sitting_height", "Upper limit of sitting height"),
               Rule("GT", 5, "back_angle", "Lower limit of back angle"),
               Rule("LT", 15, "back_angle", "Upper limit of back angle")]


def eval_chair(sitting_height, back_angle):
    params = {"sitting_height":sitting_height, "back_angle":back_angle}
    for chair_rule in chair_rules:
        if not chair_rule.eval(params):
            return False
    return True
