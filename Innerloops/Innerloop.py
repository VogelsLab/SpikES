from abc import ABCMeta, abstractmethod

class Innerloop(metaclass = ABCMeta):

    @abstractmethod
    def score(self, A):
        pass

    @abstractmethod
    def __str__(self):
        pass
    
    @abstractmethod
    def plot_optimization(self, rule_hist, loss_hist, n_meta_it, lr):
        pass