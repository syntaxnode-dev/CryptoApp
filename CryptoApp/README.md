# Crypto Authentication Lab

This version demonstrates an authorized credential exchange with modern
authenticated encryption. `challenge.py` serializes credentials in an
AES-256-GCM envelope, using a fresh 128-bit salt and a unique 96-bit nonce for
each encryption. The AES key is derived from the supplied passphrase through
the memory-hard `scrypt` KDF.

`solve.py` does not brute-force credentials. It authenticates its caller with a
local training API key, then verifies and decrypts the envelope with the
passphrase provided by the challenge owner. GCM verification rejects changed,
truncated, or incorrectly keyed ciphertexts.

The values in `api_keys.py` are intentionally fake training keys and are meant
to be committed. It also contains provider-shaped examples for OpenAI, GitHub,
Google Maps, and Stripe. They are not valid credentials for any service. An
external integration reads its real key from the documented environment variable
through `get_external_api_key(service)`; keep those real values in a secret
manager or environment variables, never in source control.

`challenge.py` can optionally send an audit event using one of those external
integrations. It sends no credentials or passphrase, only the event name and
the envelope version. This requires both a real key in the provider's
environment variable and an HTTPS endpoint:

```bash
set OPENAI_API_KEY=your_real_key
python challenge.py --audit-service openai --audit-url https://audit.example/events
```

## Run

Generate a challenge:

```bash
python challenge.py
```

Copy the JSON envelope and the demo passphrase it prints, then decrypt it with
the fake `challenge_solver` key from `api_keys.py`:

```bash
python solve.py 'JSON_ENVELOPE' 'DEMO_PASSPHRASE' --api-key 'fake_api_key_training_solver_4a9c1e8b7d3f'
```

Install the dependency first if necessary:

```bash
python -m pip install -r requirements.txt
```

## Work-in-progress HTTP app

`app.py` integrates the cryptographic challenge, the authorized solver, and
the external-service configuration. Its audit delivery endpoint deliberately
returns `501 Not Implemented`: it is **Work in progress** and does not make an
external request. Start it locally with:

```bash
python app.py
```

Available routes are `GET /health`, `POST /challenges`, `POST /solve`, and the
placeholder `POST /audit/send`. A challenge response includes a
`demo_passphrase` only for this local laboratory application.
