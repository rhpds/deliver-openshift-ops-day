# Module 13 — Lightspeed

## Brief Overview

This module introduces OpenShift Lightspeed as an AI-assisted operations tool. Participants configure OLSConfig to connect to the pre-provisioned Azure OpenAI GPT-4 endpoint, use natural language prompts in the OpenShift web console to generate Kubernetes YAML manifests, and use the MCP (Model Context Protocol) cluster introspection capability to ask questions about cluster state and troubleshoot a deliberately broken pod by conversing with the AI assistant.

## Audience and Time

- **Personas:** Cluster administrators, platform engineers new to AI-assisted operations
- **Prerequisites:** Cluster-admin access; OpenShift Lightspeed operator pre-installed; Azure OpenAI Secret pre-configured in the cluster
- **Duration:** 15–20 minutes

## Learning Objectives

1. Configure OLSConfig to use the pre-provisioned Azure OpenAI GPT-4 endpoint
2. Use natural language prompts in the OpenShift web console to generate a Kubernetes manifest
3. Apply a generated manifest and verify the resulting resource
4. Use MCP cluster introspection to query live cluster state via natural language
5. Troubleshoot a broken pod by conversing with Lightspeed and applying the suggested fix

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | Inspect OLSConfig and verify Azure OpenAI connection | 3 min |
| 2 | Generate Kubernetes YAML from natural language prompt | 4 min |
| 3 | Apply generated manifest and verify | 3 min |
| 4 | MCP cluster introspection queries | 4 min |
| 5 | Troubleshoot broken pod via Lightspeed conversation | 4 min |

## Key Takeaways

- Lightspeed integrates with the OpenShift web console — no separate AI tool or browser extension is needed
- OLSConfig references the Azure OpenAI endpoint and API key via a Kubernetes Secret — credentials never enter the YAML
- Natural language manifest generation reduces YAML authoring friction while still requiring operator review before apply
- MCP cluster introspection allows the AI to inspect live cluster state — it reads from the API server, not from training data
- Lightspeed responses include citations to OpenShift documentation when available

## Infrastructure Notes

- OpenShift Lightspeed operator is pre-installed in the `openshift-lightspeed` namespace
- Azure OpenAI GPT-4 endpoint and API key Secret are pre-provisioned by environment setup automation
- External network access to the Azure OpenAI API endpoint is required
- No GPU nodes are required — inference runs remotely on Azure
