
### Installation

To use LogLU, simply install it using the following command:

```bash
pip install loglu-tensorflow
```

### Implementation

```python
import tensorflow as tf
from loglu_tensorflow import LogLU # Importing the LogLU activation function from the loglu package

# Define a model
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(128, input_shape=(784,)),
    tf.keras.layers.Activation(LogLU()),  # Use LogLU as the activation function
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model

# Summary of the model
model.summary()
```

## License

LogLU-TensorFlow is released under the [Apache License 2.0](https://github.com/XenReZ/LogLU-TensorFlow/blob/main/LICENSE).
