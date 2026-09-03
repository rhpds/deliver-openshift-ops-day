# Module 01 — Installation & Verification

## Brief Overview

This module covers post-installation health validation for an OpenShift 4.20 cluster. Participants use `oc` commands to inspect ClusterOperators, cluster version, MachineConfigPools, networking components, storage classes, and etcd metrics. The goal is to build a repeatable verification workflow that confirms the cluster is ready to accept production workloads. No configuration changes are made — this is a read-only inspection exercise.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers
- **Prerequisites:** Active oc session with cluster-admin privileges; basic oc/kubectl familiarity
- **Duration:** 10 minutes

## Learning Objectives

1. Verify all ClusterOperators are in Available=True, Degraded=False state
2. Inspect the cluster version and update channel
3. Confirm MachineConfigPools have converged
4. Verify OVN-Kubernetes network plugin is active and node networking is healthy
5. Confirm storage classes and ODF components are ready
6. Check etcd health metrics and member status

## Lab Structure

| Section | Time |
|---------|------|
| Inspect ClusterOperators | 2 min |
| Check cluster version and update channel | 1 min |
| Verify MachineConfigPools | 2 min |
| Validate networking (OVN-Kubernetes) | 2 min |
| Confirm storage classes and ODF | 2 min |
| Check etcd health | 1 min |

## Key Takeaways

- A healthy cluster shows all ClusterOperators as Available and non-Degraded
- MachineConfigPool convergence confirms node configuration is consistent
- OVN-Kubernetes status can be verified via network operator and node annotations
- ODF health is visible through the storage operator and NooBaa system status
- etcd member count and leader election status are critical first-day checks

## Infrastructure Notes

- Cluster: 3-node compact multinode (dual-role control-plane/worker)
- OCP version: 4.20
- ODF pre-installed with Ceph RBD and NooBaa S3
- No worker nodes — all workloads run on control-plane nodes
