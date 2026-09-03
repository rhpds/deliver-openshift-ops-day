# Module 12 — Developer Hub

## Brief Overview

This module explores Red Hat Developer Hub (RHDH) from an operations perspective. Participants browse the Software Catalog to discover services and inspect live Kubernetes health data surfaced by the Kubernetes plugin, use a Software Template to scaffold a new component via RHDH's Backstage scaffolder, work through an ops troubleshooting ticket in the RHDH workflow interface, and view Prometheus metrics for a running service rendered directly in the RHDH catalog page.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers, developer experience leads
- **Prerequisites:** Cluster-admin access; RHDH pre-installed and configured; basic familiarity with the concept of an internal developer platform
- **Duration:** 25–30 minutes

## Learning Objectives

1. Browse the RHDH Software Catalog and identify services and their ownership metadata
2. Inspect live Kubernetes resource health data (pods, deployments, services) surfaced by the Kubernetes plugin
3. Use a Software Template to scaffold a new component and verify the generated repository and ArgoCD application
4. Work through an ops troubleshooting ticket in the RHDH workflow interface
5. View Prometheus metrics for a running service rendered in the RHDH catalog entity page

## Lab Structure

| Section | Time |
|---------|------|
| Browse Software Catalog and inspect entity metadata | 5 min |
| Inspect live Kubernetes data via Kubernetes plugin | 5 min |
| Use Software Template to scaffold a component | 8 min |
| Work through ops troubleshooting ticket | 7 min |
| View Prometheus metrics in catalog page | 5 min |

## Key Takeaways

- RHDH centralizes service discovery, ownership, and live operational data in a single pane of glass
- The Kubernetes plugin pulls live cluster state directly from the API server — no additional agents required
- Software Templates encode opinionated paths-to-production that developers follow without requiring platform expertise
- Ops troubleshooting tickets in RHDH create a structured workflow that guides responders through diagnosis steps
- Prometheus metrics can be embedded in catalog entity pages using the Prometheus plugin — no separate dashboard tool required

## Infrastructure Notes

- RHDH operator is pre-installed and RHDH is pre-configured with the Kubernetes and Prometheus plugins
- A demo application is pre-deployed in a namespace visible to RHDH
- Software Templates reference a GitHub organization for output repository creation — external access to github.com required
