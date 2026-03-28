# FTGP Tokenomics — AI Data Center Economics Model

## Project Overview
Streamlit app that models the full token generation pipeline for AI data centers, from GPU-level inference latency through to DC-wide annual revenue. Originally prototyped in Excel (`20260325_Tokenomics_DC_Claude.xlsx`), now maintained directly in Python.

**Computation chain:** Config → WP_Param → TL_Param → DC_Cost_Model → Revenue_Model

## Architecture

### Files
- `tokenomics.py` — Main Streamlit app (~900 lines). All computation + display in one file.
- `flowchart.html` — Animated HTML/JS flowchart template (injected via `string.Template`)
- `test_tokenomics.py` — Tests
- `data/` — Historical Excel reference files

### Key Data Flow
1. **Config** (sidebar): Rack type, model params, tokens, precision, optimization toggles, inter-rack network
2. **WP_Param**: Prefill/decode FLOP, HBM traffic, NVLink comm, GQA, batching, speculative decode
3. **TL_Param**: 6-step E2E latency timeline (tokenize → embed → prefill → decode1 → decodeN → detokenize)
4. **DC_Cost_Model**: CapEx (IT HW, facility, electrical, cooling) + OpEx (depreciation, electricity, maintenance)
5. **Revenue_Model**: Annual throughput × token pricing → revenue, Rev/OpEx ratio

### Rack Presets
- **Vera Rubin NVL72**: Next-gen (Rubin GPU, 72/rack, 260 TB/s NVLink, 20.7 TB HBM, 190 kW)
- **GB200 NVL72**: Current-gen (B200, 72/rack, 130 TB/s NVLink, 13.5 TB HBM, 139 kW)
- **Customized Rack**: User-editable

### Model Auto-Scaling (aspect ratio method)
For "Customized Model" and "1.5T (Generic)", architecture is auto-scaled from parameters:
- `n_layers = round((P / (12 * r^2))^(1/3))` where r=160 (aspect ratio)
- `d_model = round(r * n_layers / d_head) * d_head` where d_head=128
- `n_heads = d_model / d_head`
- Named presets (Llama, Mistral) use known architecture values instead

## Recent Changes (2026-03-26)

### Inter-Rack Network Expansion
Added full inter-rack network modeling based on `20260325_Tokenomics_DC_Claude.xlsx`:

**New sidebar section — "Inter-Rack Network":**
- Network fabric selector (InfiniBand XDR / Spectrum-X800 / Std Ethernet)
- NIC BW per GPU, switch latency, hops, oversubscription, SHARP v4
- Disaggregated prefill-decode toggle
- Inter-rack comm overlap

**Inter-rack overhead added to E2E latency (3 steps):**
- Step 2 (Embedding): routing latency = one-way network latency
- Step 3 (Prefill): KV cache transfer (disaggregated) + cross-rack TP activation transfer (large models)
- Step 5 (Decode-All): token streaming + cross-rack TP decode overhead

**Multi-rack Tensor Parallelism:**
When model memory > single rack GPU memory, computes racks needed for TP and adds cross-rack activation transfer overhead. Formula: `racks_for_tp = ceil(total_mem_needed / gpu_mem_per_rack)`

**Stress test table:** 6 scenarios (Current IB XDR, Std Ethernet, Disaggregated, 16:1 Oversub, Eth+Disagg, All Worst-Case) with throughput loss and revenue impact.

### Model Auto-Scaling Fix
Fixed d_model/n_layers/n_heads auto-scaling for large models (e.g., 10T). Previous formula (`2^11 * 10^log10(P/1e11)`) produced oversized d_model causing negative d_ff. Now uses Excel's aspect-ratio method.

### Energy-per-Step Model (2026-03-28)
Added rack-level energy (Joules) breakdown per pipeline step, mirroring the existing latency timeline.

**New rack preset parameters (sidebar):**
- GPU TDP (W), GPU idle power fraction, HBM power/GPU (W), HBM idle fraction, NVLink power/GPU (W), NIC TDP/GPU (W)

**Energy computation per step:**
- Idle baseline: `(GPU_idle_W + HBM_idle_W) × n_gpu × step_time` — always present
- Active compute: `(GPU_TDP - GPU_idle) × n_gpu × compute_time` — Step 3 only
- Active HBM: `(HBM_W - HBM_idle) × n_gpu × hbm_time` — Steps 2-5
- Active NVLink: `NVLink_W × n_gpu × nvlink_time` — Steps 2, 3, 5
- Active NIC: `NIC_TDP × n_gpu × ir_time` — Steps 2, 3, 5

**New TL_Param table columns:** Energy (J) per rack type alongside Duration (s), plus summary rows for Energy/Token (mJ) and Idle Energy %.

## Next Steps
- Potential areas: power curves, cooling efficiency (PUE dynamics), renewable integration, carbon intensity, time-of-use electricity pricing, battery storage

## Dev Notes
- Run: `streamlit run tokenomics.py`
- Project lives on Google Drive, syncs across laptop/desktop
- No git repo currently — files sync via Google Drive
- Build new features directly in Python with Claude (skip Excel prototyping)
