# Price snapshots

Each `YYYY-MM-DD.yaml` file is an immutable market observation.

Snapshots preserve:

- direct retailer prices;
- aggregator observations;
- offer restrictions;
- stock state;
- source freshness;
- coverage and retrieval failures.

Do not rewrite an old snapshot merely to make it look current.

If an old snapshot contains a factual transcription error, correct it explicitly in a dedicated commit and document the correction.
