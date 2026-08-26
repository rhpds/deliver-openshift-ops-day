# Module Outline: Zero Trust Workload Identity Manager

## Brief Overview

This module provides a hands-on walkthrough of Red Hat OpenShift Zero Trust Workload Identity Manager (ZTWIM). Participants deploy and configure ZTWIM to enable passwordless service authentication between workloads, building presenter confidence with the concepts, commands, and workflows needed to deliver this content to customers.

## Audience and Time

- **Target personas:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Prerequisites for this module:** Familiarity with `oc`/`kubectl` CLI and OpenShift web console; understanding of Kubernetes secrets and service accounts
- **Estimated duration:** 30 minutes

## Learning Objectives

- Deliver a module on Zero Trust Workload Identity Manager for passwordless service authentication

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1       | ZTWIM Concepts and Architecture | 5 min |
| 2       | Deploying and Configuring ZTWIM | 10 min |
| 3       | Passwordless Service Authentication | 15 min |

## Detailed Steps

### ZTWIM Concepts and Architecture

1. Review the zero trust model and why passwordless workload identity matters.
2. Understand the ZTWIM architecture and how it integrates with OpenShift.

### Deploying and Configuring ZTWIM

3. Deploy ZTWIM on the OpenShift cluster.
4. Configure workload identity policies for the sample application's services.

### Passwordless Service Authentication

5. Demonstrate service-to-service authentication without static credentials.
6. Verify that workloads authenticate using ZTWIM-issued identities.
7. Examine the identity lifecycle: issuance, rotation, and revocation.
8. Review audit and observability of authentication events.

## Key Takeaways

- ZTWIM eliminates the need for static secrets in service-to-service communication.
- Workload identities are automatically issued, rotated, and revoked, reducing the attack surface.
- ZTWIM integrates natively with OpenShift, building on existing service account and RBAC mechanisms.
- Presenters should emphasize the security and operational benefits of moving to passwordless workload authentication.

## Infrastructure Notes

- Requires an OpenShift cluster with ZTWIM prerequisites in place.
- Sample application services must be deployed for demonstrating service-to-service authentication.
- Cluster credentials are provided through Showroom environment attributes.
