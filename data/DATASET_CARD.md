---
pretty_name: OctantFake
language:
  - en
license: other
task_categories:
  - image-classification
tags:
  - multimodal
  - misinformation
  - disinformation
  - fact-checking
  - image-text
size_categories:
  - 1K<n<10K
---

# OctantFake

OctantFake is an English image-text benchmark for eight-way multimodal disinformation
classification. It accompanies the WWW'26 short paper **“An 8-Way Taxonomy for Multimodal
Disinformation and Detection Benchmark.”**

Each sample is labeled on three ordered binary axes: image veracity, text veracity, and image-text
consistency. Their Cartesian product yields `TTT`, `TTF`, `TFT`, `TFF`, `FTT`, `FTF`, `FFT`, and
`FFF`.

## Dataset summary

| Property | Value |
|---|---:|
| Total samples | 8,800 |
| Classes | 8 |
| Samples per class | 1,100 |
| Calibration split | 800 |
| Test split | 8,000 |
| Training split | None |
| Image sources | 11 source names |
| Text sources | 10 source names |

The Hugging Face `validation` split is the paper's **calibration** split. It is intended only for
pipeline checks and prompt-format stabilization, not task-specific training.

## Label space

| Label | Image | Text | Consistency |
|---|---|---|---|
| `TTT` | no factual violation detected | no factual violation detected | match |
| `TTF` | no factual violation detected | no factual violation detected | mismatch |
| `TFT` | no factual violation detected | factual violation | match |
| `TFF` | no factual violation detected | factual violation | mismatch |
| `FTT` | factual violation | no factual violation detected | match |
| `FTF` | factual violation | no factual violation detected | mismatch |
| `FFT` | factual violation | factual violation | match |
| `FFF` | factual violation | factual violation | mismatch |

For image and text, `T` means that no violation was detected under the benchmark's fixed verification
budget; it is not an unlimited proof of truth.

## Files and loading

The release uses the Hugging Face ImageFolder layout:

```text
OctantFake/
├── README.md
├── TERMS_OF_USE.md
├── dataset_info.json
├── validation/
│   ├── metadata.jsonl
│   └── images/
├── test/
│   ├── metadata.jsonl
│   └── images/
├── metadata/
│   ├── octantfake.jsonl
│   ├── calibration.jsonl
│   └── test.jsonl
└── checksums/
    ├── images.sha256
    └── metadata.sha256
```

```python
from datasets import load_dataset

dataset = load_dataset("Syokan/OctantFake")
calibration = dataset["validation"]
test = dataset["test"]
```

For code that expects local image paths, download the complete dataset and use the canonical
manifests under `metadata/`.

## Record fields

- `sample_id`: stable public identifier.
- `image_path` / `file_name`: release-relative image location.
- `text`: paired caption or claim.
- `label`: canonical eight-way label.
- `image_veracity`, `text_veracity`, `image_text_consistency`: axis labels in fixed order.
- `image_source`, `text_source`: source dataset names.
- `construction_type`: `source_native` or `cross_modal_supplement`.
- `split`: `calibration` or `test`.
- `image_sha256`, `text_sha256`: content checksums.
- `image_group_id`, `text_group_id`: stable content-group identifiers.
- `metadata.original_index`: index used in the original experiment files.
- `metadata.original_label`: original source annotation when available.

## Sources

OctantFake consolidates COSMOS, DGM4, MEIR, MMFakeBench, NewsCLIPpings, VERITE, Factify,
MS-COCO, OpenImages, DF2023, Fakeddit, PS-Battles, FakeNewsNet, LIAR, PolitiFact, and WELFake.
The six multimodal sources provide native image-text pairs. `TFF` and `FFF` are completed through
controlled pairing from the single-modality pools and CLIP-based mismatch filtering.

## Known limitations

- The exact v1.0.0 release preserves the records and split used for the paper's experiments.
- Some source datasets contain the same media or caption in more than one record or manipulation
  configuration. The release contains 706 byte-identical image groups and 495 repeated normalized-text
  groups. Of these, 138 image groups and 111 text groups occur in both calibration and test.
- There is no training split. Researchers performing any training, few-shot selection, or learned
  calibration should use `image_group_id` and `text_group_id` to create group-disjoint partitions.
- Labels inherit assumptions and possible annotation errors from their source datasets and from the
  deterministic mapping rules.
- Web evidence is time-sensitive and is not part of the core dataset release.
- The benchmark is English-dominant and does not represent all languages, regions, events, or forms
  of multimodal disinformation.

## License and access

This is a composite research dataset. The annotations and packaging do not replace or override the
licenses, copyright, privacy conditions, or terms of the underlying sources. There is therefore no
single blanket license for all image and text content. Read `TERMS_OF_USE.md` before requesting or
using the files. A gated Hugging Face release is recommended.

## Citation

```bibtex
@inproceedings{cui2026eightway,
  author    = {Shuhan Cui and Ruimin Chu and Hanrui Wang and Patrick H. Chen and Ching-Chun Chang and Isao Echizen},
  title     = {An 8-Way Taxonomy for Multimodal Disinformation and Detection Benchmark},
  booktitle = {Proceedings of the ACM Web Conference 2026},
  year      = {2026},
  doi       = {10.1145/3774904.3792906}
}
```
