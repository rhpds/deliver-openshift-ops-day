# Module 15 — Advanced Cluster Security

## Brief Overview

This module covers cluster and workload security posture management using Red Hat Advanced Cluster Security (RHACS). Participants run a vulnerability scan against a running deployment to identify CVEs, execute compliance scans against CIS Kubernetes benchmark, PCI-DSS, and STIG profiles, and create a SecurityPolicy that enforces Policy-as-Code at runtime — specifically killing any pod that executes `apk` (Alpine package manager), demonstrating how RHACS enforces security controls at the process execution level.

## Audience and Time

- **Personas:** Cluster administrators, security engineers, compliance officers
- **Prerequisites:** Cluster-admin access; RHACS pre-installed and sensor deployed to the cluster; basic understanding of CVE severity levels and compliance frameworks
- **Duration:** 15–20 minutes

## Learning Objectives

1. Run a vulnerability scan against a running deployment and identify critical CVEs
2. Execute compliance scans against CIS Kubernetes, PCI-DSS, and STIG benchmark profiles
3. Review compliance scan results and identify failing controls
4. Create a SecurityPolicy that kills pods running the `apk` command at runtime
5. Trigger the policy by running `apk` in a container and verify RHACS terminates the pod

## Lab Structure

| Section | Time |
|---------|------|
| Run vulnerability scan and review CVE report | 4 min |
| Execute CIS Kubernetes compliance scan | 3 min |
| Execute PCI-DSS and STIG compliance scans | 3 min |
| Create apk-kill SecurityPolicy | 3 min |
| Trigger policy and verify pod termination | 4 min |

## Key Takeaways

- RHACS vulnerability scanning covers base image CVEs and application-level packages — not just container image layers
- Compliance scans run against live cluster state — results reflect the actual runtime configuration, not just manifests
- Policy-as-Code moves security enforcement from audit to prevention — violations are stopped before they cause harm
- The apk-block policy demonstrates process-level enforcement — RHACS monitors syscalls, not just API requests
- RHACS integrates with image registries and CI/CD pipelines for shift-left security scanning

## Infrastructure Notes

- RHACS Central and SecuredCluster (sensor) are pre-installed
- The RHACS UI is accessible via a Route in the `stackrox` namespace
- An intentionally vulnerable demo application is pre-deployed for scanning exercises
