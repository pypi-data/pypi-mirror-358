import torch
from copy import deepcopy

from ...Exceptions import NotCompiledError


class BaseLayer:
    def __init__(self, output_shape, input_shape=None, activation=None, normalisation=None, data_type=torch.float32, device=torch.device("cpu")):
        if output_shape == 0: output_shape = tuple()
        output_shape = (output_shape,) if isinstance(output_shape, int) else output_shape
        if not isinstance(output_shape, tuple) and output_shape is not None:
            raise TypeError(f"output_shape must be a tuple. Currently {output_shape}.")
        if not isinstance(input_shape, tuple) and input_shape is not None:
            raise ValueError(f"input_shape must be a tuple or None. Currently {input_shape}.")
        if not isinstance(data_type, torch.dtype):
            raise TypeError(f"data_type must be an instance of torch.dtype.")
        if not isinstance(device, torch.device):
            raise ValueError('device must be one of torch.device("cpu") or torch.device("cuda").')

        self.input_shape = input_shape
        self.output_shape = output_shape
        self.output = None
        self.input = None
        self.nparams = 0
        self.name = "base"
        self.activation = activation
        self.normalisation = normalisation
        self.device = device
        self.data_type = data_type

    def initialise_layer(self, input_shape, data_type, device):
        if not isinstance(input_shape, tuple):
            raise ValueError(f"input_shape must be a tuple or None. Currently {input_shape}.")
        if not isinstance(data_type, torch.dtype):
            raise TypeError("data_type must be an instance of torch.dtype.")
        if not isinstance(data_type, torch.dtype):
            raise TypeError("data_type must be an instance of torch.dtype.")

        self.input_shape = input_shape
        self.data_type = data_type
        self.device = device

        if self.activation:
            self.activation.initialise_layer(input_shape=self.output_shape, data_type=data_type, device=device)
        if self.normalisation:
            self.normalisation.initialise_layer(input_shape=self.output_shape, data_type=data_type, device=device)

    def summary(self, offset=""):
        if not hasattr(self, "input_shape"):
            raise NotCompiledError("layer must be initialized correctly before calling layer.summary().")

        input_shape = self.input_shape[0] if len(self.input_shape) == 1 else self.input_shape
        output_shape = self.output_shape[0] if len(self.output_shape) == 1 else (self.output_shape if len(self.output_shape) != 0 else 1)
        params_summary = " - Parameters: " + str(self.nparams) if self.nparams > 0 else ""
        sublayer_offset = offset + "    "
        normalisation_summary = ("\n" + self.normalisation.summary(sublayer_offset)) if self.normalisation else ""
        activation_summary = ("\n" + self.activation.summary(sublayer_offset)) if self.activation else ""
        return offset + f"{self.name} - (Input, Output): ({input_shape}, {output_shape})" + params_summary + normalisation_summary + activation_summary

    def forward(self, input, **kwargs):
        if not isinstance(input, torch.Tensor):
            raise TypeError("input must be a torch.Tensor.")
        if input.shape[1:] != self.input_shape:
            raise ValueError(f"input is not the same shape as the spesified input_shape ({input.shape[1:], self.input_shape}).")

        self.input = input
        return self.input

    def backward(self, dCdy, **kwargs):
        if not isinstance(dCdy, torch.Tensor):
            raise TypeError("dCdy must be a torch.Tensor.")
        if dCdy.shape[1:] != self.output_shape and not (dCdy.ndim == 1 and self.output_shape[0] == 0):
            raise ValueError(f"dCdy is not the same shape as the spesified output_shape ({dCdy.shape[1:], self.output_shape}).")

        return dCdy
    
    def get_nparams(self):
        if not hasattr(self, "nparams"):
            raise NotCompiledError("layer must be initialized correctly before calling layer.summary().")

        return self.nparams + (self.normalisation.nparams if self.normalisation else 0)

    def get_parameters(self):
        return tuple() if self.normalisation is None else self.normalisation.get_parameters()
    
    def clone(self):
        return deepcopy(self)
