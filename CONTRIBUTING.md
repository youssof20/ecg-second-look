# Contributing

This is a small solo-maintained prototype. Prefer narrow pull requests that finish one vertical slice.

## Expectations

- Keep Training mode offline after install.
- Do not add free-form LLM text to Second Look / clinical analysis paths.
- Do not claim diagnostic performance without a defined dataset, metric, and limitations.
- Use synthetic or openly licensed, de-identified fixtures only.
- Include a visible failure or `not_assessable` path for new analysis stages.
- Add tests for the behavior you change.

## Local checks

From `app/`:

```bash
npm run test
npm run lint
npm run typecheck
npm run build
```

## Clinical safety reports

If you believe the software could encourage unsafe clinical use (wording, missing refusals, overconfident UI), open an issue labeled `clinical-safety` or email the address in `SECURITY.md`.
