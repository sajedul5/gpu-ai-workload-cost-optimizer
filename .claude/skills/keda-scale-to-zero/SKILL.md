---
name: keda-scale-to-zero
description: Configure KEDA ScaledObjects or ScaledJobs so GPU workers scale to zero when idle and scale up from SQS queue depth or a Prometheus metric. Use when adding a new GPU worker, tuning cold starts, or reviewing KEDA manifests.
---

# KEDA scale to zero

Write manifests to `k8s/keda/`, named `scaledobject-<name>.yaml` or `scaledjob-<name>.yaml`.

## Choose the resource

- **ScaledObject** for long-running workers that pull from a queue (inference services, batch consumers).
- **ScaledJob** for one-job-per-message work (training runs, offline batch). Each Job runs to completion, so Karpenter can remove the node as soon as it finishes.

## Steps

1. Identify the trigger: `aws-sqs-queue` (preferred for job queues) or `prometheus` (for request-rate driven services).
2. Set `minReplicaCount: 0`. If the service has a latency SLO that a cold start breaks, set `1` and write the reason in a comment.
3. Pick `queueLength` = messages one replica clears in about one minute.
4. Set `cooldownPeriod` (default 300s). Shorter saves more GPU time; longer avoids thrashing on bursty queues.
5. Cap `maxReplicaCount` so `max × GPUs per pod` fits under the NodePool's `limits."nvidia.com/gpu"`.
6. Authenticate with `TriggerAuthentication` using EKS Pod Identity or IRSA. Never put keys in the manifest.
7. Validate with `kubeconform -strict -ignore-missing-schemas k8s/keda/`.

## Template

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: inference-worker
spec:
  scaleTargetRef:
    name: inference-worker
  minReplicaCount: 0
  maxReplicaCount: 8
  cooldownPeriod: 300
  triggers:
    - type: aws-sqs-queue
      metadata:
        queueURL: https://sqs.us-east-1.amazonaws.com/123456789012/inference-jobs
        queueLength: "5"
        awsRegion: us-east-1
      authenticationRef:
        name: keda-aws
```

## Cold-start budget

Total time from first message to first result is roughly: node launch (Karpenter) + image pull + model load.
Record each part in the PR. Cut it with smaller images, a pre-pulled AMI, or model weights on a fast volume before reaching for warm replicas.
