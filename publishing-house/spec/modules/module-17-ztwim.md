# Module 17 — Zero-Trust Workload Identity Manager

## Brief Overview

This module introduces Zero-Trust Workload Identity Manager (ZTWIM), based on the SPIFFE/SPIRE standard, for passwordless service-to-service authentication on OpenShift. Participants deploy ZTWIM, observe the automatic issuance of X.509 SVIDs (SPIFFE Verifiable Identity Documents) to workload pods, configure mTLS between a web service and a PostgreSQL database using the SVIDs — replacing the database password with a cryptographic identity — and observe automatic certificate rotation without any manual intervention or Secret updates.

## Audience and Time

- **Personas:** Cluster administrators, security architects, zero-trust implementation engineers
- **Prerequisites:** Cluster-admin access; ZTWIM operator pre-installed; basic understanding of TLS certificates and the concept of workload identity
- **Duration:** 20 minutes

## Learning Objectives

1. Deploy the ZTWIM SPIRE server and verify agent registration on cluster nodes
2. Inspect X.509 SVIDs automatically issued to workload pods
3. Configure mTLS between a web service and PostgreSQL using SVID certificates
4. Verify that the database connection uses certificate authentication instead of password authentication
5. Observe automatic SVID rotation and confirm the service connection remains uninterrupted

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Deploy ZTWIM SPIRE server and verify agents | 4 min |
| 2 | Inspect SVIDs issued to workload pods | 3 min |
| 3 | Configure PostgreSQL to require mTLS client certs | 4 min |
| 4 | Configure web service to use SVID for DB auth | 4 min |
| 5 | Observe automatic SVID rotation | 5 min |

## Key Takeaways

- ZTWIM issues cryptographic identities (SVIDs) to workloads automatically — no Secrets, no passwords, no manual certificate management
- SVIDs are short-lived X.509 certificates that rotate automatically before expiry, eliminating the risk of credential exfiltration
- mTLS with SVIDs provides mutual authentication — both the client and server prove their identity before data flows
- SPIFFE/SPIRE is a CNCF standard — ZTWIM implements this standard on OpenShift with operator-managed lifecycle
- Zero-trust workload identity removes an entire class of secrets (database passwords, API keys for internal services) from the pod spec

## Infrastructure Notes

- ZTWIM operator is pre-installed on the cluster
- SPIRE server requires persistent storage — ODF Ceph RBD is used for the SPIRE data directory
- A PostgreSQL instance and demo web application are pre-deployed for this module
- No external network access is required — all SVID issuance and mTLS is cluster-internal
