# Evidence collection

OctantAgent uses direct text search and reverse-image web detection. Live search results change, so
the recommended experiment path is:

1. collect evidence once;
2. record collection time, provider, query, and service configuration;
3. freeze the JSON files for a run; and
4. run all compared methods against the same snapshot where their protocols permit it.

The paper uses the top three text-search pages (`k = 3`). The default collector and renderer enforce
that value. Image-search evidence is used by the image-veracity branch; the consistency branch uses
an independently generated visual description and the input text, as specified in the paper.

Text collection reads `GOOGLE_CUSTOM_SEARCH_API_KEY` and
`GOOGLE_CUSTOM_SEARCH_ENGINE_ID`. Reverse-image collection uses Google Application Default
Credentials; follow Google's supported authentication setup rather than placing a credential file or
machine path in this repository.

The normalized layouts are `evidence/text/<sample_id>.json` and
`evidence/image/<sample_id>.json`. By default, the image collector follows matched-page URLs to
capture bounded title, description, and surrounding-text fields; use `--no-page-context` if the
environment or provider terms do not permit this. Synthetic examples are committed under `examples/evidence`.
Before redistributing an evidence snapshot, review provider terms because snippets, thumbnails, and
URLs can have separate retention or redistribution rules.
