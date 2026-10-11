---
name: gpu-cost-per-job
description: Build or explain cost-per-job metrics, PromQL queries, recording rules and Grafana panels that join GPU requests and DCGM utilization with instance prices. Use for cost dashboards, idle-GPU alerts, savings reports, or before/after comparisons against a baseline.
---

# GPU cost per job

## Data sources

| Signal | Metric | Source |
|---|---|---|
| GPUs requested per pod | `kube_pod_container_resource_requests{resource="nvidia_com_gpu"}` | kube-state-metrics |
| GPU utilization | `DCGM_FI_DEV_GPU_UTIL` | NVIDIA DCGM exporter |
| Node capacity type | `kube_node_labels{label_karpenter_sh_capacity_type}` | kube-state-metrics (label allowlist) |
| Price per GPU-hour | `node_price_per_gpu_hour_usd` | project pricing exporter (planned) |

## Core queries

Dollars per hour each pod costs right now:

```promql
sum by (namespace, pod) (
  kube_pod_container_resource_requests{resource="nvidia_com_gpu"}
  * on (node) group_left()
    node_price_per_gpu_hour_usd
)
```

Idle GPU-hours over the last day (billed GPU under 5% busy):

```promql
sum(
  count_over_time((avg by (Hostname, gpu) (DCGM_FI_DEV_GPU_UTIL) < 5)[24h:1m])
) / 60
```

## Rules

- Record expensive joins as recording rules named `job:gpu_cost_usd_per_hour:sum` (level:metric:operation).
- Every dashboard panel states its unit (`$/h`, `$`, `GPU-h`) and time range.
- Savings are reported only as **measured baseline vs measured after**, same workload, same period length. Never estimate savings and present them as results.
- No real client numbers in this repo. Use clearly labelled sample data in examples.

## Report format

For a before/after report, give: period, workload, GPU-hours, cost, cost per job, idle GPU-hours, Spot share — for both baseline and after — then the difference. Note anything that changed besides the optimization (traffic, model version).
