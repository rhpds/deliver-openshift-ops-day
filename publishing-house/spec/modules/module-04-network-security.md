# Module 04 — Network Security

## Brief Overview

This module explores OVN-Kubernetes network security primitives on OpenShift 4.20. Participants create NetworkPolicy objects to isolate namespaces at the pod level, apply AdminNetworkPolicy for cluster-scoped policies that override project-level rules, configure EgressFirewall to restrict outbound traffic from namespaces, assign EgressIPs to namespaces for predictable egress SNAT, and inspect CoreDNS configuration to understand cluster DNS resolution.

## Audience and Time

- **Personas:** Cluster administrators, network security engineers
- **Prerequisites:** Cluster-admin access; conceptual understanding of IP networking, CIDR notation, and DNS
- **Duration:** 10–15 minutes

## Learning Objectives

1. Create NetworkPolicy objects to enforce namespace isolation and allow specific pod-to-pod traffic
2. Apply AdminNetworkPolicy to enforce cluster-wide rules that take precedence over per-project NetworkPolicy
3. Configure EgressFirewall rules to block or allow outbound traffic by CIDR and DNS name
4. Assign an EgressIP to a namespace for consistent outbound source NAT
5. Inspect CoreDNS configuration and verify service DNS resolution within the cluster

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Create namespace isolation NetworkPolicy | 3 min |
| 2 | Apply AdminNetworkPolicy for cluster-wide rules | 3 min |
| 3 | Configure EgressFirewall | 3 min |
| 4 | Assign EgressIP to a namespace | 3 min |
| 5 | Inspect CoreDNS and verify DNS resolution | 2 min |

## Key Takeaways

- By default OpenShift namespaces are not isolated — NetworkPolicy must be applied explicitly
- AdminNetworkPolicy (cluster-scoped) overrides project-level NetworkPolicy, enabling centralized enforcement
- EgressFirewall restricts outbound connections from a namespace without requiring per-pod proxy configuration
- EgressIP ensures that all outbound traffic from a namespace appears to come from a known, stable IP — useful for allowlisting in external firewalls
- CoreDNS provides `<service>.<namespace>.svc.cluster.local` resolution automatically for all Services

## Infrastructure Notes

- OVN-Kubernetes is the network plugin — SDN-based NetworkPolicy objects are not used
- AdminNetworkPolicy requires OVN-Kubernetes and is enabled by default in OCP 4.20
