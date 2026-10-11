---
name: architecture-diagram
description: Update and re-render the AWS architecture diagram (docs/images/architecture.png) from its Python source using the mingrammer diagrams library with official AWS icons. Use when the architecture changes or the README diagram needs editing.
---

# Architecture diagram

The PNG is generated. Edit `docs/diagrams/architecture.py`, never the image.

## Render

```bash
brew install graphviz                       # once
python3 -m venv .venv && .venv/bin/pip install diagrams   # once
.venv/bin/python docs/diagrams/architecture.py
```

Output: `docs/images/architecture.png`.

## Conventions

- Use AWS icons from `diagrams.aws.*` for AWS services. KEDA and Karpenter have no official icon; they use the Kubernetes `HPA` and `CCM` icons with a clear label.
- Clusters: AWS Region → Amazon EKS cluster → logical groups (Autoscaling, GPU workloads, node pools, Observability).
- Edge colours: amber `#C4720A` for the scaling signal, teal `#1F6F68` for the Spot path, dashed for fallback and async flows.
- Keep labels to two short lines.
- After rendering, open the PNG and check that no labels overlap before committing.
