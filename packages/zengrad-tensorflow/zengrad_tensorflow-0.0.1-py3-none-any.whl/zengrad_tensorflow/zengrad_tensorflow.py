import tensorflow as tf
from keras import layers, models
from keras.src import initializers, ops
from keras.src.optimizers import optimizer

class ZenGrad(optimizer.Optimizer):
    def __init__(
        self,
        learning_rate=0.01,
        initial_accumulator_value=0.1,
        weight_decay=1e-4,
        epsilon=1e-8,
        name="ZenGrad",
        **kwargs,
    ):
        super().__init__(
            learning_rate=learning_rate,
            name=name,
            **kwargs,
        )
        self.initial_accumulator_value = initial_accumulator_value
        self.weight_decay = weight_decay
        self.epsilon = epsilon

    def build(self, var_list):
        if self.built:
            return
        super().build(var_list)
        self._accumulators = []
        initializer = initializers.Constant(self.initial_accumulator_value)
        for var in var_list:
            self._accumulators.append(
                self.add_variable(
                    name="accumulator",
                    shape=var.shape,
                    dtype=var.dtype,
                    initializer=initializer,
                )
            )

    def update_step(self, gradient, variable, learning_rate):
        lr = ops.cast(learning_rate, variable.dtype)
        gradient = ops.cast(gradient, variable.dtype)

        accumulator = self._accumulators[self._get_variable_index(variable)]

        # A_t = A_{t-1} + g_t^2
        self.assign_add(accumulator, ops.square(gradient))

        # Optional: decoupled weight decay
        if self.weight_decay > 0.0:
            self.assign_sub(variable, variable * lr * self.weight_decay)

        # Effective learning rate and parameter update
        self.assign_sub(
            variable,
            ops.divide(
                ops.multiply(lr, gradient),
                ops.add(ops.log(ops.add(accumulator, 1.0)), self.epsilon),
            ),
        )

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "initial_accumulator_value": self.initial_accumulator_value,
                "weight_decay": self.weight_decay,
                "epsilon": self.epsilon,
            }
        )
        return config
