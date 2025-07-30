
## Installation

To install ZenGrad, run the following command:

```bash
pip install zengrad-tensorflow
```

## Implementation

```python
from zengrad_tensorflow import ZenGrad  # Import the ZenGrad optimizer

# Define your preferred model architecture here (e.g., CNN, ResNet, LSTM, Transformer, etc.)
# Example:
# model = ...

# Compile your model using ZenGrad

model.compile(
    optimizer=ZenGrad(learning_rate=0.01, weight_decay=1e-4),  # <---- In This Way
    .......                 
)

```

## License

ZenGrad_TensorFlow is released under the [Apache License 2.0](https://github.com/XenReZ/ZenGrad-TensorFlow/blob/main/LICENSE).