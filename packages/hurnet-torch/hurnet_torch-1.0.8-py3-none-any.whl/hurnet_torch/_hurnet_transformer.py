# THIS IS A HURNET TYPE ARTIFICIAL NEURAL NETWORK
"""
# HurNetTorch: A New Era in Neural Networks
HurNetTorch represents a significant evolution of the original HurNet architecture, maintaining its core computations while leveraging the flexibility of PyTorch’s dynamic tensors.
This advanced implementation offers substantial improvements in both training and inference, ensuring compatibility with a wide range of processing devices, including CPU, GPU, TPU, and MPS.

## Key Features
The module includes specialized extensions for developing Transformer-based language models, specifically tailored to integrate the unique computational logic of the HurNet network.
This integration allows exploring new horizons in natural language processing with superior computational efficiency.

## Revolutionary Paradigm
At the heart of HurNetTorch is the HurNet architecture, which introduces a completely new paradigm for artificial neural networks.
Unlike conventional approaches that rely on iterative weight adjustments through gradient calculations and multiple backpropagation cycles, HurNet implements a novel direct adjustment method.

This method uses division calculations that propagate in a single pass from the network’s output to the input, eliminating the need for repetitive processes.
This revolutionary approach results in a dramatic reduction in high-performance hardware requirements,
providing extraordinary gains in execution speed and making neural network training more accessible and efficient.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from torch.nn import Module
from torch import tensor as global_tensor
default_tensor = global_tensor([])
class HurNetTransformer(Module):
    def __init__(self, input_dim=(1,), output_dim=(1,), activation_function='linear', interaction=True, bias=0.0, device=None):
        try:
            super().__init__()
            from ._device_detection import DeviceDetection
            from torch import empty as torch_empty
            from ._activation_functions import ActivationFunctions
            from torch import ones as torch_ones
            from torch import prod as torch_prod
            from torch import cat as torch_cat
            from torch import float32 as torch_float32
            from torch import Tensor as torch_tensor_type
            from torch import tensor as torch_tensor_function
            from torch import randn as torch_randn
            from torch import zeros_like as torch_zeros_like
            from torch.nn import Parameter as torch_parameter
            from torch import linalg as torch_linalg
            from torch import zeros as torch_zeros
            from torch import stack as torch_stack
            final_device_object = DeviceDetection().getDevice(device=device)
            self.__output_dim_tuple = output_dim if isinstance(output_dim, tuple) else (output_dim,)
            self.__activation_functions = ActivationFunctions
            self.__hidden_layers_configuration = []
            self.__hidden_weights_list = []
            self.__hidden_biases_list = []
            interaction = bool(interaction) if type(interaction) in (bool, int, float) else True
            self.__interaction_enabled = interaction
            self.__torch_ones = torch_ones
            self.__torch_prod = torch_prod
            self.__torch_cat = torch_cat
            self.__selected_device = final_device_object
            bias = float(bias) if type(bias) in (bool, int, float) else 0.0
            self.__instance_bias = bias
            self.__torch_float32 = torch_float32
            self.__torch_tensor_type = torch_tensor_type
            self.__torch_tensor_function = torch_tensor_function
            self.__output_dimensions_cache = list(self.__output_dim_tuple)
            self.__final_activation_for_hidden_block = 'linear'
            self.__training_method = 'pseudo-inverse'
            self.__torch_randn = torch_randn
            self.__weights_list_per_sample = None
            self.__torch_zeros_like = torch_zeros_like
            self.__torch_parameter = torch_parameter
            self.__torch_linalg_pinv = torch_linalg.pinv
            self.__torch_zeros = torch_zeros
            self.__torch_stack = torch_stack
            self.__activation_name = str(activation_function).lower().strip()
            input_dim_tuple = input_dim if isinstance(input_dim, tuple) else (input_dim,)
            input_features_flat = torch_prod(torch_tensor_function(input_dim_tuple, device=final_device_object)).item()
            output_features_flat = torch_prod(torch_tensor_function(self.__output_dim_tuple, device=final_device_object)).item()
            number_of_features_added_for_weights = (2 if interaction else 1)
            self.weights = torch_parameter(torch_empty((int(input_features_flat) + number_of_features_added_for_weights, int(output_features_flat)), device=final_device_object))
            torch_randn((int(input_features_flat) + number_of_features_added_for_weights, int(output_features_flat)), out=self.weights.data, device=final_device_object)
            self.weights_data, self.__input_dim = self.weights.data[:1, :].T, input_dim
        except Exception as error: print('ERROR in HurNetTransformer.__init__: ' + str(error))
    def __apply_activation_function_to_tensor(self, input_tensor_param=default_tensor, activation_name_str_param=default_tensor):
        try: return self.__activation_functions().apply(input_tensor=input_tensor_param, activation_function_name=activation_name_str_param)
        except Exception as error:
            print('ERROR in HurNetTransformer.__apply_activation_function_to_tensor: ' + str(error))
            return input_tensor_param
    def __apply_hidden_layers_batch(self, input_batch_tensor_param=default_tensor, final_activation_name='linear'):
        try:
            current_hidden_state = input_batch_tensor_param.reshape(input_batch_tensor_param.shape[0], -1)
            for index_val, (neuron_count_val, activation_name_val) in enumerate(self.__hidden_layers_configuration):
                weight_matrix, bias_vector = self.__hidden_weights_list[index_val], self.__hidden_biases_list[index_val]
                linear_combination = current_hidden_state @ weight_matrix + bias_vector
                current_hidden_state = self.__apply_activation_function_to_tensor(linear_combination, activation_name_val)
            current_hidden_state = self.__apply_activation_function_to_tensor(current_hidden_state, final_activation_name)
            return current_hidden_state
        except Exception as error:
            print('ERROR in HurNetTransformer.__apply_hidden_layers_batch: ' + str(error))
            return input_batch_tensor_param
    def __add_features(self, input_tensor_param=default_tensor):
        try:
            current_input_tensor = input_tensor_param
            if current_input_tensor.dim() == 1: current_input_tensor = current_input_tensor.unsqueeze(0)
            batch_size = current_input_tensor.shape[0]
            if self.__interaction_enabled:
                interaction_term = self.__torch_prod(current_input_tensor, dim=1, keepdim=True)
                ones_term = self.__torch_ones((batch_size, 1), device=self.__selected_device, dtype=current_input_tensor.dtype)
                return self.__torch_cat([current_input_tensor, interaction_term, ones_term], dim=1)
            else:
                ones_term = self.__torch_ones((batch_size, 1), device=self.__selected_device, dtype=current_input_tensor.dtype)
                return self.__torch_cat([current_input_tensor, ones_term], dim=1)
        except Exception as error:
            print('ERROR in HurNetTransformer.__add_features: ' + str(error))
            return input_tensor_param
    def train_layer(self, x=default_tensor, y=default_tensor, activation_function='linear', bias=None, learning_rate=None, quantization=None, method='pseudo-inverse', hidden_layers=None):
        try:
            if type(x) != type(default_tensor): x = global_tensor(x) if type(x) in (tuple, list) else default_tensor
            if type(y) != type(default_tensor): y = global_tensor(y) if type(y) in (tuple, list) else default_tensor
            activation_function = str(activation_function).lower().strip()
            if bias is not None: bias = float(bias) if type(bias) in (bool, int, float) else 0.0
            learning_rate = float(learning_rate) if type(learning_rate) in (bool, int, float) else 1.0
            if quantization is not None: quantization = max((0, int(quantization))) if type(quantization) in (bool, int, float) else None
            method = str(method).lower().strip()
            if hidden_layers is not None: hidden_layers = list(hidden_layers) if type(hidden_layers) in (tuple, list) else None
            input_data, target_data, current_training_bias = x, y, bias if bias is not None else self.__instance_bias        
            input_tensor = self.__torch_tensor_function(input_data, dtype=self.__torch_float32, device=self.__selected_device) if not isinstance(input_data, self.__torch_tensor_type) else input_data.to(self.__selected_device, dtype=self.__torch_float32)
            target_tensor = self.__torch_tensor_function(target_data, dtype=self.__torch_float32, device=self.__selected_device) if not isinstance(target_data, self.__torch_tensor_type) else target_data.to(self.__selected_device, dtype=self.__torch_float32)
            if input_tensor.dim() == 1: input_tensor = input_tensor.unsqueeze(0)
            if target_tensor.dim() == 1: target_tensor = target_tensor.unsqueeze(0)  
            original_input_feature_size = input_tensor.shape[1] if input_tensor.dim() > 1 else input_tensor.shape[0]
            if input_tensor.dim() > 2 :
                original_input_feature_size = self.__torch_prod(self.__torch_tensor_function(input_tensor.shape[1:], device=self.__selected_device)).item()
                input_tensor = input_tensor.reshape(input_tensor.shape[0], -1)
            if target_tensor.dim() > 2: target_tensor = target_tensor.reshape(target_tensor.shape[0], -1)
            if isinstance(target_data, self.__torch_tensor_type): self.__output_dimensions_cache = list(target_data.shape[1:]) if target_data.dim() > 1 else []
            elif isinstance(target_data, (list, tuple)):
                if target_data and isinstance(target_data[0], (list, tuple)): self.__output_dimensions_cache = [len(target_data[0])] if target_data[0] else [1]
                elif target_data and not isinstance(target_data[0], (list, tuple)): self.__output_dimensions_cache = []
                else: self.__output_dimensions_cache = list(self.__output_dim_tuple)
            else: self.__output_dimensions_cache = list(self.__output_dim_tuple)
            self.__hidden_layers_configuration, self.__hidden_weights_list, self.__hidden_biases_list = [], [], []
            self.__final_activation_for_hidden_block, self.__training_method = activation_function, method
            if hidden_layers and isinstance(hidden_layers, list):
                self.__hidden_layers_configuration = hidden_layers
                previous_dimension = int(original_input_feature_size)
                for (neuron_count_val, activation_name_str_val) in self.__hidden_layers_configuration:
                    neuron_count = max((1, int(neuron_count_val)))
                    weight_matrix = self.__torch_randn((previous_dimension, neuron_count), dtype=self.__torch_float32, device=self.__selected_device)
                    bias_vector = self.__torch_randn((neuron_count,), dtype=self.__torch_float32, device=self.__selected_device)
                    self.__hidden_weights_list.append(weight_matrix)
                    self.__hidden_biases_list.append(bias_vector)
                    previous_dimension = neuron_count
            processed_input_for_method = input_tensor
            if self.__hidden_layers_configuration: processed_input_for_method = self.__apply_hidden_layers_batch(input_tensor, self.__final_activation_for_hidden_block)
            if self.__training_method == 'division':
                self.__weights_list_per_sample = []
                number_of_samples = processed_input_for_method.shape[0]
                for index_value in range(number_of_samples):
                    current_sample_activation, target_sample_value = processed_input_for_method[index_value], target_tensor[index_value]
                    sum_of_activations = current_sample_activation.sum()
                    if sum_of_activations.item() == 0: weights_for_sample = self.__torch_zeros_like(target_sample_value, device=self.__selected_device)
                    else: weights_for_sample = target_sample_value / sum_of_activations
                    weights_for_sample = (weights_for_sample + current_training_bias) * learning_rate
                    if quantization is not None: weights_for_sample = weights_for_sample.round(decimals=quantization)
                    self.__weights_list_per_sample.append(weights_for_sample)
            else:
                current_feature_size_for_pinv, number_of_features_added = processed_input_for_method.shape[1], (2 if self.__interaction_enabled else 1)
                expected_weights_shape_0, expected_weights_shape_1 = current_feature_size_for_pinv + number_of_features_added, target_tensor.shape[1]
                if self.weights.shape[0] != expected_weights_shape_0 or self.weights.shape[1] != expected_weights_shape_1:
                    new_weights_parameter = self.__torch_parameter(self.__torch_randn((expected_weights_shape_0, expected_weights_shape_1), dtype=self.__torch_float32, device=self.__selected_device))
                    self.weights = new_weights_parameter
                augmented_input = self.__add_features(processed_input_for_method)
                if augmented_input.device.type == 'mps' or target_tensor.device.type == 'mps':
                    augmented_input_cpu, target_tensor_cpu = augmented_input.cpu(), target_tensor.cpu()
                    calculated_weights = self.__torch_linalg_pinv(augmented_input_cpu) @ target_tensor_cpu
                    calculated_weights = calculated_weights.to(self.__selected_device)
                else: calculated_weights = self.__torch_linalg_pinv(augmented_input) @ target_tensor
                final_weights = (calculated_weights + current_training_bias) * learning_rate
                if quantization is not None: final_weights = final_weights.round(decimals=quantization)
                self.weights.data = final_weights
                if self.weights.data.shape[0] >= 2: self.weights_data = self.weights.data[:-2, :].T
                elif self.__input_dim <= self.weights.data.shape[0]: self.weights_data = self.weights.data[:self.__input_dim, :].T
                else: self.weights_data = self.weights.data[1, :].T
            return True
        except Exception as error:
            print('ERROR in HurNetTransformer.train_layer: ' + str(error))
            return False
    def forward(self, x=default_tensor):
        try:
            if type(x) != type(default_tensor): x = global_tensor(x) if type(x) in (tuple, list) else default_tensor
            input_data_param = x
            input_tensor = self.__torch_tensor_function(input_data_param, dtype=self.__torch_float32, device=self.__selected_device) if not isinstance(input_data_param, self.__torch_tensor_type) else input_data_param.to(self.__selected_device, dtype=self.__torch_float32)
            if input_tensor.dim() == 1: input_tensor = input_tensor.unsqueeze(0)
            if input_tensor.dim() > 2 : input_tensor = input_tensor.reshape(input_tensor.shape[0], -1)
            processed_input = input_tensor
            if self.__hidden_layers_configuration: processed_input = self.__apply_hidden_layers_batch(input_tensor, self.__final_activation_for_hidden_block)
            number_of_samples_in_the_batch, predicted_output_stacked = processed_input.shape[0], None
            if self.__training_method == 'division':
                if not self.__weights_list_per_sample:
                    output_shape_per_sample = self.__output_dimensions_cache if self.__output_dimensions_cache else []
                    if not output_shape_per_sample: return self.__torch_zeros(number_of_samples_in_the_batch, device=self.__selected_device)
                    else: return self.__torch_zeros(number_of_samples_in_the_batch, *output_shape_per_sample, device=self.__selected_device)
                results_list = []
                for index_value in range(number_of_samples_in_the_batch):
                    current_sample_activation = processed_input[index_value]
                    sum_of_activations = current_sample_activation.sum()
                    weights_for_sample = self.__weights_list_per_sample[index_value % len(self.__weights_list_per_sample)]
                    output_prediction_flat = sum_of_activations * weights_for_sample
                    results_list.append(output_prediction_flat)
                predicted_output_stacked = self.__torch_stack(results_list, dim=0)
                if self.__output_dimensions_cache:
                    try:
                        if self.__output_dimensions_cache: predicted_output_stacked = predicted_output_stacked.reshape(number_of_samples_in_the_batch, *self.__output_dimensions_cache)
                        elif predicted_output_stacked.dim() == 2 and predicted_output_stacked.shape[1] == 1: predicted_output_stacked = predicted_output_stacked.squeeze(-1)
                    except: pass 
                elif predicted_output_stacked.dim() > 1 and predicted_output_stacked.shape[-1] == 1: predicted_output_stacked = predicted_output_stacked.squeeze(-1)
            elif self.__training_method == 'pseudo-inverse':
                if self.weights is None or self.weights.numel() == 0:
                    output_shape_per_sample = self.__output_dimensions_cache if self.__output_dimensions_cache else []
                    if not output_shape_per_sample: return self.__torch_zeros(number_of_samples_in_the_batch, device=self.__selected_device)
                    else: return self.__torch_zeros(number_of_samples_in_the_batch, *output_shape_per_sample, device=self.__selected_device)
                augmented_input = self.__add_features(processed_input)
                predicted_output_flat = augmented_input @ self.weights
                if self.__output_dimensions_cache: 
                    try:
                        if self.__output_dimensions_cache: predicted_output_stacked = predicted_output_flat.reshape(number_of_samples_in_the_batch, *self.__output_dimensions_cache)
                        elif predicted_output_flat.dim() == 2 and predicted_output_flat.shape[1] == 1: predicted_output_stacked = predicted_output_flat.squeeze(-1)
                        else: predicted_output_stacked = predicted_output_flat
                    except: predicted_output_stacked = predicted_output_flat
                else: predicted_output_stacked = predicted_output_flat.squeeze(-1) if predicted_output_flat.dim() > 1 and predicted_output_flat.shape[-1] == 1 else predicted_output_flat
            else:
                output_shape_per_sample = self.__output_dimensions_cache if self.__output_dimensions_cache else []
                if not output_shape_per_sample: return self.__torch_zeros(number_of_samples_in_the_batch, device=self.__selected_device)
                else: return self.__torch_zeros(number_of_samples_in_the_batch, *output_shape_per_sample, device=self.__selected_device)
            if predicted_output_stacked is not None: return self.__apply_activation_function_to_tensor(predicted_output_stacked, self.__activation_name)
            else: 
                output_shape_per_sample = self.__output_dimensions_cache if self.__output_dimensions_cache else []
                if not output_shape_per_sample: return self.__torch_zeros(number_of_samples_in_the_batch, device=self.__selected_device)
                else: return self.__torch_zeros(number_of_samples_in_the_batch, *output_shape_per_sample, device=self.__selected_device)
        except Exception as error:
            print('ERROR in HurNetTransformer.forward: ' + str(error))
            return x
# THIS IS A HURNET TYPE ARTIFICIAL NEURAL NETWORK
"""
# HurNetTorch: A New Era in Neural Networks
HurNetTorch represents a significant evolution of the original HurNet architecture, maintaining its core computations while leveraging the flexibility of PyTorch’s dynamic tensors.
This advanced implementation offers substantial improvements in both training and inference, ensuring compatibility with a wide range of processing devices, including CPU, GPU, TPU, and MPS.

## Key Features
The module includes specialized extensions for developing Transformer-based language models, specifically tailored to integrate the unique computational logic of the HurNet network.
This integration allows exploring new horizons in natural language processing with superior computational efficiency.

## Revolutionary Paradigm
At the heart of HurNetTorch is the HurNet architecture, which introduces a completely new paradigm for artificial neural networks.
Unlike conventional approaches that rely on iterative weight adjustments through gradient calculations and multiple backpropagation cycles, HurNet implements a novel direct adjustment method.

This method uses division calculations that propagate in a single pass from the network’s output to the input, eliminating the need for repetitive processes.
This revolutionary approach results in a dramatic reduction in high-performance hardware requirements,
providing extraordinary gains in execution speed and making neural network training more accessible and efficient.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
