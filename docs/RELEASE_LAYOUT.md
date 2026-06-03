# Release layout

The shippable product distribution is assembled from the root package, not from
the donor validation kit submodule.

Included:

- `src/aethermind/`
- `tools/`
- `plugins/hermes/aethermind/`
- `tests/`
- `examples/`
- `docs/`
- `README.md`
- `LICENSE`
- `pyproject.toml`

Excluded:

- `.git/`
- `.hermes/`
- `.aethermind/`
- caches and bytecode
- donor submodules
- benchmark/evidence/proof/reviewer packets
- private source-authority docs

Generated artifacts include a directory drop, tarball, tarball checksum, and
`MANIFEST.sha256` for files inside the drop.
