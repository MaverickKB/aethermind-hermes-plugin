# Privacy

AetherMind stores live beside project source. Treat them as local project data.
Do not write secrets, credentials, private operator paths, customer data, raw
prompts, private transcripts, or high-volume logs into `.aem` layers.

The package includes privacy checks for common accidents:

- private-looking absolute paths
- secret/token/password assignments
- bearer tokens
- `sk-...` style API keys

Literal examples should be marked clearly as examples, for example:

```text
literal example: /Users/example/project
```

Privacy checks are a guardrail, not a guarantee. Keep layers compact and avoid
copying raw files, chat transcripts, or logs into continuity records.
