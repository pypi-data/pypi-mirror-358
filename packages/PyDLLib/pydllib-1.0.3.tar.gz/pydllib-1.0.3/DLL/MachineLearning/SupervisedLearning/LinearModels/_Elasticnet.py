import torch
from math import floor

from ....Data.Metrics import calculate_metrics, _round_dictionary
from ....Exceptions import NotFittedError


class ElasticNetRegression:
    """
    Implements a linear regression model with L1 and L2 regularization.
    
    Args:
        alpha (int | float, optional): The regularization parameter. Larger alpha will force the l1 and l2 norms of the weights to be lower. Must be a non-negative real number. Defaults to 1.
        l1_ratio (int | float, optional): The proportion of l1 regularisation compared to l2 regularisation. Must be in the range [0, 1]. Defaults to 0.5.
        loss (:ref:`losses_section_label`, optional): A loss function used for training the model. Defaults to the mean squared error.

    Attributes:
        n_features (int): The number of features. Available after fitting.
        weights (torch.Tensor of shape (n_features + 1,)): The weights of the linear regression model. The first element is the bias of the model. Available after fitting.
        residuals (torch.Tensor of shape (n_samples,)): The residuals of the fitted model. For a good fit, the residuals should be normally distributed with zero mean and constant variance. Available after fitting.
    """
    def __init__(self, alpha=1.0, l1_ratio=0.5):
        if not isinstance(alpha, int | float) or alpha < 0:
            raise ValueError("alpha must be a non-negative real number.")
        if not isinstance(l1_ratio, int | float) or not ((0 <= l1_ratio) and (l1_ratio <= 1)):
            raise ValueError("l1_ratio must be in range [0, 1].")

        self.alpha = alpha
        self.l1_ratio = l1_ratio

    def fit(self, X, y, sample_weight=None, val_data=None, epochs=100, callback_frequency=1, metrics=["loss"], verbose=False):
        """
        Fits the ElasticNetRegression model to the input data by minimizing the mean squared error loss function using cyclic coordinate-wise descent from `this paper <https://aaltodoc.aalto.fi/server/api/core/bitstreams/091c41eb-7348-48d3-b25d-c8de25fbab03/content>`_.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data, where each row is a sample and each column is a feature.
            y (torch.Tensor of shape (n_samples,)): The target values corresponding to each sample.
            val_data (tuple[X_val, y_val] | None, optional): Optional validation samples. If None, no validation data is used. Defaults to None.
            epochs (int, optional): The number of training iterations. Must be a positive integer. Defaults to 100.
            callback_frequency (int, optional): The number of iterations between printing info from training. Must be a positive integer. Defaults to 1, which means that every iteration, info is printed assuming verbose=True.
            metrics (list[str], optional): The metrics that will be tracked during training. Defaults to ["loss"].
            verbose (bool, optional): If True, prints info of the chosen metrics during training. Defaults to False.
        Returns:
            history (dict[str, torch.Tensor], each tensor is floor(epochs / callback_frequency) long.): A dictionary tracking the evolution of selected metrics at intervals defined by callback_frequency.
        Raises:
            TypeError: If the input matrix or the target matrix is not a PyTorch tensor or if other parameters are of wrong type.
            ValueError: If the input matrix or the target matrix is not the correct shape or if other parameters have incorrect values.
        """
        if not isinstance(X, torch.Tensor) or not isinstance(y, torch.Tensor):
            raise TypeError("The input matrix and the target matrix must be a PyTorch tensor.")
        if X.ndim != 2:
            raise ValueError("The input matrix must be a 2 dimensional tensor.")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError("The targets must be 1 dimensional with the same number of samples as the input data")
        if not isinstance(val_data, tuple) and val_data is not None:
            raise TypeError("val_data must either be a tuple containing validation samples or None.")
        if isinstance(val_data, tuple) and len(val_data) != 2:
            raise ValueError("val_data must contain both X_val and y_val.")
        if isinstance(val_data, tuple) and len(val_data) == 2 and (val_data[0].ndim != 2 or val_data[1].ndim != 1 or val_data[0].shape[1] != X.shape[1] or len(val_data[0]) != len(val_data[1])):
            raise ValueError("X_val and y_val must be of correct shape.")
        if not isinstance(epochs, int) or epochs <= 0:
            raise ValueError("epochs must be a positive integer.")
        if not isinstance(callback_frequency, int) or callback_frequency <= 0:
            raise ValueError("callback_frequency must be a positive integer.")
        if not isinstance(metrics, list | tuple):
            raise TypeError("metrics must be a list or a tuple containing the strings of wanted metrics.")
        if not isinstance(verbose, bool):
            raise TypeError("verbose must be a boolean.")
        if not isinstance(sample_weight, torch.Tensor) and sample_weight is not None:
            raise TypeError("sample_weight must be torch.Tensor or None.")
        if isinstance(sample_weight, torch.Tensor) and (sample_weight.ndim != 1 or len(X) != len(sample_weight)):
            raise ValueError("sample_weight must be of shape (n_samples,)")

        # self.n_features = X.shape[1]
        # history = {metric: torch.zeros(floor(epochs / callback_frequency)) for metric in metrics}
        # batch_size = len(X) if batch_size is None else batch_size
        # data_reader = DataReader(X, y, batch_size=batch_size, shuffle=shuffle_data, shuffle_every_epoch=shuffle_every_epoch)

        # self.weights = torch.randn((self.n_features,))
        # self.bias = torch.zeros((1,))
        # optimiser = ADAM() if optimiser is None else optimiser
        # optimiser.initialise_parameters([self.weights, self.bias])

        # for epoch in range(epochs):
        #     for x_batch, y_batch in data_reader.get_data():
        #         predictions = self.predict(x_batch)
        #         dCdy = self.loss.gradient(predictions, y_batch)
        #         dCdweights = (x_batch.T @ dCdy) + self.alpha * self.l1_ratio * torch.sign(self.weights) + self.alpha * (1 - self.l1_ratio) * self.weights
        #         dCdbias = dCdy.mean(dim=0, keepdim=True)
        #         self.weights.grad = dCdweights
        #         self.bias.grad = dCdbias
        #         optimiser.update_parameters()
        #     if epoch % callback_frequency == 0:
        #         values = calculate_metrics(data=(self.predict(X), y), metrics=metrics, loss=self.loss.loss)
        #         if val_data is not None:
        #             val_values = calculate_metrics(data=(self.predict(val_data[0]), val_data[1]), metrics=metrics, loss=self.loss.loss, validation=True)
        #             values |= val_values
        #         for metric, value in values.items():
        #             history[metric][int(epoch / callback_frequency)] = value
        #         if verbose: print(f"Epoch: {epoch + 1} - Metrics: {_round_dictionary(values)}")
        # self.residuals = y - self.predict(X)
        # return history

        n_samples, self.n_features = X.shape
        X = torch.cat((torch.ones(size=(X.shape[0], 1)), X), dim=1)
        
        history = {metric: torch.zeros(floor(epochs / callback_frequency)) for metric in metrics}
        self.weights = torch.randn((self.n_features + 1))

        if sample_weight is None:
            sample_weight = torch.ones(n_samples)

        normalisation_const = torch.sum(sample_weight[:, None] * X**2, axis=0)

        for epoch in range(epochs):
            for j in range(self.n_features + 1):
                residual = y - X @ self.weights + self.weights[j] * X[:, j]
                weighted_prod = torch.dot(X[:, j], sample_weight * residual)
                if normalisation_const[j] == 0:
                    continue
                soft_thresholding = torch.sign(weighted_prod) * max(abs(weighted_prod) - self.alpha * self.l1_ratio, 0) / (normalisation_const[j] + self.alpha * (1 - self.l1_ratio))
                self.weights[j] = soft_thresholding

            if epoch % callback_frequency == 0:
                values = calculate_metrics(data=(self.predict(X), y), metrics=metrics, loss=self._loss)
                if val_data is not None:
                    val_values = calculate_metrics(data=(self.predict(val_data[0]), val_data[1]), metrics=metrics, loss=self._loss, validation=True)
                    values |= val_values
                for metric, value in values.items():
                    history[metric][int(epoch / callback_frequency)] = value
                if verbose: print(f"Epoch: {epoch + 1} - Metrics: {_round_dictionary(values)}")
        
        # self.weights *= 1 + self.alpha * (1 - self.l1_ratio)  # author of paper suggests this for a correction to the double shrinkage effect, however, the results are not that good.
        self.residuals = y - self.predict(X)
        return history
    
    def _loss(self, prediction, true_outputs):
        return torch.sum((prediction - true_outputs) ** 2) + self.alpha * (2 * self.l1_ratio * torch.linalg.norm(self.weights, ord=1) + (1 - self.l1_ratio) * torch.linalg.norm(self.weights, ord=2) ** 2)

    def predict(self, X):
        """
        Applies the fitted ElasticNetRegression model to the input data, predicting the correct values.

        Args:
            X (torch.Tensor of shape (n_samples, n_features)): The input data to be regressed.
        Returns:
            target values (torch.Tensor of shape (n_samples,)): The predicted values corresponding to each sample.
        Raises:
            NotFittedError: If the ElasticNetRegression model has not been fitted before predicting.
            TypeError: If the input matrix is not a PyTorch tensor.
            ValueError: If the input matrix is not the correct shape.
        """
        if not hasattr(self, "weights"):
            raise NotFittedError("ElasticNetRegression.fit() must be called before predicting.")
        if not isinstance(X, torch.Tensor):
            raise TypeError("The input matrix must be a PyTorch tensor.")
        if X.ndim != 2 or (X.shape[1] != self.n_features and (X.shape[1] != self.n_features + 1 or torch.any(X[:, 0] != torch.ones(len(X))))):
            raise ValueError("The input matrix must be a 2 dimensional tensor with the same number of features as the fitted tensor.")

        if X.shape[1] != self.n_features + 1: X = torch.cat((torch.ones(size=(X.shape[0], 1)), X), dim=1)
        return X @ self.weights
