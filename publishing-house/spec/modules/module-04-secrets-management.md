# Module Outline: Secrets Management with Vault and External Secrets Operator

## Brief Overview

This module provides a hands-on walkthrough of secrets management using Hashicorp Vault and the External Secrets Operator (ESO). Participants configure Vault as an external secret store, deploy ESO to sync secrets into OpenShift, and verify the workflow end-to-end — building presenter confidence with the tools and patterns needed to deliver this content to customers.

## Audience and Time

- **Target personas:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Prerequisites for this module:** Familiarity with `oc`/`kubectl` CLI and OpenShift web console; understanding of Kubernetes secrets
- **Estimated duration:** 30 minutes

## Learning Objectives

- Deliver a module on secrets management with Hashicorp Vault and External Secrets Operator

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1       | Vault Setup and Secret Storage | 10 min |
| 2       | External Secrets Operator Configuration | 10 min |
| 3       | End-to-End Secret Sync and Verification | 10 min |

## Detailed Steps

### Vault Setup and Secret Storage

1. Access the Hashicorp Vault instance and review its configuration.
2. Store a secret in Vault using the CLI or UI.
3. Configure a Vault policy and authentication method for OpenShift workloads.

### External Secrets Operator Configuration

4. Review the ESO deployment on the OpenShift cluster.
5. Create a SecretStore resource pointing to the Vault instance.
6. Create an ExternalSecret resource that references a Vault secret.

### End-to-End Secret Sync and Verification

7. Verify that ESO syncs the Vault secret into an OpenShift Secret.
8. Deploy a sample application that consumes the synced secret.
9. Update the secret in Vault and observe the sync propagation.
10. Review the audit trail and error handling for failed syncs.

## Key Takeaways

- External secrets management with Vault centralizes secret storage outside the cluster, improving security posture.
- ESO automates the sync between Vault and OpenShift Secrets, eliminating manual secret management.
- The SecretStore and ExternalSecret pattern provides a declarative, auditable approach to secrets.
- Presenters should emphasize the operational benefits: centralized rotation, access policies, and audit trails.

## Infrastructure Notes

- Requires an OpenShift cluster with Hashicorp Vault and External Secrets Operator ready to deploy.
- Vault must be accessible from the cluster with appropriate authentication configured.
- Cluster credentials are provided through Showroom environment attributes.
