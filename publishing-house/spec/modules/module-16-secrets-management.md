# Module 16 — Secrets Management

## Brief Overview

This module covers centralized secrets management on OpenShift using HashiCorp Vault and External Secrets Operator. Participants install Vault via Helm, initialize and unseal the Vault instance, write secrets into the KV secrets engine, configure the Vault Agent Injector to deliver secrets as files into application pods via sidecar injection, then install External Secrets Operator and create an ExternalSecret object that syncs a Vault secret into a native Kubernetes Secret.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers, security engineers
- **Prerequisites:** Cluster-admin access; Helm CLI available; basic understanding of Kubernetes Secrets and environment variable injection
- **Duration:** 25 minutes

## Learning Objectives

1. Install HashiCorp Vault on OpenShift using Helm and initialize the Vault cluster
2. Write secrets into the Vault KV secrets engine
3. Configure Vault Kubernetes auth method using a ServiceAccount token
4. Configure the Vault Agent Injector and annotate a deployment to inject secrets as files
5. Install External Secrets Operator and create a SecretStore pointing to Vault
6. Create an ExternalSecret that syncs a Vault path into a native Kubernetes Secret

## Lab Structure

| Section | Time |
|---------|------|
| Install Vault via Helm and initialize | 5 min |
| Write secrets to Vault KV engine | 3 min |
| Configure Vault Kubernetes auth method | 4 min |
| Configure Vault Agent Injector sidecar | 5 min |
| Install External Secrets Operator | 3 min |
| Create SecretStore and ExternalSecret | 5 min |

## Key Takeaways

- HashiCorp Vault provides a centralized, auditable secrets store with fine-grained access policies
- The Vault Agent Injector delivers secrets as files mounted in `/vault/secrets/` — applications read files, not environment variables
- File-based secret delivery avoids secrets appearing in `oc describe pod` environment variable output
- External Secrets Operator bridges Vault and native Kubernetes Secrets, enabling applications that already use Kubernetes Secrets to benefit from Vault without code changes
- ESO automatically resyncs ExternalSecret objects when the Vault source changes

## Infrastructure Notes

- Helm CLI is available in the Showroom terminal
- Vault is installed in a dedicated namespace via the official HashiCorp Helm chart
- No pre-existing Vault instance — participants install and initialize from scratch
- External Secrets Operator is installed from OperatorHub during this module
