# Module 11 — Virtualization

## Brief Overview

This module demonstrates OpenShift Virtualization for running virtual machines alongside containerized workloads on the same cluster. Participants create a RHEL 9 virtual machine from a bootable volume, access it via the web console's VNC console, perform a live migration between cluster nodes without VM downtime, clone the VM to produce an identical copy, and create and restore a VM snapshot.

## Audience and Time

- **Personas:** Cluster administrators, infrastructure architects, virtualization administrators migrating from traditional hypervisors
- **Prerequisites:** Cluster-admin access; OpenShift Virtualization operator pre-installed; ODF storage pre-installed for VM disk persistence
- **Duration:** 20–25 minutes

## Learning Objectives

1. Create a RHEL 9 virtual machine using OpenShift Virtualization from a bootable volume
2. Access the virtual machine console via the OpenShift web console VNC interface
3. Perform a live migration of the VM to a different cluster node without downtime
4. Clone the virtual machine to produce an independent copy
5. Create a VM snapshot and restore the VM from that snapshot

## Lab Structure

| Section | Time |
|---------|------|
| Create RHEL 9 VM from bootable volume | 5 min |
| Access VM via web console VNC | 3 min |
| Perform live migration | 5 min |
| Clone the VM | 5 min |
| Create snapshot and restore | 5 min |

## Key Takeaways

- OpenShift Virtualization uses KubeVirt to run VMs as pods, enabling unified scheduling and networking alongside containers
- Live migration moves running VMs between nodes without power-cycling — requires shared storage (ODF RWX)
- VM clones produce independent copies with separate disk volumes; clones do not share storage with the source
- Snapshots capture VM state at a point in time and can be used for rollback or test environment creation
- The VNC console in the OpenShift web console provides direct VM access without SSH or bastion hosts

## Infrastructure Notes

- OpenShift Virtualization operator is pre-installed
- ODF Ceph RBD provides RWX persistent volumes for VM disk images
- The cluster runs on CNV (bare metal + OpenShift Virtualization) — hardware virtualization extensions are available
- Live migration requires at least two schedulable nodes — the compact cluster satisfies this with three dual-role nodes
