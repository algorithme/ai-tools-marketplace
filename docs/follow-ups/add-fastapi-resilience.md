# Add fastapi-resilience

Status: pending source. The supplied `marketplace.json` lists this plugin, but
`grumpy-senior-engineer-workflow-1.3.0.zip` does not include its implementation.
Grumpy's companion references are preserved; `fastapi-resilience` is not yet
available from `olivier-vault`.

## Source metadata

- Name: `fastapi-resilience`
- Source path: `./plugins/fastapi-resilience`
- Supplied version: `1.0.0` (confirm against the implementation when obtained)
- Author: Olivier Morel
- Description: Resiliency for FastAPI external calls (HTTP, DB, gRPC, brokers, caches) using tenacity: retries, backoff, timeouts, and error classification.
- Keywords: `fastapi`, `tenacity`, `resilience`, `retry`, `backoff`, `http`, `grpc`, `database`

## Delivery checklist

- [ ] Obtain the implementation and confirm its version, provenance, and license.
- [ ] Import it into `plugins/fastapi-resilience/`, adapting repository and contact metadata to `omorel/ai-tools-marketplace` and `olivier@devbox.ch`.
- [ ] Register it in `.claude-plugin/marketplace.json` with the explicit source `./plugins/fastapi-resilience`, using the metadata above. Keep the version in the plugin manifest only.
- [ ] Add plugin documentation, a changelog, and a root README catalog entry. Document installation with `/plugin install fastapi-resilience@olivier-vault`.
- [ ] Run `./scripts/validate.sh` with all required tools available, validate the plugin with `claude plugin validate plugins/fastapi-resilience`, and verify its component paths and usage.
- [ ] Verify Grumpy's companion references in the `plan` and `implement` skills and `grumpy-implement` command resolve to the imported skill, including external-call planning and implementation scenarios.
- [ ] Remove the pending-availability note from Grumpy's README and mark this follow-up complete once the plugin is available.
