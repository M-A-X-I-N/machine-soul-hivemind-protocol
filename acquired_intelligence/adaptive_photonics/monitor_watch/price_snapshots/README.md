# Price snapshots

Each `YYYY-MM-DDTHHMMSS+HHMM.yaml` file is an immutable market observation keyed to the **run-start time** in Europe/Stockholm.

The initial `2026-10-01.yaml` snapshot predates timestamped filenames and remains unchanged as a legacy first run.

Filename example:

~~~text
2026-10-01T044527+0200.yaml
~~~

Full ISO timestamps with colons are stored inside the YAML.

Snapshots preserve:

- direct retailer prices;
- aggregator observations;
- offer restrictions;
- stock state;
- source freshness;
- coverage and retrieval failures.

Do not rewrite an old snapshot merely to make it look current.

If an old snapshot contains a factual transcription error, correct it explicitly in a dedicated commit and document the correction.
