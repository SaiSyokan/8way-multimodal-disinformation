# OctantFake dataset

The canonical dataset release is hosted separately from the source code:

- **Dataset repository:** [Syokan/OctantFake](https://huggingface.co/datasets/Syokan/OctantFake)
- **Size:** 8,800 image-text pairs; approximately 1.3 GB of core images
- **Splits:** 800 calibration samples and 8,000 test samples; no training split

The exact metadata used for the WWW'26 experiments is included here:

- `metadata/calibration.jsonl`
- `metadata/test.jsonl`
- `dataset_info.json`
- `metadata.sha256`

Download the media with:

```bash
hf download Syokan/OctantFake --repo-type dataset --local-dir data/OctantFake
```

Then validate the complete release:

```bash
octantfake validate data/metadata/test.jsonl \
  --check-files \
  --media-root data/OctantFake
```

See [the dataset card](DATASET_CARD.md), [the terms of use](TERMS_OF_USE.md), and
[`docs/DATASET.md`](../docs/DATASET.md) for construction details.
