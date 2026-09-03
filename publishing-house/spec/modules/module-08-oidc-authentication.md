# Module 08 — Identity - OIDC

## Brief Overview

This module covers OIDC-based identity federation using the Red Hat build of Keycloak (RHBK) operator. Participants install the Keycloak operator, configure a Keycloak realm with users and groups, register OpenShift as an OIDC client, configure the OpenShift OAuth operator to use the Keycloak IDP, and verify that group membership from OIDC token claims is automatically synced to OpenShift groups on user login — eliminating the need for a separate group sync job.

## Audience and Time

- **Personas:** Cluster administrators, identity and access management engineers
- **Prerequisites:** Cluster-admin access; module 07 (LDAP) is recommended but not required; basic understanding of OAuth2/OIDC flows
- **Duration:** 15–20 minutes

## Learning Objectives

1. Install the Red Hat build of Keycloak operator and create a Keycloak instance
2. Configure a Keycloak realm with users, groups, and an OpenShift OIDC client
3. Configure the OpenShift OAuth operator with an OIDC identity provider pointing to Keycloak
4. Verify OIDC user login and inspect the ID token claims
5. Confirm that OpenShift groups are automatically populated from token claims on login

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Install RHBK operator and create Keycloak instance | 4 min |
| 2 | Configure realm, users, groups, and OIDC client | 4 min |
| 3 | Configure OpenShift OIDC IDP | 3 min |
| 4 | Verify OIDC login | 2 min |
| 5 | Inspect token claims and verify group sync | 4 min |

## Key Takeaways

- OIDC eliminates the need for a periodic group sync CronJob — groups come directly from the ID token
- RHBK provides a full-featured IdP that integrates with upstream LDAP, social login, and enterprise SSO
- The OpenShift OIDC IDP uses the `groups` claim by default for group synchronization
- Client secrets for the OIDC client are stored in an OpenShift Secret referenced by the IDP configuration
- Multiple OIDC IDPs can be configured simultaneously for different user populations

## Infrastructure Notes

- RHBK operator is installed by participants during this module from OperatorHub
- Keycloak instance is created in a dedicated namespace
- A Keycloak Route with TLS is created automatically by the operator
