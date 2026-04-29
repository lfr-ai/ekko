# JWT Setup

## Generate a Secret

```bash
openssl rand -base64 32
```

## Configure

Set in `.env` (or `.env.local` for local dev):

```env
EKKO_JWT_SECRET_KEY=<paste-generated-secret>
EKKO_JWT_EXPIRE_MINUTES=30
```

The default `change-me-ekko-jwt-secret` is only accepted in `local` environment.
Non-local environments will reject insecure defaults on startup.

## How It Works

1. **Create token**: `POST /api/auth/token` returns a signed JWT
2. **Use token**: Include `Authorization: Bearer <token>` in requests
3. **Verify**: The `jwt_adapter` decodes and validates the token on each request

## Token Payload

```json
{
  "sub": "<user-identifier>",
  "exp": 1234567890
}
```

## Files

| File | Purpose |
|------|---------|
| `backend/src/ekko/infrastructure/auth/jwt_adapter.py` | Token create/decode |
| `backend/src/ekko/config/settings/base.py` | `jwt_secret_key`, `jwt_expire_minutes`, `jwt_algorithm` |
| `backend/src/ekko/presentation/api/routes/auth.py` | Auth endpoints |
| `backend/src/ekko/presentation/api/middleware/authentication.py` | Request validation |
