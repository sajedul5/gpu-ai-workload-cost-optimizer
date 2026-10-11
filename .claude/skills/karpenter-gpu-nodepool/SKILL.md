---
name: karpenter-gpu-nodepool
description: Create or review a Karpenter v1 NodePool and EC2NodeClass for GPU workloads on EKS (Spot-first with On-Demand fallback, right-sized instance families, GPU taints, consolidation, GPU limits). Use when adding GPU capacity, changing instance families, or reviewing Karpenter manifests.
---

# Karpenter GPU NodePool

Write manifests to `k8s/karpenter/`, one resource per file (`nodepool-<name>.yaml`, `ec2nodeclass-<name>.yaml`).

## Steps

1. Ask which workload class this pool serves: **inference** (small/medium models, latency-sensitive) or **training** (long, multi-GPU).
2. Pick instance families from the table. Do not add others without a written reason.

   | Workload | Families | Capacity types |
   |---|---|---|
   | Inference, ≤24 GB model | `g5`, `g6` | spot, on-demand |
   | Inference, ≤48 GB model | `g6e` | spot, on-demand |
   | Training, multi-GPU | `p4d`, `p5` | on-demand (spot only with checkpointing) |

3. Start from the template below. Keep these invariants:
   - `apiVersion: karpenter.sh/v1`
   - capacity-type requirement lists both `spot` and `on-demand` for inference pools (Karpenter prefers the cheaper Spot offering)
   - taint `nvidia.com/gpu: NoSchedule`
   - `limits."nvidia.com/gpu"` is set, so a runaway queue cannot buy unlimited GPUs
   - `disruption.consolidationPolicy: WhenEmptyOrUnderutilized` for inference; `WhenEmpty` for training so running jobs are not moved
   - `expireAfter` set (default `720h`) so AMIs roll
4. Make sure Spot interruption handling is on: Karpenter `settings.interruptionQueue` points at the SQS queue fed by EventBridge.
5. Validate: `kubeconform -strict -ignore-missing-schemas k8s/karpenter/`.

## Template

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: gpu-inference
spec:
  template:
    metadata:
      labels:
        workload-class: inference
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: ["g5", "g6", "g6e"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: gpu
      taints:
        - key: nvidia.com/gpu
          effect: NoSchedule
      expireAfter: 720h
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 5m
  limits:
    nvidia.com/gpu: 16
```

## Review checklist

- [ ] No hard-coded account IDs, subnets or security group IDs (use tag selectors in the EC2NodeClass)
- [ ] GPU limit is set and matches the team's budget
- [ ] Training pools do not consolidate running nodes
- [ ] Workloads that use this pool tolerate the taint and request `nvidia.com/gpu`
