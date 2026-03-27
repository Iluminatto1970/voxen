# Voxen Billing Private

This branch is reserved for private/commercial billing features.

## Scope

- Stripe checkout/session automation
- webhook verification and license activation
- background reconciliation worker
- private financial telemetry

## Security rules

- Never commit real keys.
- Use only environment variables.
- Keep private endpoint URLs outside public docs.

## Required env placeholders

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `VOXEN_STRIPE_WEBHOOK_SECRET`
- `VOXEN_STRIPE_PRICE_ID`
- `VOXEN_STRIPE_SUCCESS_URL`
- `VOXEN_STRIPE_CANCEL_URL`
