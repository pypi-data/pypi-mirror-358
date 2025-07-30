import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Dense, Dropout, LayerNormalization


def about():
    print("""
        gpbacay_arcane:
        - A Python library for custom neuromimetic artificial neural network mechanisms built on top of TensorFlow and Keras.
        This library provides specialized layers and mechanisms for the A.R.C.A.N.E 
        (Augmented Reconstruction of Consciousness through Artificial Neural Evolution) project, 
        enabling the creation of adaptive, biologically-inspired neural networks. 
        It includes features like dynamic reservoirs, spiking neurons, Hebbian learning, and more, 
        all built on top of TensorFlow and Keras.

        """
    )
    
    
    
    
class ExpandDimensionLayer(tf.keras.layers.Layer):
            def call(self, inputs):
                return tf.expand_dims(inputs, axis=1)




class DenseReservoirLayer(tf.keras.layers.Layer):
    def __init__(self, units, input_dim=None, spectral_radius=None, leak_rate=None, spike_threshold=None, 
                 max_dynamic_units=None, activation='relu', kernel_initializer='glorot_uniform', 
                 bias_initializer='zeros', kernel_regularizer=None, bias_regularizer=None, name=None, **kwargs):
        super(DenseReservoirLayer, self).__init__(name=name, **kwargs)
        
        self.units = units
        self.input_dim = input_dim
        self.spectral_radius = spectral_radius
        self.leak_rate = leak_rate
        self.spike_threshold = spike_threshold
        self.max_dynamic_units = max_dynamic_units
        self.activation = tf.keras.activations.get(activation)
        self.kernel_initializer = tf.keras.initializers.get(kernel_initializer)
        self.bias_initializer = tf.keras.initializers.get(bias_initializer)
        self.kernel_regularizer = tf.keras.regularizers.get(kernel_regularizer)
        self.bias_regularizer = tf.keras.regularizers.get(bias_regularizer)

    def build(self, input_shape):
        # Initialize input weights with kernel_initializer
        self.input_weights = self.add_weight(
            shape=(self.input_dim, self.units),
            initializer=self.kernel_initializer,
            regularizer=self.kernel_regularizer,
            trainable=True,
            name='input_weights'
        )
        
        # Initialize reservoir weights (non-trainable)
        self.reservoir_weights = self.add_weight(
            shape=(self.input_dim, self.units),
            initializer=self.kernel_initializer,
            trainable=False,
            name='reservoir_weights'
        )
        
        # Initialize gate weights with kernel_initializer
        self.gate_weights = self.add_weight(
            shape=(3 * self.units, self.input_dim),
            initializer=self.kernel_initializer,
            regularizer=self.kernel_regularizer,
            trainable=True,
            name='gate_weights'
        )
        
        # Initialize biases for gates
        self.gate_bias = self.add_weight(
            shape=(3 * self.units,),
            initializer=self.bias_initializer,
            regularizer=self.bias_regularizer,
            trainable=True,
            name='gate_bias'
        )
        
        # Internal dense layer for output adjustment with kernel and bias initializers
        self.dense = tf.keras.layers.Dense(
            self.units,
            activation=self.activation,
            kernel_initializer=self.kernel_initializer,
            bias_initializer=self.bias_initializer,
            kernel_regularizer=self.kernel_regularizer,
            bias_regularizer=self.bias_regularizer,
            name="output_dense"
        )

    def call(self, inputs):
        # Compute input, reservoir, and gate components
        input_part = tf.matmul(inputs, self.input_weights)
        reservoir_part = tf.matmul(inputs, self.reservoir_weights)
        gate_part = tf.matmul(inputs, self.gate_weights, transpose_b=True) + self.gate_bias

        # Split gates
        i_gate, f_gate, o_gate = tf.split(tf.sigmoid(gate_part), 3, axis=-1)

        # Compute state update
        state = (1 - self.leak_rate) * (f_gate * reservoir_part) + self.leak_rate * tf.tanh(i_gate * (input_part + reservoir_part))
        state = o_gate * state

        # Apply spike threshold
        spikes = tf.cast(tf.greater(state, self.spike_threshold), dtype=tf.float32)
        state = tf.where(spikes > 0, state - self.spike_threshold, state)

        # Apply Dense layer for final transformation
        state = self.dense(state)

        return state

    def get_config(self):
        config = super().get_config()
        config.update({
            'units': self.units,
            'input_dim': self.input_dim,
            'spectral_radius': self.spectral_radius,
            'leak_rate': self.leak_rate,
            'spike_threshold': self.spike_threshold,
            'max_dynamic_units': self.max_dynamic_units,
            'activation': tf.keras.activations.serialize(self.activation),
            'kernel_initializer': tf.keras.initializers.serialize(self.kernel_initializer),
            'bias_initializer': tf.keras.initializers.serialize(self.bias_initializer),
            'kernel_regularizer': tf.keras.regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': tf.keras.regularizers.serialize(self.bias_regularizer),
        })
        return config




class GatedSpikingElasticReservoirLayer(tf.keras.layers.Layer):
    def __init__(self, initial_reservoir_size, input_dim, spectral_radius, leak_rate, spike_threshold, max_dynamic_reservoir_dim, **kwargs):
        super().__init__(**kwargs)
        self.initial_reservoir_size = initial_reservoir_size
        self.input_dim = input_dim
        self.spectral_radius = spectral_radius
        self.leak_rate = leak_rate
        self.spike_threshold = spike_threshold
        self.max_dynamic_reservoir_dim = max_dynamic_reservoir_dim
        
        self.state_size = [self.max_dynamic_reservoir_dim]
        self.output_size = self.max_dynamic_reservoir_dim
        
        self.initialize_weights()

    def initialize_weights(self):
        self.spatiotemporal_reservoir_weights = self.add_weight(
            shape=(self.initial_reservoir_size, self.initial_reservoir_size),
            initializer=tf.keras.initializers.RandomNormal(),
            trainable=False,
            name='spatiotemporal_reservoir_weights'
        )
        self.spatiotemporal_input_weights = self.add_weight(
            shape=(self.initial_reservoir_size, self.input_dim),
            initializer=tf.keras.initializers.RandomNormal(stddev=0.1),
            trainable=False,
            name='spatiotemporal_input_weights'
        )
        self.spiking_gate_weights = self.add_weight(
            shape=(3 * self.initial_reservoir_size, self.input_dim),
            initializer=tf.keras.initializers.RandomNormal(stddev=0.1),
            trainable=False,
            name='spiking_gate_weights'
        )

    def call(self, inputs, states):
        prev_state = states[0][:, :tf.shape(self.spatiotemporal_reservoir_weights)[0]]

        input_part = tf.matmul(inputs, self.spatiotemporal_input_weights, transpose_b=True)
        reservoir_part = tf.matmul(prev_state, self.spatiotemporal_reservoir_weights)
        gate_part = tf.matmul(inputs, self.spiking_gate_weights, transpose_b=True)

        i_gate, f_gate, o_gate = tf.split(tf.sigmoid(gate_part), 3, axis=-1)

        state = (1 - self.leak_rate) * (f_gate * prev_state) + self.leak_rate * tf.tanh(i_gate * (input_part + reservoir_part))
        state = o_gate * state

        spikes = tf.cast(tf.greater(state, self.spike_threshold), dtype=tf.float32)
        state = tf.where(spikes > 0, state - self.spike_threshold, state)

        padded_state = tf.concat([state, tf.zeros([tf.shape(state)[0], self.max_dynamic_reservoir_dim - tf.shape(state)[-1]])], axis=1)

        return padded_state, [padded_state]

    def get_config(self):
        config = super().get_config()
        config.update({
            'initial_reservoir_size': self.initial_reservoir_size,
            'input_dim': self.input_dim,
            'spectral_radius': self.spectral_radius,
            'leak_rate': self.leak_rate,
            'spike_threshold': self.spike_threshold,
            'max_dynamic_reservoir_dim': self.max_dynamic_reservoir_dim
        })
        return config




class HebbianHomeostaticLayer(tf.keras.Layer):
    def __init__(self, units, learning_rate=0.00001, target_avg=0.1, homeostatic_rate=0.00001, activation='gelu', **kwargs):
        super(HebbianHomeostaticLayer, self).__init__(**kwargs)
        self.units = units
        self.learning_rate = learning_rate
        self.target_avg = target_avg
        self.homeostatic_rate = homeostatic_rate
        self.activation = tf.keras.activations.get(activation)

    def build(self, input_shape):
        # Handle input shape properly
        if len(input_shape) == 3:  # (batch, timesteps, features)
            feature_dim = input_shape[-1]
        else:  # (batch, features)
            feature_dim = input_shape[-1]

        initializer = tf.keras.initializers.RandomNormal(mean=0., stddev=0.001)
        self.kernel = self.add_weight(
            shape=(feature_dim, self.units),
            initializer=initializer,
            trainable=True,
            name='kernel'
        )
        self.activity_scale = self.add_weight(
            shape=(self.units,),
            initializer=tf.keras.initializers.Ones(),
            trainable=False,  # Homeostatic scaling is not trainable by gradients
            name='activity_scale'
        )
        self.built = True

    def call(self, inputs):
        # Handle input shape
        original_shape = tf.shape(inputs)
        if len(inputs.shape) == 3:
            # Reshape (batch, timesteps, features) to (batch * timesteps, features)
            inputs = tf.reshape(inputs, [-1, inputs.shape[-1]])

        # Normalize inputs
        inputs = tf.nn.l2_normalize(inputs, axis=-1)

        # Normalize weights
        normalized_kernel = tf.nn.l2_normalize(self.kernel, axis=0)

        # Compute outputs
        raw_outputs = tf.matmul(inputs, normalized_kernel)

        # Apply homeostatic scaling
        outputs = raw_outputs * self.activity_scale

        # Apply optional activation
        if self.activation is not None:
            outputs = self.activation(outputs)

        # Hebbian update
        if self.learning_rate > 0:
            # Compute hebbian update
            delta_weights = tf.matmul(
                tf.transpose(inputs), 
                raw_outputs
            ) * self.learning_rate / tf.cast(tf.shape(inputs)[0], tf.float32)
            
            # Update weights with normalization
            new_kernel = self.kernel + delta_weights
            self.kernel.assign(tf.clip_by_norm(new_kernel, 1.0))

        # Homeostatic update
        avg_activity = tf.reduce_mean(raw_outputs, axis=0)
        scale_adjustment = self.homeostatic_rate * (self.target_avg - avg_activity)
        new_scale = tf.clip_by_value(
            self.activity_scale + scale_adjustment,
            0.1,
            2.0
        )
        self.activity_scale.assign(new_scale)

        # Reshape output back to original shape if necessary
        if len(inputs.shape) == 3:
            outputs = tf.reshape(outputs, [original_shape[0], original_shape[1], self.units])

        return outputs

    def compute_output_shape(self, input_shape):
        if len(input_shape) == 3:  # (batch, timesteps, features)
            return (input_shape[0], input_shape[1], self.units)
        return (input_shape[0], self.units)  # (batch, units)

    def get_config(self):
        config = super().get_config()
        config.update({
            'units': self.units,
            'learning_rate': self.learning_rate,
            'target_avg': self.target_avg,
            'homeostatic_rate': self.homeostatic_rate,
            'activation': tf.keras.activations.serialize(self.activation),
        })
        return config




class SpatioTemporalSummaryMixingLayer(tf.keras.Layer):
    def __init__(self, d_model, dropout_rate=0.1, use_weighted_summary=False, **kwargs):
        super(SpatioTemporalSummaryMixingLayer, self).__init__(**kwargs)
        self.d_model = d_model
        self.dropout_rate = dropout_rate
        self.use_weighted_summary = use_weighted_summary

    def build(self, input_shape):
        # Local processing with GLU
        self.local_dense1 = Dense(4 * self.d_model)  # GLU will be applied here
        self.local_dense2 = Dense(self.d_model)
        self.local_dropout = Dropout(self.dropout_rate)

        # Summary processing with GELU
        self.summary_dense1 = Dense(4 * self.d_model, activation='gelu')
        self.summary_dense2 = Dense(self.d_model)
        self.summary_dropout = Dropout(self.dropout_rate)

        if self.use_weighted_summary:
            self.summary_weights = Dense(1, activation='softmax')  # Learnable weights

        # Combining layers with GELU
        self.combiner_dense1 = Dense(4 * self.d_model, activation='gelu')
        self.combiner_dense2 = Dense(self.d_model)
        self.combiner_dropout = Dropout(self.dropout_rate)

        # Dynamic dense layer (potentially using GLU for dynamic gating)
        self.dynamic_dense = Dense(self.d_model)
        
        # Layer normalization
        self.layer_norm = LayerNormalization(epsilon=1e-6)

        super(SpatioTemporalSummaryMixingLayer, self).build(input_shape)

    def call(self, inputs, training=False):
        # Apply GLU for local processing (using split for gating mechanism)
        local_output = self.local_dense1(inputs)
        local_output, gate = tf.split(local_output, 2, axis=-1)  # Split for GLU
        local_output = local_output * tf.sigmoid(gate)  # GLU activation: element-wise multiplication
        local_output = self.local_dense2(local_output)
        local_output = self.local_dropout(local_output, training=training)
        
        # Summary processing with GELU
        summary = self.summary_dense1(inputs)
        summary = self.summary_dense2(summary)
        summary = self.summary_dropout(summary, training=training)

        if self.use_weighted_summary:
            weights = self.summary_weights(summary)  # Learnable token weights
            weighted_summary = tf.reduce_sum(summary * weights, axis=1, keepdims=True)
        else:
            weighted_summary = tf.reduce_mean(summary, axis=1, keepdims=True)

        weighted_summary = tf.tile(weighted_summary, [1, tf.shape(inputs)[1], 1])
        
        # Combine local output and weighted summary
        combined = tf.concat([local_output, weighted_summary], axis=-1)
        output = self.combiner_dense1(combined)
        output = self.combiner_dense2(output)
        output = self.combiner_dropout(output, training=training)

        # Apply dynamic dense layer (optional GLU or GELU, you could try both)
        inputs = self.dynamic_dense(inputs)

        # Return the final output with layer normalization
        return self.layer_norm(inputs + output)

    def get_config(self):
        config = super().get_config()
        config.update({
            'd_model': self.d_model,
            'dropout_rate': self.dropout_rate,
            'use_weighted_summary': self.use_weighted_summary,
        })
        return config




class LinearSummaryAttentionLayer(tf.keras.Layer):
    def __init__(self, d_model, dropout_rate=0.1, use_weighted_summary=False, **kwargs):
        super(LinearSummaryAttentionLayer, self).__init__(**kwargs)
        self.d_model = d_model
        self.dropout_rate = dropout_rate
        self.use_weighted_summary = use_weighted_summary

    def build(self, input_shape):
        # Query, Key, and Value projection layers
        self.query_dense = Dense(self.d_model)
        self.key_dense = Dense(self.d_model)
        self.value_dense = Dense(self.d_model)

        # Output projection layer
        self.output_dense = Dense(self.d_model)

        # Dropout layer
        self.dropout = Dropout(self.dropout_rate)

        # Learnable weights for weighted summaries (optional)
        if self.use_weighted_summary:
            self.summary_weights = Dense(1, activation='softmax')

        # Layer normalization
        self.layer_norm = LayerNormalization(epsilon=1e-6)

        super(LinearSummaryAttentionLayer, self).build(input_shape)

    def call(self, inputs, training=False):
        # Step 1: Project inputs to query, key, and value
        queries = self.query_dense(inputs)  # Shape: (batch_size, seq_len, d_model)
        keys = self.key_dense(inputs)      # Shape: (batch_size, seq_len, d_model)
        values = self.value_dense(inputs)  # Shape: (batch_size, seq_len, d_model)

        # Step 2: Apply kernel trick for linear attention
        queries = tf.nn.elu(queries) + 1  # Positive activation for kernel trick
        keys = tf.nn.elu(keys) + 1

        # Compute similarity scores using the kernel approximation
        scores = tf.matmul(queries, keys, transpose_b=True)  # Shape: (batch_size, seq_len, seq_len)

        # Normalize scores row-wise (scaled attention mechanism)
        scores = scores / tf.reduce_sum(scores, axis=-1, keepdims=True)

        # Step 3: Compute attention output
        attention_output = tf.matmul(scores, values)  # Shape: (batch_size, seq_len, d_model)

        # Step 4: Optional weighted summary extraction
        if self.use_weighted_summary:
            weights = self.summary_weights(attention_output)  # Shape: (batch_size, seq_len, 1)
            weighted_summary = tf.reduce_sum(attention_output * weights, axis=1, keepdims=True)
        else:
            weighted_summary = tf.reduce_mean(attention_output, axis=1, keepdims=True)

        # Expand summary to match sequence length
        weighted_summary = tf.tile(weighted_summary, [1, tf.shape(inputs)[1], 1])

        # Step 5: Combine attention output with weighted summary
        combined_output = tf.concat([attention_output, weighted_summary], axis=-1)  # Combine features

        # Step 6: Apply output projection and dropout
        combined_output = self.output_dense(combined_output)
        combined_output = self.dropout(combined_output, training=training)

        # Step 7: Ensure input dimensions match before adding
        # Apply Dense layer to match dimensions of 'inputs' and 'combined_output'
        inputs_projected = self.query_dense(inputs)  # Project 'inputs' to match the output dimension of combined_output

        # Step 8: Add residual connection and layer normalization
        return self.layer_norm(inputs_projected + combined_output)

    def get_config(self):
        config = super().get_config()
        config.update({
            'd_model': self.d_model,
            'dropout_rate': self.dropout_rate,
            'use_weighted_summary': self.use_weighted_summary,
        })
        return config




class KernelizedMultiheadSelfAttentionLayer(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads, dropout_rate=0.1, use_weighted_summary=False, eps=1e-6, **kwargs):
        super(KernelizedMultiheadSelfAttentionLayer, self).__init__(**kwargs)
        self.d_model = d_model
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate
        self.use_weighted_summary = use_weighted_summary
        self.eps = eps

        # Ensure d_model is divisible by the number of heads
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        self.depth = d_model // num_heads

    def build(self, input_shape):
        # Query, Key, and Value projection layers for multi-head attention
        self.query_dense = Dense(self.d_model)
        self.key_dense = Dense(self.d_model)
        self.value_dense = Dense(self.d_model)

        # Output projection layer
        self.output_dense = Dense(self.d_model)

        # Dropout layer
        self.dropout = Dropout(self.dropout_rate)

        # Optional weighted summary
        if self.use_weighted_summary:
            self.summary_weights = Dense(1, activation="softmax")

        # Layer normalization
        self.layer_norm = LayerNormalization(epsilon=self.eps)

        super(KernelizedMultiheadSelfAttentionLayer, self).build(input_shape)

    def split_heads(self, x, batch_size):
        """
        Split the last dimension into (num_heads, depth) and transpose for parallel processing.
        """
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])  # Shape: (batch_size, num_heads, seq_len, depth)

    def call(self, inputs, training=False):
        batch_size = tf.shape(inputs)[0]

        # Project inputs to query, key, and value spaces
        queries = self.query_dense(inputs)  # Shape: (batch_size, seq_len, d_model)
        keys = self.key_dense(inputs)
        values = self.value_dense(inputs)

        # Split into multiple heads
        queries = self.split_heads(queries, batch_size)  # Shape: (batch_size, num_heads, seq_len, depth)
        keys = self.split_heads(keys, batch_size)
        values = self.split_heads(values, batch_size)

        # Apply kernel trick for linear attention (e.g., positive activation)
        queries = tf.nn.elu(queries) + 1
        keys = tf.nn.elu(keys) + 1

        # Compute linear attention using kernelized queries and keys
        key_sum = tf.reduce_sum(keys, axis=2, keepdims=True)  # Shape: (batch_size, num_heads, 1, depth)
        scores = tf.einsum("bhqd,bhkd->bhqk", queries, keys) / (key_sum + self.eps)  # Shape: (batch_size, num_heads, seq_len, seq_len)

        # Compute weighted sum of values
        attention_output = tf.einsum("bhqk,bhvd->bhqd", scores, values)  # Shape: (batch_size, num_heads, seq_len, depth)

        # Merge heads back
        attention_output = tf.transpose(attention_output, perm=[0, 2, 1, 3])  # Shape: (batch_size, seq_len, num_heads, depth)
        attention_output = tf.reshape(attention_output, (batch_size, -1, self.d_model))  # Shape: (batch_size, seq_len, d_model)

        # Optionally extract a weighted summary
        if self.use_weighted_summary:
            weights = self.summary_weights(attention_output)  # Shape: (batch_size, seq_len, 1)
            weighted_summary = tf.reduce_sum(attention_output * weights, axis=1, keepdims=True)
        else:
            weighted_summary = tf.reduce_mean(attention_output, axis=1, keepdims=True)

        # Expand summary to match sequence length
        weighted_summary = tf.tile(weighted_summary, [1, tf.shape(inputs)[1], 1])  # Shape: (batch_size, seq_len, d_model)

        # Combine attention output with weighted summary
        combined_output = tf.concat([attention_output, weighted_summary], axis=-1)  # Shape: (batch_size, seq_len, 2 * d_model)

        # Apply output projection and dropout
        combined_output = self.output_dense(combined_output)
        combined_output = self.dropout(combined_output, training=training)

        # Residual connection and layer normalization
        inputs_projected = self.query_dense(inputs)  # Project inputs to match combined_output
        return self.layer_norm(inputs_projected + combined_output)

    def get_config(self):
        config = super().get_config()
        config.update({
            "d_model": self.d_model,
            "num_heads": self.num_heads,
            "dropout_rate": self.dropout_rate,
            "use_weighted_summary": self.use_weighted_summary,
            "eps": self.eps,
        })
        return config




class PositionalEncodingLayer(tf.keras.layers.Layer):
    def __init__(self, max_position, d_model, **kwargs):
        super(PositionalEncodingLayer, self).__init__(**kwargs)
        self.max_position = max_position
        self.d_model = d_model
        self.pos_encoding = self.positional_encoding(max_position, d_model)
        
    def get_angles(self, pos, i, d_model):
        angle_rates = 1 / np.power(10000, (2 * (i // 2)) / np.float32(d_model))
        return pos * angle_rates

    def positional_encoding(self, max_position, d_model):
        angle_rads = self.get_angles(np.arange(max_position)[:, np.newaxis],
                                     np.arange(d_model)[np.newaxis, :],
                                     d_model)

        angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
        angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])

        pos_encoding = angle_rads[np.newaxis, ...]

        return tf.cast(pos_encoding, dtype=tf.float32)

    def call(self, inputs):
        seq_len = tf.shape(inputs)[1]
        return inputs + self.pos_encoding[:, :seq_len, :]

    def get_config(self):
        config = super().get_config().copy()
        config.update({
            'max_position': self.max_position,
            'd_model': self.d_model
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(config['max_position'], config['d_model'])




class DynamicSelfModelingReservoirCallback(tf.keras.callbacks.Callback):
    def __init__(self, reservoir_layer, performance_metric='accuracy', target_metric=0.95,
                 growth_rate=10, prune_rate=0.05, performance_threshold=0.01, 
                 growth_phase_length=10, pruning_phase_length=5):
        super().__init__()
        self.reservoir_layer = reservoir_layer
        self.performance_metric = performance_metric
        self.target_metric = target_metric
        self.growth_rate = growth_rate
        self.prune_rate = prune_rate
        self.performance_threshold = performance_threshold
        self.growth_phase_length = growth_phase_length
        self.pruning_phase_length = pruning_phase_length
        self.performance_history = []
        self.previous_loss = float('inf')

    def on_epoch_end(self, epoch, logs=None):
        current_metric = logs.get(self.performance_metric, 0)
        self.performance_history.append(current_metric)

        # Calculate the rate of change in performance over the last 5 epochs
        if len(self.performance_history) > 5:
            improvement_rate = (current_metric - self.performance_history[-5]) / 5
        else:
            improvement_rate = 0

        # If performance improvement is below the threshold, trigger growth
        if improvement_rate > self.performance_threshold:
            self.reservoir_layer.add_neurons(self.growth_rate)
            print(f"Growing reservoir by {self.growth_rate} neurons.")

        # Trigger pruning if needed based on the prune rate
        if improvement_rate < self.performance_threshold:
            self.reservoir_layer.prune_connections(self.prune_rate)
            print(f"Pruned connections by {self.prune_rate * 100}%.")
        
        # If the current metric has reached the target, allow for reservoir growth or pruning
        if current_metric >= self.target_metric:
            print(f" - Performance metric {self.performance_metric} reached target {self.target_metric}.")
            if improvement_rate > self.performance_threshold:
                self.reservoir_layer.add_neurons(self.growth_rate)
            elif improvement_rate < self.performance_threshold:
                self.reservoir_layer.prune_connections(self.prune_rate)

        # Optionally print or log the training progress
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: {self.performance_metric} = {current_metric}")

    def reset(self):
        """Resets the monitoring mechanism for a new training session."""
        self.previous_loss = float('inf')

    def get_config(self):
        """Returns the configuration of the callback."""
        config = {
            'reservoir_layer': self.reservoir_layer,
            'performance_metric': self.performance_metric,
            'target_metric': self.target_metric,
            'growth_rate': self.growth_rate,
            'prune_rate': self.prune_rate,
            'performance_threshold': self.performance_threshold,
            'growth_phase_length': self.growth_phase_length,
            'pruning_phase_length': self.pruning_phase_length
        }
        return config
