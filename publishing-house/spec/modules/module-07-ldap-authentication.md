# Module 07 — Identity - LDAP

## Brief Overview

This module walks through configuring JumpCloud as an external LDAP identity provider on OpenShift. Participants create an OAuth identity provider object pointing to the JumpCloud LDAP service, verify login with an LDAP-backed user account, set up periodic group synchronization using an LDAP group sync CronJob, and bind RBAC roles to the synced groups. The result is a fully integrated external directory driving cluster access control.

## Audience and Time

- **Personas:** Cluster administrators, identity and access management engineers
- **Prerequisites:** Cluster-admin access; basic understanding of LDAP directory structure (DN, OU, CN, bind credentials)
- **Duration:** 15–20 minutes

## Learning Objectives

1. Configure an LDAP identity provider in the OpenShift OAuth cluster operator
2. Verify external LDAP user authentication via the OpenShift login flow
3. Create an LDAP group sync configuration and run a manual sync
4. Deploy a group sync CronJob for periodic automated synchronization
5. Bind an OpenShift RBAC role to a synced LDAP group

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Configure LDAP IDP in OAuth cluster operator | 4 min |
| 2 | Verify LDAP user login | 2 min |
| 3 | Create group sync configuration | 4 min |
| 4 | Run manual group sync | 2 min |
| 5 | Deploy periodic CronJob for group sync | 3 min |
| 6 | Bind RBAC role to synced group | 3 min |

## Key Takeaways

- OpenShift supports multiple identity providers simultaneously — LDAP can coexist with htpasswd or OIDC
- Bind credentials (service account DN + password) are stored in an OpenShift Secret and referenced by the IDP
- Group sync does not happen automatically — a CronJob or external trigger is required
- Synced groups appear as OpenShift Group objects and can be used directly in RoleBinding and ClusterRoleBinding
- User accounts from LDAP are created in OpenShift on first login — they do not need to be pre-created

## Infrastructure Notes

- JumpCloud LDAP service endpoint: `ldaps://ldap.jumpcloud.com:636`
- TLS certificate for JumpCloud's CA is required for the IDP configuration
- JumpCloud LDAP credentials are pre-provisioned and injected as environment variables in Showroom
