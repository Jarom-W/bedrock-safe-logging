## Secret Logging Review Checklist

- [ ] No raw prompt text is logged unless explicit debug prompt logging is enabled.
- [ ] Logs use `_mask_sensitive_information()` before emitting prompt-derived content.
- [ ] `.env` files are not committed.
- [ ] `.env.example` contains placeholders only.
- [ ] No AWS credentials appear in code, tests, docs, or sample logs.
- [ ] No `AKIA...` or `ASIA...` access key IDs appear in committed files.
- [ ] No `aws_secret_access_key`, `aws_session_token`, `password`, `token`, or `api_key` values are hardcoded.
- [ ] Error logs include `trace_id` but do not include raw secrets.
- [ ] Integration tests use named profiles/SSO, not static credentials.
