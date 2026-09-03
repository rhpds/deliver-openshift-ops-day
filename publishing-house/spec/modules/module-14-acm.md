# Module 14 — ACM Multi-Cluster Management

## Brief Overview

This module covers multi-cluster fleet management using Red Hat Advanced Cluster Management (RHACM). Participants use RHACM to create a Hosted Control Plane (HCP) cluster, manage Fleet Virtualization resources across the fleet, deploy a multi-cluster application using an ArgoCD ApplicationSet, and enforce a GDPR compliance policy across the managed cluster fleet using RHACM Policy objects.

## Audience and Time

- **Personas:** Cluster administrators, platform architects, multi-cluster operations teams
- **Prerequisites:** Cluster-admin access; RHACM pre-installed and configured as the hub; conceptual understanding of multi-cluster architectures
- **Duration:** 30 minutes

## Learning Objectives

1. Create a Hosted Control Plane cluster using RHACM's HyperShift integration
2. Manage Fleet Virtualization resources via RHACM across the fleet
3. Deploy a multi-cluster application using an ArgoCD ApplicationSet targeting multiple managed clusters
4. Create an RHACM Policy to enforce a GDPR compliance requirement across the fleet
5. Verify policy compliance status and observe remediation behavior

## Lab Structure

| Section | Time |
|---------|------|
| Create Hosted Control Plane cluster | 8 min |
| Inspect Fleet Virtualization management | 5 min |
| Deploy application via ArgoCD ApplicationSet | 7 min |
| Create GDPR compliance Policy | 5 min |
| Verify policy compliance status | 5 min |

## Key Takeaways

- Hosted Control Planes decouple the OCP control plane from worker nodes, enabling lightweight cluster provisioning at scale
- RHACM provides a single pane of glass for fleet observability, policy, and application delivery across many clusters
- ArgoCD ApplicationSets enable GitOps-driven multi-cluster deployments from a single manifest
- RHACM Policies can enforce configuration, security posture, and compliance requirements across the entire fleet
- Policy status rolls up to the hub — non-compliant clusters are surfaced automatically

## Infrastructure Notes

- RHACM hub operator is pre-installed on the participant's cluster
- Hosted Control Plane creation requires the HyperShift operator and CNV infrastructure — both pre-configured
- Fleet Virtualization requires OpenShift Virtualization on managed clusters
- External access to github.com is required for ApplicationSet source repositories
