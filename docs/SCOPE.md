# Scope

The AetherMind Hermes plugin exposes the project-local continuity primitive
through Hermes tools and lifecycle hooks.

## Included

- project-local `layers.aem`, `texture.aem`, `events.aem`, and
  `archive.aem`;
- all six Light v1 primitives and their relationships;
- filtered reads, task reorientation, currentness, briefs, events, and archive
  methods;
- export and import of AEM text;
- Hermes tool, hook, and companion-skill registration;
- compatibility with the 0.1 tool names and AEM records.

## Boundary

The plugin does not replace transcripts, task tracking, general memory, search,
deployment orchestration, or harness policy. It operates only on the project
root supplied by Hermes or by the tool caller.

Integrators own their interface, routing, deployment, and data-sharing choices.
