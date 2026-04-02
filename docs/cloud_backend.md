# Cloud Backend

## Role

The cloud backend is the canonical coordination layer for the personal AI system.

It provides:

- stronger cloud inference
- canonical memory/profile/address book storage
- device and desktop sync APIs
- upload and media metadata intake
- adaptive interface hints

## API Surface

- `GET /health`
- `POST /v1/query`
- `POST /v1/sync/push`
- `POST /v1/sync/pull`
- `POST /v1/upload`
- `GET /v1/profile`
- `POST /v1/profile/facts`
- `GET /v1/address-book`
- `POST /v1/address-book`

## Storage Model

- Supabase Storage-backed JSON state for the hosted prototype
- local JSON fallback for development without hosted credentials
- append-only style merge behavior for sync safety
- memory facts grouped by category:
  - preferences
  - habits
  - relationships
  - life_details

## Deployment Notes

- Hosted on Vercel as a Python serverless API
- Uses Supabase Storage as the canonical state store in the prototype
- Run behind TLS and real authentication before production use
- Replace JSON object persistence with PostgreSQL + object storage for production
- Add signed upload URLs for photos/documents in production
