# Module 06 — GitOps

## Brief Overview

This module introduces GitOps-driven application delivery using Red Hat OpenShift GitOps (ArgoCD). Participants create an ArgoCD Application CR that points to a Git repository, observe the initial sync that deploys the application, then introduce configuration drift by directly editing a Kubernetes resource. They observe ArgoCD detecting the drift and watch the self-healing reconciliation restore the desired state from Git.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers, DevOps engineers
- **Prerequisites:** Cluster-admin access; basic understanding of Git and declarative configuration; ArgoCD pre-installed via OpenShift GitOps operator
- **Duration:** 10–15 minutes

## Learning Objectives

1. Create an ArgoCD Application CR targeting a Git repository and a specific path
2. Observe the initial application sync and verify resources are created in the target namespace
3. Introduce configuration drift by manually editing a Kubernetes resource out-of-band
4. Verify ArgoCD detects the drift and marks the application as OutOfSync
5. Trigger or observe automatic self-healing as ArgoCD reconciles the cluster to Git state

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Inspect pre-installed ArgoCD instance | 2 min |
| 2 | Create ArgoCD Application CR | 3 min |
| 3 | Observe initial sync | 2 min |
| 4 | Introduce drift by editing a live resource | 2 min |
| 5 | Observe drift detection and self-healing | 3 min |

## Key Takeaways

- ArgoCD continuously compares the live cluster state against the declared Git state
- The Application CR is the primary unit of GitOps management — each app has one source and one destination
- Manual edits to managed resources are automatically reverted when self-heal is enabled
- GitOps provides a full audit trail — every change is a Git commit with author, timestamp, and diff
- The ArgoCD UI shows application health, sync status, and the resource tree at a glance

## Infrastructure Notes

- Red Hat OpenShift GitOps operator is pre-installed in the `openshift-gitops` namespace
- The lab uses a public GitHub repository for the application manifests
- External access to github.com is required
