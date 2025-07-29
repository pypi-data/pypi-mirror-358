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
class HurNetTorch(Module):
    def __init__(self, device=None, dtype=None, show_errors=True):
        try: self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
        except: self.__show_errors = True
        try:
            from warnings import filterwarnings
            from os import environ
            from ._device_detection import DeviceDetection
            from torch import tensor as torch_tensor, Tensor as tensor_torch
            from torch import float32 as torch_float32
            from numpy import array as numpy_array
            from torch import stack as torch_stack
            from ._activation_functions import ActivationFunctions
            from torch import randn as torch_randn
            from tqdm import tqdm
            from torch import pinverse as torch_pinverse
            from io import BytesIO as bytes_io
            from torch import save as torch_save
            from os import path as os_path
            from torch import load as torch_load
        except Exception as error:
            if self.__show_errors: print('ERROR when importing in HurNetTorch.__init__: ' + str(error))
        try:
            filterwarnings('ignore')
            environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            self.__dtype = dtype
            self.__device = DeviceDetection().getDevice(device=device)
            self.__torch_tensor = torch_tensor
            self.__torch_float32 = torch_float32
            self.__tensor_torch = tensor_torch
            self.__numpy_array = numpy_array
            self.__quantization = None
            self.__torch_stack = torch_stack
            self.__weights_vector = []
            self.__hidden_weights = []
            self.__hidden_biases = []
            self.__weights_list = []
            self.__weights_matrix = []
            self.__output_dimensions = [1]
            self.__activation_functions = ActivationFunctions
            self.__hidden_layers = []
            self.__one_dimensional_input = 0
            self.__one_dimensional_output = 0
            self.__method = 'pseudo-inverse'
            self.__torch_randn = torch_randn
            self.__tqdm = tqdm
            self.__torch_pinverse = torch_pinverse
            self.__activation_function = 'linear'
            self.__vector_length = 1
            self.__bytes_io = bytes_io
            self.__torch_save = torch_save
            self.__os_path = os_path
            self.__torch_load = torch_load
            self.__load_model = False
            self.__second_prediction = False
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.__init__: ' + str(error))
    def __toTensor(self, array=[]):
        try:
            try:
                def torchTensor(_array=[]):
                    if self.__dtype is not None: return self.__torch_tensor(_array, dtype=self.__dtype, device=self.__device)
                    torch_float32 = self.__method == 'pseudo-inverse' or self.__device.type == 'mps'
                    return self.__torch_tensor(_array, dtype=self.__torch_float32, device=self.__device) if torch_float32 else self.__torch_tensor(_array).to(self.__device)
                try: return torchTensor(_array=array)
                except: return [torchTensor(_array=element) for element in array]
            except: return self.__torch_tensor(array)
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.__toTensor: ' + str(error))
            return array
    def __standardizesAttributes(self, for_list=True):
        try:
            default_tensor = self.__toTensor(array=[])
            type_tensor = type(default_tensor)
            def prepareArray(array=[]):
                try:
                    type_array = type(array)
                    length_of_hidden_weights = len(self.__hidden_weights)
                    if type_array in (tuple, list) and len(array) > 0 and type(array[0]) == type_tensor: array = [element.tolist() for element in array] if length_of_hidden_weights > 1 else self.__torch_stack(array).tolist()
                    elif type_array == type_tensor: array = array.tolist()
                    return array
                except:
                    try:
                        def convertTensorsToList(structure=[]):
                            if isinstance(structure, self.__tensor_torch): return structure.tolist()
                            elif isinstance(structure, (tuple, list)): return type(structure)(convertTensorsToList(x) for x in structure)
                            elif isinstance(structure, dict): return {x: convertTensorsToList(y) for x, y in structure.items()}
                            else: return structure
                        return convertTensorsToList(structure=array)
                    except: return array   
            if for_list:
                def toList(array=default_tensor):
                    try:
                        def roundsElements(elements=[]): return self.__numpy_array(elements).round(self.__quantization).tolist() if self.__quantization is not None else elements
                        array = prepareArray(array=array)
                        return roundsElements(elements=array)
                    except: return array
                self.__weights_vector = toList(array=self.__weights_vector)
                self.__hidden_weights = toList(array=self.__hidden_weights)
                self.__hidden_biases = toList(array=self.__hidden_biases)
                self.__weights_list = toList(array=self.__weights_list)
                self.__weights_matrix = toList(array=self.__weights_matrix)
                self.__output_dimensions = toList(array=self.__output_dimensions)
            else:
                def toTensor(array=[]):
                    try: 
                        array = prepareArray(array=array)
                        type_array = type(array)
                        return self.__toTensor(array=array) if type_array in (tuple, list) else array
                    except: return array
                self.__weights_vector = toTensor(self.__weights_vector)
                self.__hidden_weights = toTensor(self.__hidden_weights)
                self.__hidden_biases = toTensor(self.__hidden_biases)
                self.__weights_list = toTensor(self.__weights_list)
                self.__weights_matrix = toTensor(self.__weights_matrix)
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.__standardizesAttributes with for_list equal to ' + str(for_list) + ': ' + str(error))
    def __applyHiddenLayers(self, input_vector=[], activation_function='linear'):
        try:
            activation_functions = self.__activation_functions()
            def applyActivationFunction(hidden_layer=[]):
                try:
                    for index, (neuron_count, activation_name) in enumerate(self.__hidden_layers):
                        weight = self.__hidden_weights[index]
                        bias = self.__hidden_biases[index]
                        linear = hidden_layer @ weight + bias
                        hidden_layer = activation_functions.apply(input_tensor=linear, activation_function_name=activation_name)
                    return hidden_layer
                except: return hidden_layer
            hidden_layer = input_vector
            hidden_layer = applyActivationFunction(hidden_layer=hidden_layer)
            return applyActivationFunction(hidden_layer=hidden_layer) if activation_function != 'linear' else hidden_layer
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.__applyHiddenLayers: ' + str(error))
            return input_vector
    def __countElementsPerVector(self, input_tensor=[]):
        try:
            default_tensor = self.__toTensor(array=[])
            if type(input_tensor) == type(default_tensor): return input_tensor.shape[-1]
            elif isinstance(input_tensor, (list, tuple)):
                if len(input_tensor) == 0: return 1
                first = input_tensor[0]
                if isinstance(first, (int, float)): return len(input_tensor)
                else: return self.__countElementsPerVector(first)
            else: return 1
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.__countElementsPerVector: ' + str(error))
            return 1
    def toAdjustInnerLength(self, input_tensor=[], numeric_length=None):
        try:
            if numeric_length is None: return input_tensor
            type_input, type_tensor, type_tuple, type_list = type(input_tensor), type(self.__toTensor(array=[])), type((0,)), type([])
            if type_input != type_tensor:
                input_tensor = list(input_tensor) if type_input in (type_tuple, type_list) else [input_layer]
                input_tensor = self.__toTensor(array=input_tensor)
            last_dimension = input_tensor.size(-1)
            def getResult(result_tensor=[]):
                if type_input == tuple: return tuple(result_tensor.tolist())
                elif type_input == list: return result_tensor.tolist()
                else: return result_tensor
            if last_dimension == numeric_length: return getResult(result_tensor=input_tensor)
            if last_dimension > numeric_length: return getResult(result_tensor=input_tensor[..., :numeric_length])
            new_shape = list(input_tensor.shape)
            new_shape[-1] = numeric_length
            result_tensor = input_tensor.new_zeros(new_shape)
            result_tensor[..., :last_dimension] = input_tensor
            return getResult(result_tensor=result_tensor)
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.toAdjustInnerLength: ' + str(error))
            return input_tensor
    def addHiddenLayer(self, num_neurons=1, activation_function='linear'):
        try:
            num_neurons = max((1, int(num_neurons))) if type(num_neurons) in (bool, int, float) else 1
            activation_function = str(activation_function).lower().strip()
            self.__hidden_layers.append([num_neurons, activation_function])
            return len(self.__hidden_layers) > 0
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.addHiddenLayer: ' + str(error))
            return False
    def train(self, input_layer=[], output_layer=[], activation_function='linear', bias=0.0, learning_rate=1.0, quantization=None, method='division', progress=False):
        try:
            input_layer = list(input_layer) if type(input_layer) in (tuple, list) else [input_layer]
            output_layer = list(output_layer) if type(output_layer) in (tuple, list) else [output_layer]
            activation_function = str(activation_function).lower().strip()
            bias = float(bias) if type(bias) in (bool, int, float) else 0.0
            learning_rate = float(learning_rate) if type(learning_rate) in (bool, int, float) else 1.0
            if quantization is not None: quantization = max((0, int(quantization))) if type(quantization) in (bool, int, float) else None
            method = str(method).lower().strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else False
            if len(input_layer) > 0 and type(input_layer[0]) in (bool, int, float): input_layer, self.__one_dimensional_input = [[_input] for _input in input_layer], 1
            if len(output_layer) > 0 and type(output_layer[0]) in (bool, int, float): output_layer, self.__one_dimensional_output = [[_output] for _output in output_layer], 1
            input_tensor, target_tensor = self.__toTensor(array=input_layer), self.__toTensor(array=output_layer)
            self.__quantization = quantization
            if (input_tensor.dim() == 1 and target_tensor.dim() == 1 and method == 'division'):
                weights_vector = self.__toTensor(array=input_tensor.shape).zero_()
                nonzero_mask = input_tensor != 0
                weights_vector[nonzero_mask] = target_tensor[nonzero_mask] / input_tensor[nonzero_mask]
                if quantization is not None: weights_vector = weights_vector.round(decimals=quantization)
                self.__weights_vector = weights_vector.add(bias).mul(learning_rate)
                self.__method = 'division_1d'
                self.__standardizesAttributes(for_list=True)
                return True
            if method == 'division':
                self.__output_dimensions = (list(target_tensor.shape[1:]) if target_tensor.dim() > 1 else [])
                self.__method = 'division'
                samples_number = input_tensor.shape[0]
                if self.__hidden_layers and not self.__hidden_weights:
                    previous_dimension = input_tensor.shape[1]
                    for (neuron_count, activation_name) in self.__hidden_layers:
                        weight = self.__torch_randn((previous_dimension, neuron_count), dtype=self.__torch_float32, device=self.__device)
                        hidden_bias = self.__torch_randn((neuron_count,), dtype=self.__torch_float32, device=self.__device)
                        self.__hidden_weights.append(weight)
                        self.__hidden_biases.append(hidden_bias)
                        previous_dimension = neuron_count
                indexes, weights_list = range(samples_number), []
                if progress: indexes = self.__tqdm(indexes, desc='Training model')
                for index in indexes:
                    sample = input_tensor[index]
                    if self.__hidden_layers: hidden_layer = self.__applyHiddenLayers(input_vector=sample, activation_function=activation_function)
                    else: hidden_layer = sample.reshape(-1)
                    target_sample, sum_hidden = target_tensor[index], hidden_layer.sum()
                    if sum_hidden == 0: weights_sample = target_sample.clone().zero_()
                    else:
                        weights_sample = ((target_sample / sum_hidden) + bias) * learning_rate
                        if quantization is not None:
                            try: weights_sample = weights_sample.round(decimals=quantization)
                            except:
                                factor = 10 ** quantization
                                weights_sample = (weights_sample * factor).round() / factor
                    weights_list.append(weights_sample)
                self.__weights_list = weights_list
                self.__standardizesAttributes(for_list=True)
                return True
            self.__output_dimensions = (list(target_tensor.shape[1:]) if target_tensor.dim() > 1 else [])
            self.__method = method
            samples_number = input_tensor.shape[0]
            if self.__hidden_layers and not self.__hidden_weights:
                previous_dimension = input_tensor.shape[1]
                for (neuron_count, activation_name) in self.__hidden_layers:
                    weight = self.__torch_randn((previous_dimension, neuron_count), dtype=self.__torch_float32, device=self.__device)
                    hidden_bias = self.__torch_randn((neuron_count,), dtype=self.__torch_float32, device=self.__device)
                    self.__hidden_weights.append(weight)
                    self.__hidden_biases.append(hidden_bias)
                    previous_dimension = neuron_count
            if self.__hidden_layers:
                indexes, hidden_activations = range(samples_number), []
                if progress: indexes = self.__tqdm(indexes, desc='Training model')
                for index in indexes:
                    sample = input_tensor[index]
                    hidden_layer = self.__applyHiddenLayers(input_vector=sample, activation_function=activation_function)
                    hidden_activations.append(hidden_layer)
                hidden_stack = self.__torch_stack(hidden_activations, dim=0)
                input_flattened = hidden_stack
            else: input_flattened = input_tensor.reshape(samples_number, -1)
            output_flattened = target_tensor.reshape(samples_number, -1)
            if self.__device.type == 'mps':
                input_cpu, output_cpu = input_flattened.cpu(), output_flattened.cpu()
                weights_cpu = self.__torch_pinverse(input_cpu) @ output_cpu
                weights_matrix = weights_cpu.to(self.__device)
            else: weights_matrix = self.__torch_pinverse(input_flattened) @ output_flattened
            if quantization is not None: weights_matrix = weights_matrix.round(decimals=quantization)
            self.__activation_function = activation_function
            self.__weights_matrix = weights_matrix.add(bias).mul(learning_rate)
            self.__vector_length = self.__countElementsPerVector(input_tensor=input_tensor)
            self.__standardizesAttributes(for_list=True)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.train: ' + str(error))
            return False
    def getParameters(self):
        try:
            return_state = {
                'one_dimensional_input': int(self.__one_dimensional_input),
                'one_dimensional_output': int(self.__one_dimensional_output),
                'method': str(self.__method).lower().strip(),
                'weights_vector': self.__weights_vector,
                'activation_function': str(self.__activation_function).lower().strip(),
                'hidden_layers': self.__hidden_layers,
                'hidden_weights': self.__hidden_weights,
                'hidden_biases': self.__hidden_biases,
                'weights_list': self.__weights_list,
                'weights_matrix': self.__weights_matrix,
                'output_dimensions': self.__output_dimensions,
                'vector_length': int(self.__vector_length)
            }
            return return_state
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.getParameters: ' + str(error))
            return {
                'one_dimensional_input': 0,
                'one_dimensional_output': 0,
                'method': 'pseudo-inverse',
                'weights_vector': [],
                'activation_function': 'linear',
                'hidden_layers': [],
                'hidden_weights': [],
                'hidden_biases': [],
                'weights_list': [],
                'weights_matrix': [],
                'output_dimensions': [1],
                'vector_length': 1
            }
    def setParameters(self, state={}):
        try:
            if type(state) != dict: return False
            if 'one_dimensional_input' in state: self.__one_dimensional_input = int(state['one_dimensional_input']) if type(state['one_dimensional_input']) in (bool, int, float) else 0
            if 'one_dimensional_output' in state: self.__one_dimensional_output = int(state['one_dimensional_output']) if type(state['one_dimensional_output']) in (bool, int, float) else 0
            if 'method' in state: self.__method = str(state['method']).lower().strip()
            if 'weights_vector' in state: self.__weights_vector = list(state['weights_vector']) if type(state['weights_vector']) in (tuple, list) else []
            if 'activation_function' in state: self.__activation_function = str(state['activation_function']).lower().strip()
            if 'hidden_layers' in state: self.__hidden_layers = list(state['hidden_layers']) if type(state['hidden_layers']) in (tuple, list) else []
            if 'hidden_weights' in state: self.__hidden_weights = list(state['hidden_weights']) if type(state['hidden_weights']) in (tuple, list) else []
            if 'hidden_biases' in state: self.__hidden_biases = list(state['hidden_biases']) if type(state['hidden_biases']) in (tuple, list) else []
            if 'weights_list' in state: self.__weights_list = list(state['weights_list']) if type(state['weights_list']) in (tuple, list) else []
            if 'weights_matrix' in state: self.__weights_matrix = list(state['weights_matrix']) if type(state['weights_matrix']) in (tuple, list) else []
            if 'output_dimensions' in state: self.__output_dimensions = list(state['output_dimensions']) if type(state['output_dimensions']) in (tuple, list) else [1]
            if 'vector_length' in state: self.__vector_length = int(state['vector_length']) if type(state['vector_length']) in (bool, int, float) else 1
            self.__standardizesAttributes(for_list=False)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.getParameters: ' + str(error))
            return False
    def saveModel(self, model_path='', progress=False):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else False
            model_path = model_path if model_path else './model.hurnettorch'
            if not model_path.endswith('.hurnettorch'): model_path += '.hurnettorch'
            state = self.getParameters()
            if progress:
                buffer = self.__bytes_io()
                self.__torch_save(state, buffer)
                total_bytes = buffer.tell()
                buffer.seek(0)
                class _TqdmWriter:
                    def __init__(self, file_obj, tqdm_inst): self._file, self._tqdm = file_obj, tqdm_inst
                    def write(self, data):
                        self._file.write(data)
                        self._tqdm.update(len(data))
                    def flush(self): self._file.flush()
                with open(model_path, 'wb') as file:
                    with self.__tqdm(total=total_bytes, unit='B', unit_scale=True, desc='Saving model') as data:
                        wrapped = _TqdmWriter(file, data)
                        self.__torch_save(state, wrapped)
            else: self.__torch_save(state, model_path)
            return True
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.saveModel: ' + str(error))
            return False
    def loadModel(self, model_path='', progress=False):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else False
            model_path = model_path if model_path else './model.hurnettorch'
            if not model_path.endswith('.hurnettorch'): model_path += '.hurnettorch'
            if not self.__os_path.exists(model_path):
                print('The model was not found on the path: ' + str(model_path))
                return False
            if progress:
                total_bytes = self.__os_path.getsize(model_path)
                chunk_size, buffer = 1024 * 1024, self.__bytes_io()
                with open(model_path, 'rb') as file, self.__tqdm(total=total_bytes, unit='B', unit_scale=True, desc='Loading model') as data:
                    while True:
                        chunk = file.read(chunk_size)
                        if not chunk: break
                        buffer.write(chunk)
                        data.update(len(chunk))
                buffer.seek(0)
                state = self.__torch_load(buffer, map_location=self.__device)
            else: state = self.__torch_load(model_path, map_location=self.__device)
            self.setParameters(state=state)
            self.__load_model = True
            return self.__load_model
        except Exception as error:
            if self.__show_errors: print('ERROR in HurNetTorch.loadModel: ' + str(error))
            return False
    def predict(self, input_layer=[], decimal_places=None):
        try:
            input_layer = list(input_layer) if type(input_layer) in (tuple, list) else [input_layer]
            decimal_places = max((0, int(decimal_places))) if type(decimal_places) in (bool, int, float) else 8
            if self.__one_dimensional_input: input_layer = [[_input] for _input in input_layer]
            input_prediction = self.__toTensor(array=input_layer)
            if not self.__load_model: self.__standardizesAttributes(for_list=False)
            def adaptOutput(output_layer=[]):
                if self.__one_dimensional_output: output_layer = [_output[0] for _output in output_layer]
                output_layer = self.__numpy_array(output_layer)
                if decimal_places <= 0: output_layer = output_layer.round().astype(int)
                else: output_layer = output_layer.round(decimal_places) if decimal_places is not None else output_layer
                return output_layer.tolist()
            if input_prediction.dim() == 1 and self.__method == 'division_1d':
                output_tensor = input_prediction * self.__weights_vector
                if output_tensor.device.type == 'mps':
                    output_cpu = output_tensor.cpu()
                    return adaptOutput(output_layer=output_cpu.tolist())
                else: return adaptOutput(output_layer=output_tensor.cpu().tolist())
            samples_number, results = input_prediction.shape[0], []
            if self.__method == 'division':
                for index in range(samples_number):
                    sample = input_prediction[index]
                    if self.__hidden_layers: hidden_layer = self.__applyHiddenLayers(input_vector=sample, activation_function=self.__activation_function)
                    else: hidden_layer = sample.reshape(-1)
                    sum_hidden = hidden_layer.sum()
                    weights_sample = self.__weights_list[index % len(self.__weights_list)]
                    try: output_tensor = sum_hidden * weights_sample
                    except: output_tensor = self.__toTensor(array=weights_sample)
                    if output_tensor.device.type == 'mps':
                        output_cpu = output_tensor.cpu()
                        results.append(output_cpu.tolist())
                    else: results.append(output_tensor.cpu().tolist())
                return adaptOutput(output_layer=results)
            for index in range(samples_number):
                sample = input_prediction[index]
                if self.__hidden_layers: hidden_layer = self.__applyHiddenLayers(input_vector=sample, activation_function=self.__activation_function)
                else: hidden_layer = sample.reshape(-1)
                output_flat = hidden_layer @ self.__weights_matrix
                if self.__output_dimensions != []: output_tensor = output_flat.reshape(*self.__output_dimensions)
                else: output_tensor = output_flat
                if self.__device.type == 'mps':
                    output_cpu = output_tensor.cpu()
                    results.append(output_cpu.tolist())
                else: results.append(output_tensor.cpu().tolist())
            return adaptOutput(output_layer=results)
        except Exception as error:
            vector_length = self.__countElementsPerVector(input_tensor=input_layer)
            if not self.__second_prediction and vector_length != self.__vector_length:
                self.__second_prediction = True
                input_layer = self.toAdjustInnerLength(input_tensor=input_layer, numeric_length=self.__vector_length)
                return self.predict(input_layer=input_layer, decimal_places=decimal_places)
            else:
                if self.__show_errors: print('ERROR in HurNetTorch.predict: ' + str(error))
                return []
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
