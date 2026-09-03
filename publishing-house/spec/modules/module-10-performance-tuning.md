# Module 10 — Performance Tuning

## Brief Overview

This module covers automated workload right-sizing and horizontal scaling using the Vertical Pod Autoscaler (VPA) and Horizontal Pod Autoscaler (HPA). Participants apply a VPA object to a running application and inspect its CPU and memory recommendations after a brief observation window. They then configure an HPA targeting CPU utilization, generate synthetic load using a load generator pod, and observe the HPA scale the workload out and then back in as load subsides.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers, capacity planners
- **Prerequisites:** Cluster-admin access; VPA operator pre-installed; basic understanding of CPU/memory resource requests and limits
- **Duration:** 15–20 minutes

## Learning Objectives

1. Install or verify the Vertical Pod Autoscaler operator and create a VPA object for a running Deployment
2. Inspect VPA recommendations for CPU and memory resource requests
3. Configure a Horizontal Pod Autoscaler targeting a CPU utilization threshold
4. Generate load against the application and observe HPA scaling out replicas
5. Observe HPA scale-in behavior after load is removed and the cooldown period elapses

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Install VPA operator (if not pre-installed) | 2 min |
| 2 | Create VPA object and observe recommendations | 5 min |
| 3 | Configure HPA | 3 min |
| 4 | Generate load and observe scale-out | 4 min |
| 5 | Observe scale-in after load subsides | 4 min |

## Key Takeaways

- VPA recommendations improve resource efficiency by right-sizing requests based on actual observed usage
- VPA operates in recommendation-only mode by default — it does not automatically apply changes unless configured
- HPA responds to real-time metrics from the metrics-server and scales within configured min/max bounds
- HPA scale-in is deliberately slower than scale-out to avoid thrashing during intermittent load spikes
- VPA and HPA can coexist when VPA manages memory and HPA manages replica count (do not let both manage CPU)

## Infrastructure Notes

- VPA operator is installed by participants from OperatorHub during this module
- Metrics-server is pre-installed as part of the OpenShift monitoring stack
- Load generator uses a busybox or siege pod — no external tools required
