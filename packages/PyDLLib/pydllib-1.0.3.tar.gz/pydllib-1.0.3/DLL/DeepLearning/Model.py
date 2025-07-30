import torch
from copy import deepcopy
import pickle


class Model:
    """
    The base model for a sequantial deep learning model. Uses a linear stack of layers to do forward- and backpropagation.

    Args:
        input_shape (tuple[int] | int): A tuple or an int containing the input shape of the model. The batch size should not be given as the first member of the tuple. For instance, if the input is of shape (n_sample, n_features), the input_shape should be n_features or if the input is of shape (n_samples, n_channels, width, heigth), the input_shape should be (n_channels, width, heigth).
        data_type (torch.dtype, optional): The data type used by the model. Defaults to torch.float32.
        device (torch.device, optional): The device of the model. Determines if the computation is made using the gpu or the cpu. Defaults to torch.device("cpu").
    """
    def __init__(self, input_shape, data_type=torch.float32, device=torch.device("cpu")):
        if not isinstance(input_shape, tuple | int):
            raise TypeError("input_shape must be a tuple of ints or an int. See documentation for examples.")
        if not isinstance(data_type, torch.dtype):
            raise TypeError("data_type must be an instance of torch.dtype.")
        if not isinstance(device, torch.device):
            raise TypeError('device must be either torch.device("cpu") or torch.device("cuda").')

        from .Layers import Input
        input_shape = (input_shape,) if isinstance(input_shape, int) else input_shape
        self.layers = [Input(input_shape, device=device, data_type=data_type)]
        self.optimiser = None
        self.loss = None
        self.data_type = data_type
        self.device = device
        self.training = False

    def compile(self, optimiser=None, loss=None, metrics=("loss",), callbacks=tuple()):
        """
        Configures the model for training. Sets the optimiser and the loss function.

        Args:
            optimiser (:ref:`optimisers_section_label` | None, optional): The optimiser used for training the model. If None, the ADAM optimiser is used.
            loss (:ref:`losses_section_label` | None, optional): The loss function used for training the model. If None, the MSE loss is used.
            metrics (tuple[str], optional): The metrics that will be tracked during training. Defaults to ("loss").
            callbacks (tuple[:ref:`callbacks_section_label`], optional): The callbacks used by the model. Defaults to ().
        Raises:
            TypeError: If the optimiser is not from DLL.DeepLearning.Optimisers, the loss is not from DLL.DeepLearning.Losses or the metrics is not a tuple or a list of strings.
        """

        from .Losses._BaseLoss import BaseLoss
        from .Optimisers._BaseOptimiser import BaseOptimiser
        from .Callbacks import Callback
        from .Losses import MSE
        from .Optimisers import ADAM

        if not isinstance(optimiser, BaseOptimiser) and optimiser is not None:
            raise TypeError("optimiser must be from DLL.DeepLearning.Optimisers")
        if not isinstance(loss, BaseLoss) and loss is not None:
            raise TypeError("loss must be from DLL.DeepLearning.Losses")
        if not isinstance(metrics, list | tuple):
            raise TypeError("metrics must be a list or a tuple containing the strings of wanted metrics.")
        if any([not isinstance(callback, Callback) for callback in callbacks]):
            raise TypeError("callbacks must be a tuple of callback objects.")

        self.optimiser = optimiser if optimiser is not None else ADAM()
        parameters = [parameter for layer in self.layers for parameter in layer.get_parameters()]
        self.optimiser.initialise_parameters(parameters)
        self.loss = loss if loss is not None else MSE()
        self.metrics = metrics
        self.callbacks = callbacks

    def clone(self):
        """
        Returns a copy of the same model.
        """
        return deepcopy(self)

    def add(self, layer):
        """
        Adds and initializes a layer to the model.

        Args:
            layer (:ref:`layers_section_label`): The layer that is added to the model.
        """
        from .Layers._BaseLayer import BaseLayer
        if not isinstance(layer, BaseLayer):
            raise TypeError("layer must be from DLL.Deeplearning.Layers")

        layer.initialise_layer(input_shape=self.layers[-1].output_shape, data_type=self.data_type, device=self.device)
        self.layers.append(layer)
    
    def train(self):
        """
        Change the state of the model to training state. Effects some layers, but other layers remain the same.
        """
        self.training = True

    def eval(self):
        """
        Change the state of the model to evaluation state. Effects some layers, but other layers remain the same.
        """
        self.training = False
    
    def summary(self):
        """
        Prints the summary of the model containing its architecture and the number of parameters of the model.
        """
        print("Model summary:")
        total_params = 0
        for layer in self.layers:
            print(layer.summary())
            total_params += layer.get_nparams()
        print(f"Total number of parameters: {total_params}")
    
    def __str__(self):
        message = "Model summary:"
        total_params = 0
        for layer in self.layers:
            message += layer.summary() + "\n"
            total_params += layer.get_nparams()
        message += f"Total number of parameters: {total_params}"
        return message

    def predict(self, X):
        """
        Applies the fitted Model to the input data, predicting wanted values by forward propagation.

        Args:
            X (torch.Tensor of shape (n_samples, *input_shape)): The input data that goes through the model by forward propagation.
        
        Raises:
            NotCompiledError: If the Model has not been compiled before predicting.

        Returns:
            torch.Tensor of shape (n_samples, *last_layer.output_shape)): The predictions made by the model.
        """
        from ..Exceptions import NotCompiledError
        if self.optimiser is None:
            raise NotCompiledError("Model.compile() must be called before predicting.")

        current = X
        for layer in self.layers:
            current = layer.forward(current, training=self.training)
        return current
    
    def backward(self, initial_gradient):
        """
        :meta private:
        """
        reversedLayers = reversed(self.layers)
        gradient = initial_gradient
        for layer in reversedLayers:
            gradient = layer.backward(gradient, training=self.training)
        return gradient

    def fit(self, X, Y, val_data=None, epochs=10, callback_frequency=1, batch_size=None, shuffle_every_epoch=True, shuffle_data=True, verbose=False):
        """
        Fits the LogisticRegression model to the input data by minimizing the cross entropy loss (logistic loss).

        Args:
            X (torch.Tensor of shape (n_samples, *first_layer.input_shape)): The input data, of correct shape determined by the input_shape of the model.
            y (torch.Tensor): The targets corresponding to each sample.
            val_data (tuple[X_val, y_val] | None, optional): Optional validation samples. Must have the same remaining dimensions than X and y apart from n_samples. If None, no validation data is used. Defaults to None.
            epochs (int, optional): The number of training iterations. Must be a positive integer. Defaults to 10.
            callback_frequency (int, optional): The number of iterations between printing info from training. Must be a positive integer. Defaults to 1, which means that every iteration, info is printed assuming verbose=True.
            batch_size (int | None, optional): The batch size used in training. Must be a positive integer. If None, every sample is used for every gradient calculation. Defaults to None.
            shuffle_every_epoch (bool, optional): If True, shuffles the order of the samples every epoch. Defaults to True.
            shuffle_data (bool, optional): If True, shuffles data before the training.
            verbose (bool, optional): If True, prints info of the chosen metrics during training. Defaults to False.
        Returns:
            history (dict[str, list]): A dictionary tracking the evolution of selected metrics at intervals defined by callback_frequency. If training was not stopped early, each metric is floor(epochs / callback_frequency) long.
        Raises:
            TypeError: If the input matrix or the target matrix is not a PyTorch tensor or if other parameters are of wrong type.
            ValueError: If the input matrix or the target matrix is not the correct shape or if other parameters have incorrect values.
        """
        if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
            raise TypeError("The input matrix and the target matrix must be a PyTorch tensor.")
        if X.shape[1:] != self.layers[0].input_shape:
            raise ValueError("The input matrix must have the same shape as input_shape.")
        if len(Y) != len(X) or Y.shape[1:] != self.layers[-1].output_shape:
            raise ValueError(f"The targets must have the same shape as the output_shape of the last layer with the same number of samples as the input data {Y.shape[1:], self.layers[-1].output_shape}.")
        if not isinstance(val_data, list | tuple) and val_data is not None:
            raise TypeError("val_data must either be a tuple containing validation samples or None.")
        if isinstance(val_data, list | tuple) and len(val_data) != 2:
            raise ValueError("val_data must contain both X_val and y_val.")
        if isinstance(val_data, list | tuple) and len(val_data) == 2 and (val_data[0].shape[1:] != X.shape[1:] or val_data[1].shape[1:] != Y.shape[1:] or len(val_data[0]) != len(val_data[1])):
            raise ValueError("X_val and y_val must be of correct shape.")
        if not isinstance(epochs, int) or epochs <= 0:
            raise ValueError("epochs must be a positive integer.")
        if not isinstance(callback_frequency, int) or callback_frequency <= 0:
            raise ValueError("callback_frequency must be a positive integer.")
        if (not isinstance(batch_size, int) or batch_size <= 0) and batch_size is not None:
            raise ValueError("batch_size must be a positive integer.")
        if not isinstance(shuffle_every_epoch, bool):
            raise TypeError("shuffle_every_epoch must be a boolean.")
        if not isinstance(shuffle_data, bool):
            raise TypeError("shuffle_data must be a boolean.")
        if not isinstance(verbose, bool):
            raise TypeError("verbose must be a boolean.")
        
        from ..Data import DataReader
        from ..Data.Metrics import calculate_metrics, _round_dictionary

        history = {metric: [] for metric in self.metrics}
        batch_size = len(X) if batch_size is None else batch_size
        data_reader = DataReader(X, Y, batch_size=batch_size, shuffle=shuffle_data, shuffle_every_epoch=shuffle_every_epoch)

        train_metrics = [metric for metric in self.metrics if metric[:4] != "val_"]
        val_metrics = [metric for metric in self.metrics if metric[:4] == "val_"]

        self.stop_training = False  # boolean for callbacks to stop the training
        for callback in self.callbacks:
            callback.set_model(self)
            callback.on_train_start()

        for epoch in range(epochs):
            if self.stop_training:
                break
            self.train()
            for x, y in data_reader.get_data():
                self.optimiser.zero_grad()
                predictions = self.predict(x)
                initial_gradient = self.loss.gradient(predictions, y)
                self.backward(initial_gradient)
                self.optimiser.update_parameters()
                for callback in self.callbacks:
                    callback.on_batch_end(epoch)

            self.eval()
            if epoch % callback_frequency == 0:
                values = calculate_metrics(data=(self.predict(X), Y), metrics=train_metrics, loss=self.loss.loss)
                if val_data is not None:
                    val_values = calculate_metrics(data=(self.predict(val_data[0]), val_data[1]), metrics=val_metrics, loss=self.loss.loss, validation=True)
                    values |= val_values
                for metric, value in values.items():
                    history[metric].append(value)
                if verbose: print(f"Epoch: {epoch + 1} - Metrics: {_round_dictionary(values)}")
            
            for callback in self.callbacks:
                callback.on_epoch_end(epoch, values)
        
        for callback in self.callbacks:
            callback.on_train_end()

        return history


def save_model(model, filepath="./model.pkl"):
    """Saves a model using pickle serialization."""
    try:
        with open(filepath, "wb") as f:
            pickle.dump(model, f)
    except TypeError as e:
        print(f"Error: The model is not serializable. Saving failed.")
        raise
    except OSError as e:
        print(f"File error while saving the model.")
        raise

def load_model(filepath="./model.pkl"):
    """Loads a model from a pickle file."""
    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except (pickle.UnpicklingError, EOFError, AttributeError, ModuleNotFoundError, TypeError) as e:
        print(f"Error loading the model file.")
        raise
    except OSError as e:
        print(f"File error while loading the model.")
        raise
