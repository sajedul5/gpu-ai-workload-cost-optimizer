"""Render the architecture diagram with official AWS icons.

Usage:
    pip install diagrams pillow   # also needs Graphviz: brew install graphviz
    python docs/diagrams/architecture.py

Writes docs/images/architecture.png.
"""

from datetime import date
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2Instance, EC2SpotInstance, ElasticKubernetesService
from diagrams.aws.cost import Budgets, CostAndUsageReport
from diagrams.aws.general import Users
from diagrams.aws.integration import Eventbridge, SimpleQueueServiceSqsQueue
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.compute import Pod
from diagrams.k8s.controlplane import CCM
from diagrams.onprem.monitoring import Grafana, Prometheus
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "images" / "architecture"
OUT.parent.mkdir(parents=True, exist_ok=True)
COPYRIGHT = f"\u00a9 {date.today().year} Sajedul Islam \u00b7 DevOps Engineer"

graph_attr = {
    "fontsize": "22",
    "fontname": "Helvetica-Bold",
    "bgcolor": "white",
    "pad": "0.6",
    "nodesep": "0.7",
    "ranksep": "1.0",
    "splines": "spline",
    "labelloc": "t",
}
node_attr = {"fontsize": "12", "fontname": "Helvetica"}

with Diagram(
    "GPU AI Workload Cost Optimizer on AWS",
    filename=str(OUT),
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    users = Users("Jobs and\ninference requests")
    queue = SimpleQueueServiceSqsQueue("Amazon SQS\njob queue")
    interrupts = Eventbridge("EventBridge\nSpot interruptions")
    cur = CostAndUsageReport("Cost and Usage\nReport")
    budgets = Budgets("AWS Budgets")

    with Cluster("AWS Region", graph_attr={"bgcolor": "#F2F7FF", "fontsize": "14"}):
        with Cluster("Amazon EKS cluster", graph_attr={"bgcolor": "#FFF7EC", "fontsize": "14"}):
            eks = ElasticKubernetesService("EKS\ncontrol plane")

            with Cluster("Autoscaling", graph_attr={"bgcolor": "white"}):
                keda = HPA("KEDA\nscale 0..N pods")
                karpenter = CCM("Karpenter\nlaunch / consolidate")

            with Cluster("GPU workloads", graph_attr={"bgcolor": "white"}):
                workers = Pod("GPU worker pods")

            with Cluster("GPU node pools (Karpenter NodePools)", graph_attr={"bgcolor": "white"}):
                spot = EC2SpotInstance("Spot GPU nodes\ng5 / g6 / g6e")
                ondemand = EC2Instance("On-Demand fallback\np4d / p5")

            with Cluster("Observability", graph_attr={"bgcolor": "white"}):
                prom = Prometheus("Prometheus\n+ DCGM exporter")
                grafana = Grafana("Grafana\ncost per job")

    users >> Edge(label="enqueue") >> queue
    queue >> Edge(label="queue depth", color="#C4720A", style="bold") >> keda
    keda >> Edge(label="replicas") >> workers
    workers >> Edge(label="pending pods") >> karpenter
    karpenter >> Edge(label="prefer Spot", color="#1F6F68", style="bold") >> spot
    karpenter >> Edge(label="fallback", style="dashed") >> ondemand
    interrupts >> Edge(label="drain", style="dashed") >> karpenter
    eks - Edge(style="dotted") - karpenter

    [spot, ondemand] >> Edge(label="GPU metrics", color="#6B7B79") >> prom
    cur >> Edge(label="prices", style="dashed") >> prom
    prom >> grafana
    grafana >> Edge(label="alerts", style="dashed") >> budgets


def add_copyright(png: Path, text: str) -> None:
    """Add a footer strip with the copyright notice to the rendered PNG."""
    img = Image.open(png).convert("RGB")
    strip = max(48, img.height // 28)
    out = Image.new("RGB", (img.width, img.height + strip), "white")
    out.paste(img, (0, 0))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("Helvetica.ttc", strip // 2)
    except OSError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", strip // 2)
        except OSError:
            font = ImageFont.load_default()
    draw.line([(40, img.height), (img.width - 40, img.height)], fill="#D8E0DF", width=2)
    w = draw.textlength(text, font=font)
    draw.text((img.width - w - 40, img.height + strip // 4), text, fill="#566664", font=font)
    out.save(png)


add_copyright(OUT.with_suffix(".png"), COPYRIGHT)
