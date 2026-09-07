# Member Token V2

`api/_member_token.py` is the single source of truth. Two formats coexist.

## V1 (current, default)

```
token = HMAC_SHA256(HMAC_SECRET, email)   # hex
```

Deterministic, never expires, cannot be revoked for one member without
rotating `HMAC_SECRET` (which breaks every link at once). Used in
`/members/?t=…&e=…`, `/api/scan`, `/api/wallet`, Google Wallet objects.

## V2 (implemented, dormant)

```
token = "v2." + exp + "." + HMAC_SHA256(HMAC_SECRET, "v2:" + SALT + ":" + email + ":" + exp)
```

- `exp` — unix seconds; `validar_token` rejects once passed.
- `SALT` — `MEMBER_TOKEN_SALT` env. Bump it to invalidate every outstanding
  V2 link (rotation / mass revocation) without touching `HMAC_SECRET`.
- TTL — `MEMBER_TOKEN_V2_TTL_DAYS` (default 120).

`validar_token` already accepts both formats today. Nothing issues V2 yet.

## Rollout (each step is one env change + redeploy, reversible)

| Step | Env | Effect |
|---|---|---|
| now | *(none)* | issue V1, accept V1 + V2 |
| 1. start grace | `MEMBER_TOKEN_V2=1` | issue V2 for **new** links; old V1 links still work |
| 2. reissue | — | regenerate member links/QRs from the panel; re-send Wallet |
| 3. sunset V1 | `MEMBER_TOKEN_V1_SUNSET=YYYY-MM-DD` | after that date `validar_token` rejects V1 |
| rollback | unset `MEMBER_TOKEN_V2` | back to V1 issuance; V1 links accepted again |

## Why this is DEFERRED for production activation

Step 1 changes what `/api/link` and `/api/member` hand back. The happy path
(a real member token validating end-to-end through `/api/scan` and
`/api/wallet`) can only be exercised with `HMAC_SECRET`, which is not
available to the audit environment, and with a real member row. Activate
after one manual smoke test:

1. set `MEMBER_TOKEN_V2=1` in **Preview**, redeploy
2. from the panel, generate a link for a test member — confirm it starts `v2.`
3. open `/members/?t=<v2>&e=<email>` → card loads
4. scan flow: `/api/scan?...&t=<v2>` → PIN page → confirm → experience +1
5. `/api/wallet?e=<email>&t=<v2>` → redirects to Google Wallet
6. confirm an **old V1** link for the same member still works
7. promote the env var to Production
