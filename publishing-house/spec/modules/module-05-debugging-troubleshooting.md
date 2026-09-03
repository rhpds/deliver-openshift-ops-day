# Module 05 — Debugging & Troubleshooting

## Brief Overview

This module presents six intentionally broken microservices that participants must diagnose and fix using standard OpenShift and Kubernetes debugging techniques. Each broken service represents a distinct failure mode commonly encountered in production: image pull failures, crash-looping containers, resource quota violations, missing configuration, selector mismatches, and Security Context Constraint rejections. Participants work through each scenario using `oc describe`, `oc logs`, and `oc get events`.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers, on-call site reliability engineers
- **Prerequisites:** Cluster-admin access; basic oc/kubectl familiarity; understanding of pod lifecycle
- **Duration:** 10–15 minutes

## Learning Objectives

1. Diagnose and resolve an ImagePullBackOff caused by an invalid image reference or missing pull secret
2. Debug a CrashLoopBackOff by inspecting container logs and exit codes
3. Identify and resolve a LimitRange quota violation preventing pod scheduling
4. Fix a missing or incorrectly mounted ConfigMap key causing application startup failure
5. Correct a Service selector mismatch that breaks pod-to-service connectivity
6. Diagnose and resolve an SCC violation preventing a pod from running with elevated privileges

## Lab Structure

| Section | Time |
|---------|------|
| Scenario 1: ImagePullBackOff | 2 min |
| Scenario 2: CrashLoopBackOff | 2 min |
| Scenario 3: LimitRange violation | 2 min |
| Scenario 4: ConfigMap key missing | 2 min |
| Scenario 5: Service selector mismatch | 2 min |
| Scenario 6: SCC violation | 3 min |

## Key Takeaways

- `oc describe pod` and `oc get events` are the first-line debugging commands for any pod that won't start
- Container logs from a crashed pod are still accessible via `oc logs --previous`
- LimitRange objects cap resource requests/limits at the namespace level — check them when pods are Pending
- ConfigMap key errors surface as `Error` or `CreateContainerConfigError` in pod events
- Service selectors must match pod labels exactly — a single typo silently breaks connectivity
- SCC violations appear in pod events as `unable to validate against any security context constraint`
