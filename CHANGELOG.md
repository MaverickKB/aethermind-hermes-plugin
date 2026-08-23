# Change log

## 0.2.0

### Continuity methods

- Updated the bundled continuity engine to the public Light v1 runtime.
- Added artifact-reference, anchor, pressure-event, supersession, and rollback
  primitive fields to `aethermind_write_layer`.
- Added currentness, scoped brief, anchor brief, capability, event, archive,
  audit, and plan-check methods.
- Added `events.aem` and `archive.aem` support.
- Added `since_ts`, `last_n`, and multi-marker read filters.

### Compatibility

- Preserved all ten 0.1 tool names.
- Preserved the existing lifecycle hooks and companion-skill registration.
- Kept 0.1 AEM records readable without a store rewrite.
- Kept imports validation-first and preserved existing layer bytes as the
  prefix when `allow_existing=true`.
- Replaced each imported AEM file through a same-directory atomic write after
  complete validation of the combined layer stream.
- Exposed the legacy `next` and remote-work metadata fields through
  `aethermind_write_layer`.

### Documentation

- Updated the Hermes operation guide and method inventory.
- Added a 0.1 to 0.2 preservation, verification, and rollback path.
- Updated the AEM format reference.
