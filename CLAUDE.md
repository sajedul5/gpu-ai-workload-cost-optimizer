# CLAUDE.md

Project memory for Claude Code. Loaded automatically at the start of every session.
Keep it short and factual; long procedures live in `.claude/skills/`.

## What this project is

Reference platform for cutting GPU and AI workload costs on AWS:
Spot and right-sized GPU nodes, scale-to-zero with Karpenter and KEDA on EKS,
and cost-per-job dashboards in Prometheus and Grafana. Public, client-facing repo.

## Repo map

- `docs/diagrams/architecture.py` – source of `docs/images/architecture.png` (mingrammer `diagrams`)
- `docs/images/` – rendered images used by README.md
- `.claude/` – shared Claude Code config: settings, hooks, skills
- Planned (not yet created): `terraform/`, `k8s/karpenter/`, `k8s/keda/`, `k8s/monitoring/`, `dashboards/`, `examples/`

## Commands

- Render diagram: `python3 -m venv .venv && .venv/bin/pip install diagrams pillow && .venv/bin/python docs/diagrams/architecture.py` (needs `brew install graphviz`)
- Validate manifests: `kubeconform -strict -ignore-missing-schemas k8s/`
- Terraform checks: `terraform fmt -recursive && terraform validate && terraform plan`. Applying changes is done by a human only.

## Conventions

- Karpenter API is `karpenter.sh/v1`; GPU NodePools allow `spot` and `on-demand` and set `limits."nvidia.com/gpu"`.
- Every GPU NodePool taints `nvidia.com/gpu:NoSchedule`; workloads tolerate it explicitly.
- KEDA ScaledObjects set `minReplicaCount: 0` unless a documented latency SLO needs warm replicas.
- Instance families: inference `g5`/`g6`/`g6e`, large training `p4d`/`p5`. Justify anything else in the PR.
- Cost metrics are named `*_usd` and are per hour unless the name says otherwise.
- YAML: 2-space indent, one resource per file, file named `<kind>-<name>.yaml`.

## Rules for public content

- This repo is public. Never commit account IDs, ARNs, cluster endpoints, client names or real cost data.
  Use `123456789012` and `us-east-1` in examples.
- Never state savings as fact without a measured baseline. Use "up to" only when quoting an AWS figure, with a link.

## Safety

- Never change real infrastructure: no Terraform state changes, `kubectl delete`, `helm uninstall`, or AWS delete/terminate calls.
  Hooks in `.claude/hooks/` block the common ones; do not work around them. Give the user the command instead.
- Do not read `.env`, `*.pem`, kubeconfigs or `~/.aws/`.
