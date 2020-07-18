from abc import ABC, abstractmethod
from typing import Sequence, Dict
import numpy as np
import pandas as pd
from .combiners import DiscreteDistributionPrediction

########### States #############################

class State:

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def draw_labels(self, n):
        pass


class DiscreteState(State):

    def __init__(self,
                 state_name: str,
                 labels: Sequence[str],
                 probabilities: Sequence[float],
                 num_raters: int=0
                 ):
        super().__init__()
        self.state_name = state_name
        self.labels = labels
        self.probabilities = probabilities
        self.num_raters = num_raters

    def __repr__(self):
        return f"DiscreteState {self.state_name} based on {self.num_raters}: {list(zip(self.labels, self.probabilities))}"

    def pr_dict(self):
        return {l: p for (l, p) in zip(self.labels, self.probabilities)}

    def draw_labels(self, n: int):
        return np.random.choice(
            self.labels,
            n,
            p=self.probabilities
        )

############ Distributions over states ###############

class DistributionOverStates(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def draw_states(self, n: int):
        pass


class DiscreteDistributionOverStates(DistributionOverStates):
    def __init__(self, states: Sequence[State], probabilities: Sequence[float]):
        super().__init__()
        self.probabilities = probabilities
        self.states = states

    def draw_states(self, n: int) -> Sequence[DiscreteState]:
        return np.random.choice(
            self.states,
            size=n,
            p=self.probabilities
        )

class DiscreteLabelsWithNoise(DiscreteDistributionOverStates):
    def __init__(self, states: Sequence[DiscreteState], probabilities: Sequence[float]):
        # check that state names match the label names
        labels_names = [s.state_name for s in states]
        for s in states:
            assert s.labels == labels_names

        # if so, this fits the discrete labels with noise model
        super().__init__(states, probabilities)



class MixtureOfBetas(DistributionOverStates):
    def __init__(self):
        super().__init__()
        pass

    def draw_states(self, n) -> Sequence[DiscreteState]:
        pass



# def generate_labels(item_states: Sequence[State], num_labels_per_item=10):
#     return pd.DataFrame(
#         [state.draw_labels(num_labels_per_item) for state in item_states],
#         columns = ["r{}".format(i) for i in range(1, num_labels_per_item+1)]
#     )

