# OpenShift Ops Day Roadshow

## Overview

The OpenShift Ops Day Roadshow is a modular, hands-on lab that gives cluster administrators direct experience operating Red Hat OpenShift Container Platform in a production-representative environment. Participants work through a curated selection of 17 selectable modules covering installation verification, application lifecycle management, networking, identity, observability, security, and advanced topics such as virtualization, multi-cluster management, and AI-assisted operations. Operators choose which modules to include via catalog parameters, enabling the lab to be scoped to a half-day session or expanded to a full day.

## Target Audience

- **Role:** Cluster administrators, platform engineers, infrastructure architects
- **Experience level:** Intermediate
- **What they already know:** `oc`/`kubectl` CLI usage, Linux command-line comfort, conceptual understanding of containers and Kubernetes (pods, nodes, namespaces, secrets, operators)
- **What they don't know:** Operational depth across the full OpenShift feature surface — networking internals, GitOps workflows, identity federation, observability stacks, advanced security posture management, virtualization, and AI-assisted cluster operations

## Prerequisites

- Active `oc` session with cluster-admin privileges (provided by the lab environment)
- Familiarity with OpenShift web console navigation
- Basic Linux CLI comfort (grep, curl, vi/nano)

## Learning Objectives

1. Verify cluster health by inspecting ClusterOperators, MachineConfigPools, cluster version, and etcd metrics after installation
2. Deploy, expose, scale, and roll back applications using OpenShift workload management primitives including PodDisruptionBudgets and health probes
3. Configure HAProxy IngressControllers, Routes, and TLS termination including HSTS and rate limiting
4. Implement network segmentation using OVN-Kubernetes NetworkPolicy, AdminNetworkPolicy, EgressFirewall, and EgressIP
5. Troubleshoot common workload failures including ImagePullBackOff, CrashLoopBackOff, LimitRange violations, ConfigMap mismatches, and SCC errors
6. Deploy and manage GitOps workflows with ArgoCD including drift detection and self-healing application sync
7. Configure LDAP and OIDC identity providers with automated group synchronization and RBAC on OpenShift
8. Monitor cluster and application health using Prometheus, Alertmanager, Loki, and distributed tracing with Tempo and OpenTelemetry
9. Scale workloads automatically using Vertical Pod Autoscaler recommendations and Horizontal Pod Autoscaler under load
10. Provision, live-migrate, clone, and snapshot virtual machines using OpenShift Virtualization
11. Secure the cluster using RHACS vulnerability scanning, compliance scans against CIS/PCI-DSS/STIG benchmarks, and runtime Policy-as-Code
12. Manage secrets centrally with HashiCorp Vault and External Secrets Operator, and establish mTLS workload identity using Zero-Trust Workload Identity Manager

## Content Type

Lab (hands-on)

## Products & Technologies

- Red Hat OpenShift Container Platform 4.20
- Red Hat OpenShift GitOps (ArgoCD)
- Red Hat OpenShift Virtualization
- Red Hat Advanced Cluster Management (RHACM)
- Red Hat Advanced Cluster Security (RHACS)
- Red Hat build of Keycloak (RHBK)
- Red Hat Developer Hub (RHDH)
- OpenShift Lightspeed
- Red Hat OpenShift Data Foundation (ODF) — NooBaa (S3) and Ceph RBD
- OpenShift Logging (Loki Operator, Cluster Logging Operator, Vector)
- Red Hat build of OpenTelemetry
- Tempo Operator
- Vertical Pod Autoscaler (VPA)
- OpenShift Compliance Operator
- Zero-Trust Workload Identity Manager (ZTWIM)
- HashiCorp Vault
- External Secrets Operator (ESO)

## Module Map

| Module | Title | Duration |
|--------|-------|----------|
| Setup (always shown) | Setup & Overview | 15–20 min |
| 01 | Installation & Verification | 10 min |
| 02 | Application Management | 15–20 min |
| 03 | Ingress & Load Balancing | 25 min |
| 04 | Network Security | 10–15 min |
| 05 | Debugging & Troubleshooting | 10–15 min |
| 06 | GitOps | 10–15 min |
| 07 | Identity - LDAP | 15–20 min |
| 08 | Identity - OIDC | 15–20 min |
| 09 | Observability & Logging | 35–40 min |
| 10 | Performance Tuning | 15–20 min |
| 11 | Virtualization | 20–25 min |
| 12 | Developer Hub | 25–30 min |
| 13 | Lightspeed | 15–20 min |
| 14 | ACM Multi-Cluster Management | 30 min |
| 15 | Advanced Cluster Security | 15–20 min |
| 16 | Secrets Management | 25 min |
| 17 | Zero-Trust Workload Identity Manager | 20 min |
| Conclusion (always shown) | Wrap Up | ~5 min |

The lab is modular — operators select a subset of modules 01–17 via catalog parameters (`module_enable_*`). A typical delivery covers 6–10 modules.

## Difficulty Level

Intermediate

## Environment

**Learner view:** Participants access a dedicated OpenShift cluster via the Showroom interface. The cluster starts in a near-production state: monitoring stack (Prometheus, Alertmanager, Thanos), OVN-Kubernetes networking, ODF storage (Ceph RBD + NooBaa S3), OpenShift Virtualization, RHACM, RHACS, RHDH, and OpenShift Lightspeed are pre-installed and pre-configured. A JumpCloud LDAP service and an Azure OpenAI GPT-4 endpoint (pre-configured Secret) are available from the start. Students install RHBK, Loki, Cluster Logging, OpenTelemetry, Tempo, VPA, HashiCorp Vault (via Helm), and External Secrets Operator during their selected modules.

**Automation needed:** Yes — environment setup automation provisions and configures the pre-installed operators, seeds demo applications, and injects per-student credentials and endpoints.

## Infrastructure Requirements

- **Platform:** OCP
- **Cluster type:** 3-node compact multinode — control-plane nodes carry workloads (dual-role); worker MachineSet scaled to 0 at start
- **OCP version:** 4.20
- **Topology:** Per-student (one cluster per participant)
- **Cloud provider:** CNV (bare metal + OpenShift Virtualization)
- **Storage:** ODF — Ceph RBD (block) and NooBaa S3 (object)
- **AI/MaaS:** Azure OpenAI GPT-5 (frontier) — pre-provisioned endpoint and Secret for OpenShift Lightspeed (module 13)
- **External services:** registry.redhat.io, registry.access.redhat.com, registry.connect.redhat.com, quay.io, github.com (support scripts and demo apps), ldap.jumpcloud.com:636 (LDAP IDP for module 07)
- **Non-GA products:** None (all products are GA as of OCP 4.20)
- **GPU nodes:** None
- **Automation approach:** Ansible
- **Sizing (control plane):** 3 nodes, 16 vCPU, 64GB RAM each (dual-role control-plane + worker)

## Assessment Strategy

This is a classic Showroom lab with trust-based assessment. There are no automated solve/validate playbooks — participants complete exercises by following the lab guide and verify their own work using the OpenShift web console and `oc` CLI. Instructors may use the Wrap Up section's discussion questions for informal assessment.
