# Privacy

AetherMind stores live beside project source. Treat them as project data and keep
them small.

Do not write credentials, customer data, raw prompts, transcripts, private
operator paths, or high-volume logs into `.aem` layers.

The plugin checks for common accidents:

- private-looking absolute paths
- credential-style assignments
- bearer-style tokens
- `sk-...` style keys

Literal path examples should be marked clearly:

```text
literal example: /Users/example/project
```

Privacy checks are guardrails, not guarantees. Keep layers compact and avoid
copying raw files or logs into continuity records.
