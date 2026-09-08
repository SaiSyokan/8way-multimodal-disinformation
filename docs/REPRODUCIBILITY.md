# Reproducibility protocol

Record the following for every published run:

- repository commit and configuration files;
- official manifest checksum and source-dataset versions;
- Python, PyTorch, Transformers, LLaVA, CUDA, model checkpoint, and hardware versions;
- random seed and decoding settings;
- evidence provider, collection date, and evidence-snapshot checksum;
- raw outputs, normalized predictions, invalid-output count, and evaluation JSON.

Run the local checks before inference:

```bash
octantfake validate data/OctantFake/metadata/octantfake.jsonl \
  --check-files --media-root data/OctantFake
python -m unittest discover -s tests -v
```

After inference:

```bash
octantfake evaluate predictions/run.jsonl --output predictions/run.metrics.json
```

The evaluator computes all eight per-class metrics even if a class has no predicted instances. An
invalid response contributes a false negative for its gold class and never a false positive for an
invented fallback class.

Manifest validation distinguishes structural errors from documented content-group warnings. The
official v1.0.0 metadata contains `image_group_id` and `text_group_id`; any derived training or
selection split should be group-disjoint on both fields.
