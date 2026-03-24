# Tokenomics

An interactive calculator for estimating **AI inference throughput and revenue** for large-scale AI data centers, built with [Streamlit](https://streamlit.io).

## Overview

This tool models the full computation chain for LLM inference:

**Config → WP_Param → TL_Param → Revenue_Model**

Given a hardware configuration and model spec, it calculates:

- **WP_Param**: Per-layer FLOP counts, HBM traffic, and NVLink communication for both prefill and decode phases. Includes optimizations like FlashAttention to minimize memory bandwidth bottlenecks.
- **TL_Param**: End-to-end latency timeline (tokenization → embedding → prefill → decode → detokenization) with GQA, batching, and NVLink SHARP optimizations.
- **Revenue Model**: Expandable section detailing token throughput, pricing tiers, and total estimated annual revenue across all rack configurations.

## Features & Supported Hardware

### Dynamic Rack Specifications
Customize your data center layout with dynamic rack parameters in the sidebar:
- Define arbitrary GPUs/Rack, Rack Power, Peak FLOPS, and NVLink Bandwidth.
- Built-in presets for **GB200 NVL72** and **Vera Rubin NVL72**.

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
| Model | Parameters, vocab size, layers, heads, precision (FP4/FP8/FP16) |
| Tokens | Input tokens, output tokens |
| Optimization | GQA KV heads, batch size, speculative decoding, NVLink SHARP, TP/PP |
| Revenue | Pricing models, GPU utilization rate, uptime |

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
