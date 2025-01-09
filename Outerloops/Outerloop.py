from abc import ABCMeta, abstractmethod

class Outerloop(metaclass = ABCMeta):

    def __init__(self, innerloop_params, outerloop_params):
        pass
  
    @abstractmethod
    def run(self, n_meta_it):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def plot(self):
        self.innerloop.plot_optimization(self.rule_hist, self.loss_hist, self.current_meta_it, self.lr)
        pass