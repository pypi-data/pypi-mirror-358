import tensorflow as tf
class LogLU(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(LogLU, self).__init__(**kwargs)
    def call(self, inputs):
        return self.loglu_activation(inputs)
    @tf.custom_gradient
    def loglu_activation(self, inputs):
        epsilon = 1e-8
        inputs = tf.cast(inputs, dtype=tf.float16)
        inputs_clipped = tf.clip_by_value(inputs, -1.0 + epsilon, tf.float16.max)
        outputs = tf.where(inputs > 0, inputs, -tf.math.log1p(-inputs_clipped) + epsilon)
        def grad(dy):
            grad_inputs = tf.where(inputs > 0, 1.0, 1.0 / (-inputs_clipped + 1.0)+ epsilon)
            return dy * grad_inputs
        return outputs, grad
    def get_config(self):
        config = super(LogLU, self).get_config()
        return config
