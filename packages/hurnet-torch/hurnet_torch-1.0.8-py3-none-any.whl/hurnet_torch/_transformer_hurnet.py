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
class TransformerHurNet(Module):
    def __init__(self, embedding_dim=0, block_size=0, number_heads=0, number_layers=0, dropout=None, vocab_size=0, device=None, outer=None):
        try:
            super().__init__()
            embedding_dim = max((0, int(embedding_dim))) if type(embedding_dim) in (bool, int, float) else 0
            block_size = max((0, int(block_size))) if type(block_size) in (bool, int, float) else 0
            number_heads = max((0, int(number_heads))) if type(number_heads) in (bool, int, float) else 0
            number_layers = max((0, int(number_layers))) if type(number_layers) in (bool, int, float) else 0
            vocab_size = max((0, int(vocab_size))) if type(vocab_size) in (bool, int, float) else 0
            from torch.nn import Parameter as torch_parameter
            from torch import tensor as torch_tensor
            from torch.nn import Dropout as torch_dropout
            from torch.nn import Embedding as torch_embedding
            from torch.nn import TransformerDecoder as torch_transformer_decoder
            from torch.nn import TransformerDecoderLayer as torch_transformer_decoder_layer
            from ._hurnet_transformer import HurNetTransformer
            from ._device_detection import DeviceDetection
            from torch import triu as torch_triu
            from torch import ones as torch_ones
            self.positional_encoding = torch_parameter(torch_tensor([]).new_zeros(1, block_size, embedding_dim))
            self.dropout = torch_dropout(dropout)
            self.embedding = torch_embedding(vocab_size, embedding_dim)
            self.__torch_triu = torch_triu
            self.__torch_ones = torch_ones
            self.multi_head_attention = torch_transformer_decoder(torch_transformer_decoder_layer(d_model=embedding_dim, nhead=number_heads, dropout=dropout, batch_first=True), num_layers=number_layers)
            final_device_object = DeviceDetection().getDevice(device=device)
            self.hurnet_layer, self.outer = HurNetTransformer(embedding_dim, vocab_size, activation_function='linear', interaction=True, device=final_device_object), outer
        except Exception as error: print('ERROR in TransformerHurNet.__init__: ' + str(error))
    def forward(self, input_tensor=default_tensor):
        try:
            if type(input_tensor) != type(input_tensor): input_tensor = global_tensor(input_tensor) if type(input_tensor) in (tuple, list) else input_tensor
            batch_size, sequence_length = input_tensor.size()
            positions = self.positional_encoding[:, :sequence_length, :].to(input_tensor.device)
            input_embedding = self.dropout(self.embedding(input_tensor) + positions)
            masked_multi_head_attention = self.__torch_triu(self.__torch_ones(sequence_length, sequence_length, device=input_tensor.device) * float('-inf'), diagonal=1)
            output_embedding = self.multi_head_attention(input_embedding, memory=input_embedding, tgt_mask=masked_multi_head_attention)
            return self.hurnet_layer(output_embedding.reshape(-1, output_embedding.size(-1))).view(batch_size, sequence_length, -1)
        except Exception as error:
            print('ERROR in TransformerHurNet.forward: ' + str(error))
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
