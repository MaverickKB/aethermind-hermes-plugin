# AEM Light v1 format

AEM Light v1 is the project-local continuity format used by AetherMind 0.2.

## Store layout

```text
<project-root>/.aethermind/
  layers.aem
  texture.aem
  events.aem
  archive.aem
```

`layers.aem` is required for continuity records. The other AEM files are created
when their corresponding methods are used.

## Layer record

Each record is one TOML `[[layer]]` table.

Required fields:

- `id`: string unique within the file;
- `ts`: RFC3339 timestamp with a timezone;
- `author`: writer identifier;
- `type`: lowercase semantic token;
- `body`: compact continuity content;
- `ctx`: context path;
- `conf`: floating-point confidence from 0.0 through 1.0;
- `markers`: array of strings;
- `primitive`: one of the six Light v1 primitives.

Readers treat an absent `primitive` as `layer`. Readers also accept the 0.1
`schema_version = "aem-v1"` field.

Common optional fields:

- `thread_key`;
- `supersedes`, `rollback_of`, and `corrects`;
- `evidence`, `recurrence_of`, `verification`, and `next`;
- `artifact`, `artifact_ref`, `anchor`, and `ref`;
- `prev_hash` and `archived_to`;
- `remote_target`, `local_store_reason`, `source_tool`, and `store_kind`.

Accepted CL2 optional fields include `evidence`, `verification`, `supersedes`,
`rollback_of`, `recurrence_of`, `artifact`, `artifact_ref`, `anchor`, `ref`,
`reason`, `scope`, `severity`, `kind`, `inherit`, `action_rule`, `review_after`,
`domain`, `nutrition`, and `force_reason`.

CL2 boundary capsules are intentionally v1-compatible. Until every configured
reader accepts a raw `boundary` layer type, capsules are encoded as
`type = "load-bearing"` with `kind = "boundary"` and marker `boundary`.

Readers are lenient with legacy or extended stores: omitted `markers` are treated
as `[]`, and non-canonical historical types such as `decision`, `thought`, or
`runtime-validation` are readable. New plugin writes still enforce the canonical
v1 type set unless a CL2 helper explicitly remaps the write into a compatible
shape.

## Primitives

### layer

The base continuity record. All common required fields apply.

### artifact-reference

Requires `ref`. Optional fields include `kind`, `label`, `host`,
`repo_root`, and `content_id`.

### anchor

Requires `anchor` and either `artifact` or `artifact_ref`. Optional fields
include `selector`, `span_hint`, and `inline`.

### pressure-event

Uses `type = "friction"`. Requires `domain`, `symptom`, `evidence`, and
`next_verification`. Optional fields include `suspected_mechanism`, `scope`,
`severity`, `recurrence_of`, `owner_hint`, and `repair`.

### supersession

Requires `supersedes` and `reason`. Optional fields include `scope`,
`replacement`, `artifact`, and `anchor`.

### rollback

Requires `rollback_of` and `reason`. Optional fields include `restored_to`
and `verification`.

## Currentness

Currentness is derived without editing history:

- a newer record listed in `supersedes` makes the referenced record inactive;
- a record listed in `rollback_of` becomes inactive;
- a newer record with the same `thread_key` replaces the prior thread head;
- records without those relationships remain active.

## Append behavior

Writers append complete TOML records. Existing records stay byte-for-byte unchanged.
Numeric IDs are zero-padded and increase from the largest numeric ID already present.
Non-numeric legacy IDs remain valid and reserved.

## Texture entries

New texture entries use a compact, append-only text form:

```text
YYYY-MM-DD [author | context]
<optional semantic marker><body>
---
```

Existing free-form `texture.aem` content remains readable and is not rewritten.

## Event records

Each `events.aem` record is one `[[event]]` TOML table with `id`, `ts`,
`author`, `ctx`, `type`, and `body`. Events hold routine observations and are
excluded from currentness and default briefs.

## Archive records

`archive.aem` begins with a continuation header and contains copied `[[layer]]`
records. Archiving does not remove or edit the original records in
`layers.aem`. After the copies are durable, the writer appends a correction
record to `layers.aem` that supersedes the archived IDs and references the
archive file.

## 0.1 compatibility

A 0.1 store can be read directly. Its UUID IDs, `schema_version`, `next`,
remote-work metadata, and other defined optional fields remain valid. New 0.2
records may coexist with 0.1 records in the same `layers.aem` file.
