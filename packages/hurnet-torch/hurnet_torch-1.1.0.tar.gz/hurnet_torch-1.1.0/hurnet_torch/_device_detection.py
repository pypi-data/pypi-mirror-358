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
class DeviceDetection(Module):
	def __init__(self):
		try:
			from torch import device as torch_device_class
			from torch import cuda as torch_cuda
			from torch.backends import mps as torch_mps
			try: from torch_xla.core.xla_model import xm as torch_xm_module
			except: torch_xm_module = None
			self.__torch_device_class = torch_device_class
			self.__torch_cuda = torch_cuda
			self.__torch_mps = torch_mps
			self.__torch_xm_module = torch_xm_module
		except Exception as error: print('ERROR in DeviceDetection.__init__: ' + str(error))
	def getDevice(self, device=None):
		try:
			requested_string_device_type, final_device_object = None, None
			if isinstance(device, str): requested_string_device_type = device.lower().strip()
			elif isinstance(device, self.__torch_device_class):  requested_string_device_type = device.type
			if requested_string_device_type:
				if requested_string_device_type in ('cuda', 'gpu') and self.__torch_cuda.is_available(): final_device_object = self.__torch_device_class('cuda')
				elif requested_string_device_type == 'mps' and self.__torch_mps.is_available(): final_device_object = self.__torch_device_class('mps')
				elif self.__torch_xm_module and requested_string_device_type in ('xla', 'tpu'): final_device_object = self.__torch_xm_module.xla_device()
				else: final_device_object = self.__torch_device_class('cpu')
			if final_device_object is None: 
				if self.__torch_cuda.is_available(): final_device_object = self.__torch_device_class('cuda')
				elif self.__torch_mps.is_available(): final_device_object = self.__torch_device_class('mps')
				elif self.__torch_xm_module: final_device_object = self.__torch_xm_module.xla_device()
				else: final_device_object = self.__torch_device_class('cpu')
			return final_device_object
		except Exception as error:
			print('ERROR in DeviceDetection.getDevice: ' + str(error))
			return self.__torch_device_class('cpu')
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
