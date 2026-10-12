#!/bin/bash
# Cleanup script for Module 07 - LDAP Authentication
# Restores OAuth to htpasswd only, removes LDAP resources
# NOTE: Caller must be logged in as admin before running this script

echo "Cleaning up LDAP resources..."

# Verify we're logged in as admin
if ! oc whoami | grep -q admin; then
  echo "ERROR: Not logged in as admin — run 'oc login -u admin' first"
  exit 1
fi

# Restore OAuth to htpasswd only
cat <<'EOF' | oc apply -f -
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  identityProviders:
  - name: htpasswd
    mappingMethod: claim
    type: HTPasswd
    htpasswd:
      fileData:
        name: htpasswd
EOF

# Remove LDAP secrets and config
oc delete secret ldap-secret -n openshift-config --ignore-not-found
oc delete configmap ca-config-map -n openshift-config --ignore-not-found

# Remove LDAP users, identities, and groups
# NOTE: identities are named explicitly here (not `--all`) so htpasswd:admin
# is never touched — deleting it leaves the admin User object pointing at a
# nonexistent Identity, which breaks OAuth login for admin until the Identity
# is recreated.
oc delete user normaluser1 fancyuser1 fancyuser2 teamuser1 teamuser2 --ignore-not-found
oc delete identity ldap:normaluser1 ldap:fancyuser1 ldap:fancyuser2 ldap:teamuser1 ldap:teamuser2 --ignore-not-found
oc delete group ose-fancy-dev ose-normal-dev ose-teamed-app ose-user --ignore-not-found

# Remove RBAC bindings
oc adm policy remove-cluster-role-from-user cluster-admin fancyuser1 2>/dev/null || true
oc adm policy remove-cluster-role-from-group cluster-reader ose-fancy-dev 2>/dev/null || true

# Wait for the OAuth rollout to finish *before* tearing down glauth, so the
# old LDAP-configured oauth-openshift pods are gone before their backend
# disappears. Deleting glauth first (the old order) left a window where
# still-running old pods tried to reach an already-deleted LDAP server,
# which looked like a frozen console during that window.
(
  oc rollout status deployment/oauth-openshift -n openshift-authentication --timeout=120s
  oc delete project app-dev app-test app-prod glauth --ignore-not-found
) &>/dev/null &

echo "Cleanup running in background — OAuth restoring to htpasswd only. You can continue to the next module."
