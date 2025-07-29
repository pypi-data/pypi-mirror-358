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
class ActivationFunctions(Module):
	def __init__(self):
		try:
			from torch.nn.functional import sigmoid as torch_sigmoid
			from torch.nn.functional import hardsigmoid as torch_hard_sigmoid
			from torch.nn.functional import tanh as torch_tanh
			from torch.nn.functional import relu as torch_relu
			from torch.nn.functional import leaky_relu as torch_leaky_relu
			from torch.nn.functional import softmax as torch_softmax
			from torch.nn.functional import softplus as torch_softplus
			from torch.nn.functional import elu as torch_elu
			from torch.nn.functional import silu as torch_silu
			from torch.nn.functional import gelu as torch_gelu
			from torch.nn.functional import selu as torch_selu
			from torch.nn.functional import mish as torch_mish
			self.__torch_sigmoid = torch_sigmoid
			self.__torch_hard_sigmoid = torch_hard_sigmoid
			self.__torch_tanh = torch_tanh
			self.__torch_relu = torch_relu
			self.__torch_leaky_relu = torch_leaky_relu
			self.__torch_softmax = torch_softmax
			self.__torch_softplus = torch_softplus
			self.__torch_elu = torch_elu
			self.__torch_silu = torch_silu
			self.__torch_gelu = torch_gelu
			self.__torch_selu = torch_selu
			self.__torch_mish = torch_mish
		except Exception as error: print('ERROR in ActivationFunctions.__init__: ' + str(error))
	def apply(self, input_tensor=default_tensor, activation_function_name='linear'):
		try:
			activation_function_name = str(activation_function_name).lower().strip()
			if activation_function_name == 'sigmoid': return self.__torch_sigmoid(input_tensor)
			elif activation_function_name in ('hard_sigmoid', 'hardsigmoid'): return self.__torch_hard_sigmoid(input_tensor)
			elif activation_function_name == 'tanh': return self.__torch_tanh(input_tensor)
			elif activation_function_name == 'relu': return self.__torch_relu(input_tensor)
			elif activation_function_name == ('leaky_relu', 'leakyrelu'): return self.__torch_leaky_relu(input_tensor)
			elif activation_function_name == 'softmax': return self.__torch_softmax(input_tensor, dim=-1)
			elif activation_function_name == 'softplus': return self.__torch_softplus(input_tensor)
			elif activation_function_name == 'elu': return self.__torch_elu(input_tensor)
			elif activation_function_name in ('silu', 'swish'): return self.__torch_silu(input_tensor)
			elif activation_function_name == 'gelu': return self.__torch_gelu(input_tensor)
			elif activation_function_name == 'selu': return self.__torch_selu(input_tensor)
			elif activation_function_name == 'mish': return self.__torch_mish(input_tensor)
			else: return input_tensor
		except Exception as error:
			print('ERROR in ActivationFunctions.apply: ' + str(error))
			return input_tensor
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
