import torch
from collections import Counter

from ._DecisionTree import DecisionTree
from ....Exceptions import NotFittedError


class RandomForestClassifier:
    """
    RandomForestClassifier implements a classification algorithm fitting many :class:`DecisionTrees <DLL.MachineLearning.SupervisedLearning.Trees.DecisionTree>` to bootstrapped data.

    Args:
        n_trees (int, optional): The number of trees used for predicting. Defaults to 10. Must be a positive integer.
        max_depth (int, optional): The maximum depth of the tree. Defaults to 10. Must be a positive integer.
        min_samples_split (int, optional): The minimum required samples in a leaf to make a split. Defaults to 2. Must be a positive integer.
    """
    def __init__(self, n_trees=10, max_depth=10, min_samples_split=2):
        if not isinstance(n_trees, int) or n_trees < 1:
            raise ValueError("n_trees must be a positive integer.")
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ValueError("max_depth must be a positive integer.")
        if not isinstance(min_samples_split, int) or min_samples_split < 1:
            raise ValueError("min_samples_split must be a positive integer.")
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = [DecisionTree(max_depth=max_depth, min_samples_split=min_samples_split) for _ in range(n_trees)]

    def fit(self, X, y):
        """
        Fits the RandomForestClassifier model to the input data by generating trees, which split the data appropriately.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data, where each row is a sample and each column is a feature.
            y (torch.Tensor of shape (n_samples,)): The labels corresponding to each sample.
        Returns:
            None
        Raises:
            TypeError: If the input matrix or the label matrix is not a PyTorch tensor.
            ValueError: If the input matrix or the label matrix is not the correct shape.
        """
        if not isinstance(X, torch.Tensor) or not isinstance(y, torch.Tensor):
            raise TypeError("The input matrix and the label matrix must be a PyTorch tensor.")
        if X.ndim != 2:
            raise ValueError("The input matrix must be a 2 dimensional tensor.")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError("The labels must be 1 dimensional with the same number of samples as the input data")
        for tree in self.trees:
            tree.fit(*self._bootstrap_sample(X, y))

    def predict(self, X):
        """
        Applies the fitted RandomForestClassifier model to the input data, predicting the correct classes.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data to be classified.
        Returns:
            labels (torch.Tensor of shape (n_samples,)): The predicted labels corresponding to each sample.
        Raises:
            NotFittedError: If the RandomForestClassifier model has not been fitted before predicting.
            TypeError: If the input matrix is not a PyTorch tensor.
            ValueError: If the input matrix is not the correct shape.
        """
        if self.trees is None:
            raise NotFittedError("RandomForestClassifier.fit() must be called before predicting.")
        if not isinstance(X, torch.Tensor):
            raise TypeError("The input matrix must be a PyTorch tensor.")
        if X.ndim != 2 or X.shape[1] != self.trees[0].n_features:
            raise ValueError("The input matrix must be a 2 dimensional tensor with the same number of features as the fitted tensor.")
        predictions = torch.stack([tree.predict(X) for tree in self.trees]).T
        return torch.tensor([Counter(sample_prediction).most_common(1)[0][0] for sample_prediction in predictions])
    
    def predict_proba(self, X):
        """
        Applies the fitted RandomForestClassifier model to the input data, predicting the probabilities of each class. Is calculated as the average of each individual trees predicted probabilities.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data to be classified.
        Returns:
            probabilities (torch.Tensor of shape (n_samples, n_classes)): The predicted probabilities corresponding to each sample.
        Raises:
            NotFittedError: If the RandomForestClassifier model has not been fitted before predicting.
            TypeError: If the input matrix is not a PyTorch tensor.
            ValueError: If the input matrix is not the correct shape.
        """
        if self.trees is None:
            raise NotFittedError("RandomForestClassifier.fit() must be called before predicting.")
        if not isinstance(X, torch.Tensor):
            raise TypeError("The input matrix must be a PyTorch tensor.")
        if X.ndim != 2 or X.shape[1] != self.trees[0].n_features:
            raise ValueError("The input matrix must be a 2 dimensional tensor with the same number of features as the fitted tensor.")
        return torch.stack([tree.predict_proba(X) for tree in self.trees]).mean(dim=0)

    def _bootstrap_sample(self, X, y):
        indices = torch.randint(high=len(y), size=(len(y), 1)).flatten()
        return X[indices], y[indices]
