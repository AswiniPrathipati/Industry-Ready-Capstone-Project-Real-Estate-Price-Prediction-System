"""
Shared model-registry class definitions.

Both the training pipeline (ml-pipeline/training/train_models.py) and the
serving layer (backend/services/prediction_service.py) import
EnsembleWrapper from this single location. This avoids the classic
"pickle can't find class __main__.EnsembleWrapper" failure that happens
when a class used inside a pickled object only exists in the script
that created it.
"""
import numpy as np


class EnsembleWrapper:
    """Averages predictions from multiple fitted sklearn-style pipelines."""

    def __init__(self, pipes):
        self.pipes = pipes

    def predict(self, X):
        preds = np.column_stack([p.predict(X) for p in self.pipes])
        return preds.mean(axis=1)
