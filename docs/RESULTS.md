# Reported results

The following values are transcribed from Table 1 of the WWW'26 paper. They are macro-averaged
F1 / precision / recall percentages, rounded to one decimal place.

| Scale | Method | Calibration (800) | Test (8,000) |
|---|---|---:|---:|
| 7B | SNIFFER | 20.8 / 26.0 / 18.2 | 19.1 / 24.5 / 17.4 |
| 7B | FKA-Owl | 17.2 / 22.8 / 15.1 | 16.5 / 22.0 / 14.3 |
| 7B | DEFAME | 16.8 / 21.0 / 15.6 | 17.4 / 21.5 / 16.3 |
| 7B | MMD-Agent | 15.3 / 18.4 / 14.0 | 15.1 / 20.4 / 12.2 |
| 7B | OctantAgent | 21.7 / 26.8 / 20.6 | 20.4 / 25.5 / 19.6 |
| 34B | SNIFFER | 28.7 / 33.1 / 27.0 | 27.9 / 32.0 / 26.2 |
| 34B | FKA-Owl | 26.1 / 31.3 / 24.5 | 26.9 / 31.1 / 25.5 |
| 34B | DEFAME | 24.4 / 29.4 / 23.1 | 24.1 / 28.5 / 22.4 |
| 34B | MMD-Agent | 23.2 / 27.1 / 21.4 | 22.2 / 26.1 / 20.6 |
| 34B | OctantAgent | 31.6 / 36.9 / 30.4 | 30.1 / 35.2 / 28.7 |
| GPT-4V | SNIFFER | 45.9 / 50.3 / 44.0 | 44.1 / 48.9 / 42.1 |
| GPT-4V | FKA-Owl | 47.8 / 51.1 / 46.2 | 45.5 / 49.1 / 44.0 |
| GPT-4V | DEFAME | 43.8 / 49.0 / 41.1 | 42.9 / 47.5 / 40.6 |
| GPT-4V | MMD-Agent | 41.5 / 47.4 / 39.3 | 40.6 / 44.8 / 38.2 |
| GPT-4V | OctantAgent | 50.7 / 55.9 / 49.7 | 49.2 / 54.3 / 47.6 |

These are the paper's reported reference values. New runs should publish normalized prediction files,
run metadata, the repository revision, model revision, and evidence-snapshot checksum alongside their
metrics; small differences may result from model serving, evidence freshness, or dependency changes.
