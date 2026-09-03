# Module 03 — Ingress & Load Balancing

## Brief Overview

This module provides a hands-on deep-dive into OpenShift's HAProxy-based IngressController. Participants inspect the default IngressController, create custom IngressController shards, define Routes with different TLS termination modes (edge, passthrough, re-encrypt), inject HSTS headers for security compliance, and apply rate limiting annotations to protect backend services from traffic spikes.

## Audience and Time

- **Personas:** Cluster administrators, network engineers, platform engineers
- **Prerequisites:** Cluster-admin access; basic understanding of TLS certificates and HTTP routing
- **Duration:** 25 minutes

## Learning Objectives

1. Inspect and describe the default HAProxy IngressController configuration
2. Create a Route with edge TLS termination using a custom certificate
3. Configure passthrough and re-encrypt TLS termination modes
4. Inject HSTS response headers via Route annotations
5. Apply rate limiting to a Route using IngressController annotations
6. Verify traffic routing behavior using curl and the OpenShift web console

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Inspect default IngressController | 3 min |
| 2 | Create edge-TLS Route with custom cert | 5 min |
| 3 | Configure passthrough and re-encrypt Routes | 5 min |
| 4 | Apply HSTS header annotations | 4 min |
| 5 | Configure rate limiting | 5 min |
| 6 | Verify routing and test behavior | 3 min |

## Key Takeaways

- The HAProxy IngressController is the default ingress mechanism in OpenShift and does not require an external load balancer for basic use
- Edge termination decrypts traffic at the router; passthrough sends encrypted traffic directly to the pod
- HSTS enforces HTTPS by instructing browsers to refuse plain-HTTP connections
- Rate limiting at the IngressController level protects backends without requiring changes to application code
- IngressController shards allow different routes to be served by different router replicas

## Infrastructure Notes

- Wildcard DNS is pre-configured for the cluster's apps subdomain
- Default IngressController is pre-installed and serving traffic on port 443
