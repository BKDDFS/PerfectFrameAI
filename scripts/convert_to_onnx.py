#!/usr/bin/env python3
"""
One-time script to convert TensorFlow weights to ONNX format.

Usage with Docker:
    cd scripts
    docker build -f Dockerfile.convert -t nima-convert .
    docker run --rm -v $(pwd):/convert nima-convert

After conversion, upload the weights to HuggingFace:
    huggingface-cli upload BKDDFS/nima_weights weights.onnx
"""

import tensorflow as tf
import tf2onnx
import onnx

print("Building model architecture...")
base_model = tf.keras.applications.InceptionResNetV2(
    input_shape=(224, 224, 3), include_top=False, pooling="avg", weights=None
)
x = tf.keras.layers.Dropout(0.75)(base_model.output)
output = tf.keras.layers.Dense(10, activation="softmax")(x)
model = tf.keras.Model(inputs=base_model.input, outputs=output)

print("Loading weights.h5...")
model.load_weights("weights.h5")

print("Converting to ONNX (opset 17)...")
input_signature = [tf.TensorSpec([None, 224, 224, 3], tf.float32, name="input")]
onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature, opset=17)

onnx.save(onnx_model, "weights.onnx")
print("Saved weights.onnx")
