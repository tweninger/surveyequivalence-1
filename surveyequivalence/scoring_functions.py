from abc import ABC, abstractmethod
from typing import Sequence, Dict
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, log_loss, roc_auc_score, accuracy_score
from scipy.stats import entropy
from sklearn.preprocessing import LabelBinarizer
from .combiners import Prediction, DiscreteDistributionPrediction, NumericPrediction


class Scorer(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
                    rater_labels: Sequence[str]) -> float:
        pass

class Correlation(Scorer):

    @staticmethod
    def score(classifier_predictions: Sequence[NumericPrediction],
                        rater_labels: Sequence[float]):
        """
        :param classifier_predictions: numeric values
        :param rater_labels: numeric values
        :return: Pearson correlation coefficient
        """

        return np.corrcoef([p.value for p in classifier_predictions],
                           rater_labels)[1,0]

class AgreementScore(Scorer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
                        rater_labels: Sequence[str]):
        """
        Resolve predictions to identify the most likely single label;
        Return the fraction where predicted matches actual
        >>> AgreementScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'])
        0.6666666666666666

        >>> AgreementScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'])
        0.3333333333333333
        """
        return np.mean([a == b for (a, b) in zip([p.value for p in classifier_predictions],
                                                 rater_labels)])


class CrossEntropyScore(Scorer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
              rater_labels: Sequence[str]):
        """
        Calculates the Cross Entropy of the two labels.

        >>> CrossEntropyScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'])
        0.594597099859

        >>> CrossEntropyScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'])
        0.87702971998
        """

        # diagnostics
        d = [p.probabilities for p in classifier_predictions]
        bad_predictions = [(p, l) for (p, l) in zip(d, rater_labels) if (p[0] < .001 and l=='pos') or (p[0] > .995 and l=='neg')]
        if len(bad_predictions) > 0:
            for p, l in bad_predictions:
                print(p, l)

        d = [[neg_pr, pos_pr] for (pos_pr, neg_pr) in [p.probabilities_with_extremes_cut_off for p in classifier_predictions]]
        # d = [list([p.probabilities[1], p.probabilities[0]]) for p in classifier_predictions]
        try:
            return -log_loss(rater_labels, d, normalize=True, labels=classifier_predictions[0].label_names)/np.log(2)
        except:
            print([(p, l) for (p, l) in zip(d, rater_labels) if p[0] < .001 or p[0] > .995])
            foobar


class PrecisionScore(Scorer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
              rater_labels: Sequence[str], average: str = 'micro') -> float:
        """
        Micro precision score

        >>> PrecisionScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'], 'micro')
        0.6666666666666666
        >>> PrecisionScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'], 'macro')
        0.5

        >>> PrecisionScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'], 'micro')
        0.3333333333333333
        >>> PrecisionScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'], 'macro')
        0.25
        """
        return precision_score(rater_labels, [p.value for p in classifier_predictions], average=average)


class RecallScore(Scorer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
              rater_labels: Sequence[str], average: str = 'micro') -> float:
        """
        Recall

        >>> RecallScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'], 'micro')
        0.6666666666666666
        >>> RecallScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'], 'macro')
        0.5

        >>> RecallScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'], 'micro')
        0.3333333333333333
        >>> RecallScore.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'], 'macro')
        0.25
        """
        return recall_score(rater_labels, [p.value for p in classifier_predictions], average=average)


class F1Score(Scorer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
              rater_labels: Sequence[str], average: str = 'micro') -> float:
        """
        F1 score

        >>> F1Score.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'], 'micro')
        0.6666666666666666
        >>> F1Score.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['b', 'b', 'b'], 'macro')
        0.39759036144

        >>> F1Score.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'], 'micro')
        0.3333333333333333
        >>> F1Score.score([DiscreteDistributionPrediction(['a', 'b'], prs) for prs in [[.3, .7], [.4, .6], [.6, .4]]],  ['a', 'b', 'b'], 'macro')
        0.25
        """
        return f1_score(rater_labels, [p.value for p in classifier_predictions], average=average)


class AUCScore(Scorer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def score(classifier_predictions: Sequence[DiscreteDistributionPrediction],
              rater_labels: Sequence[str]) -> float:
        if len(set(rater_labels)) == 1:
            print("AUC isn't defined for single class")
            return 0
        if len(set(rater_labels)) == 2:
            return roc_auc_score(rater_labels, [p.value_prob for p in classifier_predictions])
        if len(set(rater_labels)) > 2:
            return roc_auc_score(rater_labels, [p.probabilities for p in classifier_predictions], multi_class='ovr', labels=classifier_predictions[0].label_names)