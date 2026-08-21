# Module Outline: Application Management Hands-On

## Brief Overview

This module provides hands-on practice with the Application Management content from the Roadshow. Participants work through cluster verification, application deployment, and debugging exercises as if they were delivering the module to a customer. The goal is to build familiarity with the specific commands, workflows, and expected outcomes so that presenters can demonstrate and troubleshoot them confidently during a live session.

## Audience and Time

- **Target personas:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Prerequisites for this module:** Basic familiarity with OpenShift CLI (`oc`) and the web console; completion of Modules 1-3
- **Estimated duration:** 30 minutes

## Learning Objectives

- Verify cluster health using CLI commands and the web console
- Deploy a sample application and confirm it is running correctly
- Debug a failing application using logs, events, and pod diagnostics
- Explain each step's purpose and expected outcome as a presenter would during a live walkthrough

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1       | Cluster Verification | 10 min |
| 2       | Application Deployment | 10 min |
| 3       | Debugging a Failing Application | 10 min |

## Detailed Steps

1. Log in to the OpenShift cluster using the CLI with the provided credentials.
2. Verify cluster health: check node status, confirm all cluster operators are available, and review any degraded conditions.
3. Use the web console to confirm the same cluster health information visually.
4. Create a new project for the application deployment exercise.
5. Deploy the pre-configured sample application using the provided manifests.
6. Confirm the application pods are running and the route is accessible.
7. Access the application through its route and verify the expected response.
8. Introduce a fault into the application (using a provided misconfigured manifest or environment variable change).
9. Observe the failing pod status and identify the error using `oc get pods`, `oc describe pod`, and `oc logs`.
10. Review pod events to identify the root cause of the failure.
11. Apply the fix and confirm the application returns to a healthy state.
12. Clean up the project created during the exercise.
13. Answer the checkpoint questions to confirm understanding of cluster verification, deployment, and debugging workflows.

## Key Takeaways

- Cluster verification is the first step in any Roadshow module delivery; presenters should confirm health before starting exercises.
- Application deployment exercises follow a predictable pattern: create project, apply manifests, verify pods and routes.
- Debugging follows a systematic approach: check pod status, read logs, review events, identify root cause, apply fix.
- Presenters should be comfortable narrating each command's purpose and expected output during a live walkthrough.

## Infrastructure Notes

- Requires an OpenShift cluster with a pre-deployed sample application and monitoring stack enabled.
- The sample application must include a mechanism to introduce a controlled fault for the debugging exercise (misconfigured manifest or environment variable).
- Cluster credentials are provided through Showroom environment attributes.
