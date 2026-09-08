# Baseline normalization

The WWW paper compares SNIFFER, FKA-Owl, DEFAME, MMD-Agent, and OctantAgent with the backbones
described in the paper. Their repositories and model weights remain external dependencies and are
not copied here.

Convert every baseline output to JSONL before evaluation:

```json
{"sample_id":"stable-id","gold_label":"TTT","prediction":"TTF"}
```

`prediction` must be one of the eight canonical labels or `null`. Parse failures, timeouts, and
missing responses remain invalid and count as incorrect. Do not map them to `TTT`. Keep the raw model
response and error in additional fields so the normalization is auditable.

For a fair comparison, preserve the paper's zero-shot setting, split, backbone/checkpoint, decoding
parameters, evidence snapshot, and prompt version. Report macro precision, macro recall, macro F1,
accuracy, and the invalid-output count from the common evaluator.
