# Module 02 — Application Management

## Brief Overview

This module walks through the full application lifecycle on OpenShift: deploying a workload from a container image, exposing it internally via a Service and externally via a Route, scaling replicas and observing self-healing, configuring liveness and readiness probes, setting up PodDisruptionBudgets for high-availability, and performing a rollback to a previous deployment revision. Participants use both the `oc` CLI and the OpenShift web console.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers, application operators
- **Prerequisites:** Cluster-admin access; familiarity with Kubernetes Deployment and Service concepts
- **Duration:** 15–20 minutes

## Learning Objectives

1. Deploy an application from a container image using `oc new-app` and a Deployment manifest
2. Expose the application with a Service and an edge-terminated Route
3. Scale the Deployment and observe pod scheduling and self-healing behavior
4. Configure liveness and readiness probes to control traffic routing
5. Create a PodDisruptionBudget to enforce minimum replica availability
6. Roll back to a previous deployment revision using `oc rollout undo`

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Deploy application and inspect pods | 3 min |
| 2 | Expose via Service and Route | 2 min |
| 3 | Scale replicas and observe self-healing | 3 min |
| 4 | Add liveness and readiness probes | 3 min |
| 5 | Create PodDisruptionBudget | 3 min |
| 6 | Trigger and perform rollback | 3 min |

## Key Takeaways

- OpenShift Routes provide external access without additional load balancer configuration
- Kubernetes self-healing restarts failed pods automatically within seconds
- Liveness probes distinguish between unresponsive pods and probes that haven't passed yet
- PodDisruptionBudgets protect availability during voluntary disruptions such as node drains
- `oc rollout undo` gives operators a fast recovery path after a bad deployment
