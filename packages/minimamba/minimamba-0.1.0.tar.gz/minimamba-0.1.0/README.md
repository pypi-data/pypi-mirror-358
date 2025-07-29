# MiniMamba: A Minimal PyTorch Implementation of Mamba (Selective State Space Model)

<p align="center">
  <img src="https://img.shields.io/badge/PyTorch-ee4c2c?style=for-the-badge&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge"/>
  <img src="https://img.shields.io/github/stars/Xinguang/MiniMamba?style=for-the-badge"/>
</p>

**MiniMamba** is a clean and minimal PyTorch reimplementation of the [Mamba](https://arxiv.org/abs/2312.00752) architecture — a **Selective State Space Model (S6)** for fast and efficient sequence modeling. This repository is designed for readability, simplicity, and educational use — no custom CUDA kernels, and fully compatible with CPU, CUDA, and Apple Silicon (MPS).

> 📂 Repository: [github.com/Xinguang/MiniMamba](https://github.com/Xinguang/MiniMamba)

---

## ✨ Features

- 🧠 **Pure PyTorch**: Easy to understand and modify; no custom CUDA ops.
- 📦 **Self-contained**: Single-file modules, plug-and-play ready.
- ⚡ **Efficient inference**: Supports autoregressive generation with internal state caching.
- 🧪 **Well-tested**: Includes unit tests with `pytest` for correctness.
- 🔬 **Educational**: Ideal for learning and experimentation.

---

## 🛠️ Installation

```bash
git clone https://github.com/Xinguang/MiniMamba.git
cd MiniMamba
pip install -r requirements.txt
```

> ✅ Requirements:
>
> * Python ≥ 3.8
> * PyTorch ≥ 1.12
> * `pytest` ≥ 7.0 (for running tests)

---

## 🚀 Quick Start

Run the example script to verify the model runs correctly on your hardware:

```bash
python examples/run_mamba_example.py
```

Example output:

```
✅ Using device: MPS (Apple Silicon)
Total model parameters: 26,738,688
Input shape: torch.Size([2, 128])
Output shape: torch.Size([2, 128, 10000])
Inference time: 0.1524 seconds
```

---

## 📚 Usage Example

```python
import torch
from minimamba import Mamba

# 1. Define config
config = {
    'd_model': 512,
    'n_layer': 6,
    'vocab_size': 10000,
    'd_state': 16,
    'd_conv': 4,
    'expand': 2,
}

# 2. Initialize model
model = Mamba(**config)

# 3. Dummy input
input_ids = torch.randint(0, config['vocab_size'], (2, 128))
logits = model(input_ids)
print(logits.shape)  # torch.Size([2, 128, 10000])
```

### 🔁 Autoregressive Inference with Caching

```python
class InferenceCache:
    def __init__(self):
        self.seqlen_offset = 0
        self.key_value_memory_dict = {}

inference_params = InferenceCache()

# Simulate token-by-token generation
input1 = torch.randint(0, config['vocab_size'], (1, 1))
logits1 = model(input1, inference_params=inference_params)
inference_params.seqlen_offset += 1

input2 = torch.randint(0, config['vocab_size'], (1, 1))
logits2 = model(input2, inference_params=inference_params)
```

---

## 🧪 Testing

To run all tests:

```bash
pytest tests/
```

Includes:

* ✅ Model construction test
* ✅ Output shape verification
* ✅ Empty input handling

---

## 📂 Project Structure

```
MiniMamba/
├── minimamba/              # Core model components
│   ├── model.py            # Mamba model class
│   ├── block.py            # MambaBlock with residuals
│   ├── s6.py               # Selective State Space layer
│   ├── norm.py             # RMSNorm module
│   └── __init__.py
│
├── examples/
│   └── run_mamba_example.py
│
├── tests/
│   └── test_mamba.py       # Unit tests
│
├── requirements.txt
├── setup.py
├── README.md
├── README.zh-CN.md
├── README.ja.md
└── LICENSE
```

---

## 🧠 About the Mamba Model

Mamba is a **state-space model** that supports long-sequence modeling with **linear time complexity**, unlike traditional transformers.

This implementation includes:

* ✅ `S6`: Selective state-space scan layer
* ✅ `MambaBlock`: Pre-norm + residual structure
* ✅ `Mamba`: Full model with token embedding and output head

It uses mathematically correct parallel scan logic and supports autoregressive inference with internal cache for fast generation.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## 🙏 Acknowledgments

This project is inspired by:

* **Paper**: [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752)
  by Albert Gu & Tri Dao
* **Reference Implementation**: [state-spaces/mamba](https://github.com/state-spaces/mamba)

Thanks to the original authors for their brilliant work.

---

## 🌐 Other Languages

* [简体中文文档](./README.zh-CN.md)
* [日本語ドキュメント](./README.ja.md)
