# Authentication

Ekko runs as a local-only desktop application. Authentication is auto-provided:

- All requests are automatically authenticated as `dev-user` with `admin` role
- No tokens, passwords, or login required
- The `AuthenticationMiddleware` attaches a `UserProfile` to every request
- The `AuthorizationMiddleware` is a no-op (all requests allowed)

This design is intentional — a single-user local app has no need for auth gates.
