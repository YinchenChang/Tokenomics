# Tokenomics

An interactive calculator for estimating **AI inference throughput and revenue** for large-scale AI data centers, built with [Streamlit](https://streamlit.io).

## Overview

This tool models the full computation chain for LLM inference — from GPU-level latency through inter-rack networking to DC-wide annual revenue:

**Config → WP_Param → TL_Param → DC_Cost_Model → Revenue_Model**

Given a hardware configuration and model spec, it calculates:

- **WP_Param**: Per-layer FLOP counts, HBM traffic, and NVLink communication for both prefill and decode phases. Includes optimizations like FlashAttention to minimize memory bandwidth bottlenecks.
- **TL_Param**: End-to-end latency timeline (tokenization → embedding → prefill → decode → detokenization) with GQA, batching, NVLink SHARP optimizations, and inter-rack network overhead.
- **DC_Cost_Model**: Full CapEx breakdown (IT hardware, facility, electrical, cooling, fiber/security, soft costs) and annual OpEx (depreciation, electricity, maintenance & operations).
- **Revenue Model**: Token throughput, pricing tiers, and total estimated annual revenue across all rack configurations, with Rev/OpEx ratio and cost-per-Mtoken.

## Features & Supported Hardware

### Dynamic Rack Specifications
Customize your data center layout with dynamic rack parameters in the sidebar:
- Define arbitrary GPUs/Rack, Rack Power, Peak FLOPS, and NVLink Bandwidth.
- Built-in presets for **GB200 NVL72** and **Vera Rubin NVL72**.

### Inter-Rack Network Modeling
Model the impact of DC-scale networking on inference throughput:
- **Network fabric presets**: InfiniBand XDR (Quantum-X800), Spectrum-X800, Standard Ethernet
- **Configurable parameters**: NIC bandwidth per GPU, switch latency, network hops, oversubscription ratio, SHARP v4 in-network reduction
- **Disaggregated prefill-decode**: Toggle to model KV cache transfer overhead when prefill and decode run on separate rack groups
- **Multi-rack Tensor Parallelism**: Automatically detects when a model exceeds single-rack GPU memory and computes cross-rack activation transfer overhead
- **Stress test comparison**: 6 network scenarios (IB XDR, Ethernet, disaggregated, high oversubscription, combined worst-case) with throughput loss and revenue impact

### Model Auto-Scaling
Architecture parameters (d_model, n_layers, n_heads) auto-scale from total parameter count using an aspect-ratio method, supporting models from 8B to 10T+ without manual tuning.

### Advanced Physics & Optimizations
The calculator incorporates Deep Dive explanations for cutting-edge techniques:
- **FlashAttention** Memory bandwidth optimization context
- PagedAttention & Continuous Batching
- Speculative Decoding & KV Cache Quantization
- Asynchronous Compute/Communication Overlap

## Key Inputs

| Category | Parameters |
|---|---|
| Data Center | Total power (GW), PUE, rack spec customization |
| Model | Parameters (auto-scales architecture), vocab size, precision (FP4/FP8/FP16) |
| Tokens | Input tokens, output tokens |
| Optimization | GQA KV heads, batch size, speculative decoding, NVLink SHARP, TP/PP |
| Inter-Rack Network | Fabric type, NIC BW, switch latency, hops, oversubscription, SHARP v4, disaggregated mode, comm overlap |
| Revenue | Pricing tiers (auto-selected by model size), GPU utilization rate, uptime |

## Getting Started

### Run locally

For Windows users, we provide a convenient batch script:
```cmd
run_local.bat
```

Alternatively, run manually via:
```bash
pip install -r requirements.txt
streamlit run tokenomics.py
```

### Deploy

Deploy via [Streamlit Community Cloud](https://share.streamlit.io) by connecting this repository.

## Requirements

- Python 3.9+
- streamlit
- pandas
- openpyxl
