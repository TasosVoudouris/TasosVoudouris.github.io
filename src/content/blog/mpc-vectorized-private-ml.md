---
title: "Vectorized MPC and Private Machine Learning: Tensors, Fixed Point, Polynomial Activations, and Toy-Model Pitfalls"
description: "Turn scalar sharing into tensor computation, explain secure dot products and fixed-point scaling, and audit why the recovered CNN/ML examples are useful sketches but not end-to-end private-training protocols."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "MPC"
  - "Cryptographic Engineering"
tags:
  - "private-machine-learning"
  - "tensor-mpc"
  - "fixed-point"
  - "secure-dot-product"
  - "polynomial-activation"
  - "cnn"
difficulty: "Advanced"
status: "Research Note"
series: "Secure Multiparty Computation"
seriesOrder: 6
draft: false
---
The recovered archive contains ambitious experiments that jump from scalar secret sharing to neural-network training. The direction is legitimate, but the code mixes normal Keras execution with secure-computation sketches. This chapter keeps the useful engineering ideas and makes the missing cryptographic steps explicit.

## 1. Scalars become tensors

For additive two-party sharing of a tensor $X$:

$$
X=X_0+X_1\pmod q,
$$

where $X_0$ and $X_1$ are matrices/tensors of the same shape.

Addition remains element-wise and local:

$$
[X+Y]_i=X_i+Y_i.
$$

Multiplication by a public tensor is also local.

The interesting operation is a private-private product such as matrix multiplication.

## 2. Matrix Beaver triples

Generalize the scalar triple to matrices:

$$
A,\ B,\ C=AB.
$$

For private matrices $X,Y$, open

$$
E=X-A,
$$

$$
F=Y-B.
$$

Then

$$
XY=C+EB+AF+EF.
$$

The identity is the same as in the scalar case; only the multiplication operation changes.

This is the clean way to reason about secure dense layers and convolutions: identify the bilinear operation and preprocess a compatible correlation.

## 3. Why element-wise tensor multiplication is not a dot product

One recovered `PrivateTensor` prototype generated

```python
c = np.multiply(a, b)
```

then later discussed dot products and convolution.

That triple authenticates/accelerates **Hadamard multiplication**, not matrix multiplication.

For a dense layer we need

$$
C=AB
$$

with matrix multiplication dimensions, not

$$
C=A\odot B.
$$

The operation encoded in the triple must match the circuit gate being evaluated.

## 4. Fixed-point encoding

Neural networks use real-valued weights and activations, while arithmetic MPC works over fields/rings.

Encode

$$
\widetilde x=\lfloor Sx\rceil
$$

for scale $S$.

Then

$$
\widetilde x\widetilde y\approx S^2xy.
$$

A secure truncation/rescaling step is required.

A correct system must track:

- precision loss;
- signed representation;
- modular wraparound;
- range bounds;
- truncation leakage/bias.

## 5. Polynomial activations

Comparison-heavy activations such as ReLU are expensive in arithmetic MPC.

One common educational trick is to approximate a smooth activation by a low-degree polynomial, for example

$$
\sigma(x)\approx c_0+c_1x+c_3x^3+c_5x^5.
$$

This replaces comparisons/transcendentals with additions and multiplications.

But every multiplication consumes preprocessing and adds communication depth, so polynomial degree is a cryptographic performance parameter, not merely an approximation parameter.

## 6. The recovered CNN code is not a secure CNN implementation

The archive combines `PrivateTensor` sketches with ordinary Keras layers such as

```text
Conv2D
Activation
Dropout
Softmax
```

without replacing every internal operation by an MPC protocol.

Therefore it should be read as an **architecture sketch**:

- these are the ML operations we would like to realize;
- some have clear arithmetic-circuit forms;
- others require secure specialized subprotocols or approximations.

Calling `model.fit()` on ordinary tensors does not magically execute the model under secret sharing.

## 7. Dropout and shared randomness

One note suggested using the same fixed NumPy seed across parties to obtain a common dropout mask.

That is not a secure distributed-randomness protocol. It makes the mask predictable and couples security to application-level PRNG state.

If a shared random mask is required, it should come from the MPC preprocessing/randomness mechanism with the intended secrecy/publicity property.

## 8. Softmax and loss functions

Softmax requires exponentiation and division:

$$
\operatorname{softmax}(x_i)=\frac{e^{x_i}}{\sum_j e^{x_j}}.
$$

Those are not native low-cost field operations.

Likewise, cross-entropy and gradient normalization can introduce logarithms, reciprocals, comparisons, or range-management problems.

Private ML frameworks therefore redesign models and numeric representations rather than running an unchanged floating-point framework inside MPC.

## 9. What the experiments are still good for

The recovered code is useful for estimating:

- tensor shapes;
- number of bilinear operations;
- polynomial-activation cost;
- where truncation is needed;
- which layers dominate communication;
- how batching might reduce round overhead.

This makes it a good **protocol cost-model notebook**, not a security-validated training system.

## 10. Takeaway

Private ML is not "take TensorFlow and replace numbers with shares." Every operation must have a secure semantics.

The design loop is:

```text
ML operation
   ↓
arithmetic/Boolean circuit
   ↓
secret-sharing representation
   ↓
secure gate protocol
   ↓
range/precision analysis
   ↓
communication + security audit
```

That is the level at which the old experiments become genuinely useful.
