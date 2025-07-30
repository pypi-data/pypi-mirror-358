import torch

from ._LGBMTree import _LGBMTree, _ExclusiveFeatureBundling
from ....DeepLearning.Losses import MSE, MAE, Huber
from ....Exceptions import NotFittedError
from ....Data.Metrics import calculate_metrics


class LGBMRegressor:
    """
    LGBMRegressor implements a regression algorithm fitting many consecutive trees to gradients and hessians of the loss function. The algorithm is based on `this paper <https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf>`_.

    Args:
        n_trees (int, optional): The number of trees used for predicting. Defaults to 50. Must be a positive integer.
        learning_rate (float, optional): The number multiplied to each additional trees residuals. Must be a real number in range (0, 1). Defaults to 0.5.
        max_depth (int, optional): The maximum depth of the tree. Defaults to 3. Must be a positive integer.
        min_samples_split (int, optional): The minimum required samples in a leaf to make a split. Defaults to 2. Must be a positive integer.
        n_bins (int, optional): The number of bins used to find the optimal split of data. Must be greater than 1. Defaults to 30.
        reg_lambda (float | int, optional): The regularisation parameter used in fitting the trees. The larger the parameter, the smaller the trees. Must be a positive real number. Defaults to 1.
        gamma (float | int, optional): The minimum gain to make a split. Must be a non-negative real number. Defaults to 0.
        large_error_proportion (float, optional): The proportion of the whole data with the largest error, which is always used to train the next weak learner. Defaults to 0.3.
        small_error_proportion (float, optional): The proportion of data randomly selected from the remaining (1 - large_error_proportion) percent of data to train the next weak learner. Defaults to 0.2.
        loss (string, optional): The loss function used in calculations of the gradients and hessians. Must be one of "squared", "absolute" or "huber". Defaults to "squared".
        huber_delta (float | int, optional): The delta parameter for the possibly used huber loss. If loss is not "huber", this parameter is ignored.
        max_conflict_rate (float, optional): The proportion of samples, which are allowed to be nonzero without featuers being bundled. Is ignored if use_efb=False. Defaults to 0.0.
        use_efb (bool, optional): Determines if the exclusive feature bundling algorithm is used. Defaults to True.
    Attributes:
        n_features (int): The number of features. Available after fitting.
    """
    def __init__(self, n_trees=50, learning_rate=0.5, max_depth=3, min_samples_split=2, n_bins=30, reg_lambda=1, gamma=0, large_error_proportion=0.3, small_error_proportion=0.2, loss="squared", huber_delta=1, max_conflict_rate=0.0, use_efb=True):
        if not isinstance(n_trees, int) or n_trees < 1:
            raise ValueError("n_trees must be a positive integer.")
        if not isinstance(learning_rate, float) or learning_rate <= 0 or learning_rate >= 1:
            raise ValueError("learning_rate must be a float in range (0, 1).")
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ValueError("max_depth must be a positive integer.")
        if not isinstance(min_samples_split, int) or min_samples_split < 1:
            raise ValueError("min_samples_split must be a positive integer.")
        if not isinstance(n_bins, int) or n_bins <= 1:
            raise ValueError("n_bins must be an integer greater than 1.")
        if not isinstance(reg_lambda, int | float) or reg_lambda <= 0:
            raise ValueError("reg_lambda must be a positive real number.")
        if not isinstance(gamma, int | float) or gamma < 0:
            raise ValueError("gamma must be a non-negative real number.")
        if not isinstance(large_error_proportion, float) or large_error_proportion <= 0 or large_error_proportion >= 1:
            raise ValueError("large_error_proportion must be a float in range (0, 1).")
        if not isinstance(small_error_proportion, float) or small_error_proportion <= 0 or small_error_proportion >= 1:
            raise ValueError("small_error_proportion must be a float in range (0, 1).")
        if large_error_proportion + small_error_proportion > 1:
            raise ValueError("large_error_proportion and small_error_proportion must sum to a value less than 1.")
        if loss not in ["squared", "absolute", "huber"]:
            raise ValueError('loss must be one in ["squared", "absolute", "huber"].')
        if not isinstance(huber_delta, int | float) or huber_delta <= 0:
            raise ValueError("huber_delta must be a positive real number.")
        if not isinstance(max_conflict_rate, float) or max_conflict_rate < 0 or max_conflict_rate >= 1:
            raise ValueError("max_conflict_rate must be a float in range [0, 1).")
        if not isinstance(use_efb, bool):
            raise TypeError("use_efb must be a boolean.")

        self.n_trees = n_trees
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_bins = n_bins
        self.reg_lambda = reg_lambda
        self.gamma = gamma
        self.trees = None
        self.large_error_proportion = large_error_proportion
        self.small_error_proportion = small_error_proportion
        self.loss = self._choose_loss(loss, huber_delta)
        self.use_efb = use_efb
        if self.use_efb: self.efb = _ExclusiveFeatureBundling(max_conflict_rate=max_conflict_rate, n_bins=n_bins)

    def _choose_loss(self, loss, huber_delta):
        if loss == "squared":
            return MSE(reduction="sum")
        elif loss == "absolute":
            return MAE(reduction="sum")
        elif loss == "huber":
            return Huber(reduction="sum", delta=huber_delta)

    def fit(self, X, y, metrics=["loss"]):
        """
        Fits the LGBMRegressor model to the input data by fitting trees to the errors made by previous trees.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data, where each row is a sample and each column is a feature.
            y (torch.Tensor of shape (n_samples,)): The target values corresponding to each sample.
            metrics (dict[str, torch.Tensor]): Contains the metrics that will be calculated between fitting each tree and returned.
        Returns:
            metrics (dict[str, torch.Tensor]): The calculated metrics.
        Raises:
            TypeError: If the input matrix or the target vector is not a PyTorch tensor.
            ValueError: If the input matrix or the target vector is not the correct shape.
        """
        if not isinstance(X, torch.Tensor) or not isinstance(y, torch.Tensor):
            raise TypeError("The input matrix and the target matrix must be a PyTorch tensor.")
        if X.ndim != 2:
            raise ValueError("The input matrix must be a 2 dimensional tensor.")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError("The target must be 1 dimensional with the same number of samples as the input data")
        if not isinstance(metrics, list | tuple):
            raise ValueError("metrics must be a list or tuple containing the shorthand names of each wanted metric.")
        self.n_features = X.shape[1]

        if self.use_efb: X = self.efb.fit_transform(X)

        self.initial_pred = y.mean()
        pred = torch.full(y.shape, self.initial_pred)
        trees = []
        history = {metric: torch.zeros(self.n_trees) for metric in metrics}

        top_n = int(len(y) * self.large_error_proportion)
        rand_n = int(len(y) * self.small_error_proportion)
        fact = (1 - self.large_error_proportion) / self.small_error_proportion

        for i in range(self.n_trees):
            gradient = self.loss.gradient(pred, y).to(X.dtype)
            hessian = self.loss.hessian(pred, y).to(X.dtype)

            # GOSS (gradient-based one-sided sampling)
            indicies = torch.argsort(gradient, descending=True)
            large_error_indicies = indicies[:top_n]
            small_error_indicies = indicies[torch.randperm(len(indicies) - len(large_error_indicies))[:rand_n] + top_n]
            train_indicies = torch.cat([large_error_indicies, small_error_indicies])
            hessian[small_error_indicies] *= fact

            tree = _LGBMTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split, n_bins=self.n_bins, reg_lambda=self.reg_lambda, gamma=self.gamma)
            tree.fit(X[train_indicies], gradient[train_indicies], hessian[train_indicies])
            prediction = tree.predict(X)
            pred += self.learning_rate * prediction

            trees.append(tree)

            values = calculate_metrics(data=(pred, y), metrics=metrics, loss=self.loss.loss)
            for metric, value in values.items():
                history[metric][i] = value

        self.trees = trees
        return history

    def predict(self, X):
        """
        Applies the fitted LGBMRegressor model to the input data, predicting the target values.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data to be classified.
        Returns:
            targets (torch.Tensor of shape (n_samples,)): The predicted target values corresponding to each sample.
        Raises:
            NotFittedError: If the LGBMRegressor model has not been fitted before predicting.
            TypeError: If the input matrix is not a PyTorch tensor.
            ValueError: If the input matrix is not the correct shape.
        """
        if not hasattr(self, "initial_pred"):
            raise NotFittedError("LGBMRegressor.fit() must be called before predicting.")
        if not isinstance(X, torch.Tensor):
            raise TypeError("The input matrix must be a PyTorch tensor.")
        if X.ndim != 2 or X.shape[1] != self.n_features:
            raise ValueError("The input matrix must be a 2 dimensional tensor with the same number of features as the fitted tensor.")

        if self.use_efb: X = self.efb.transform(X)

        pred = torch.full((X.shape[0],), self.initial_pred)
        
        for tree in self.trees:
            pred += self.learning_rate * tree.predict(X)
        return pred
