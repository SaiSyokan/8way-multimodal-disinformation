# Dataset construction

## Sources

The six multimodal adapters read the historical layouts of COSMOS, DGM4, MEIR, MMFakeBench,
NewsCLIPpings, and VERITE. Their source labels are mapped to the three OctantFake factors in
`builder/mappers/multimodal.py`. Unknown labels and missing media are excluded; they are never
assigned a default class.

The two classes absent from these direct mappings, `TFF` and `FFF`, are formed by controlled pairing
from single-modality pools. The paper uses image sources Factify, MS-COCO, OpenImages, DF2023,
Fakeddit, and PS-Battles, and text sources FakeNewsNet, LIAR, Politifact, and WELFake. Obtain every
source from its official distributor and comply with its license and access conditions.

The implemented direct-label mapping is:

| Source | Original label | OctantFake label |
|---|---|---|
| COSMOS | context label 0 / 1 | `TTT` / `TTF` |
| DGM4 | orig | `TTT` |
| DGM4 | text_attribute / text_swap | `TFT` / `TTF` |
| DGM4 | face_attribute or face_swap | `FTT` |
| DGM4 | face manipulation + text_attribute | `FFT` |
| DGM4 | face manipulation + text_swap | `FTF` |
| MEIR | none / manipulated text class | `TTT` / `TFT` |
| MMFakeBench | original / textual / visual / mismatch | `TTT` / `TFT` / `FTT` / `TTF` |
| NewsCLIPpings | falsified false / true | `TTT` / `TTF` |
| VERITE | true / miscaptioned / out-of-context | `TTT` / `TFT` / `TTF` |

## Normalized pool formats

The builder deliberately separates source-specific downloading/normalization from benchmark
selection. This prevents unofficial download URLs and redistribution assumptions from becoming part
of the benchmark definition.

`images.jsonl` contains one object per line:

```json
{"id":"globally-unique-image-id","path":"relative/or/absolute.jpg","source":"source-name","veracity":"T","metadata":{}}
```

`texts.jsonl` uses:

```json
{"id":"globally-unique-text-id","text":"claim or caption","source":"source-name","veracity":"F","metadata":{}}
```

IDs must remain stable across runs. Relative image paths are resolved from the image-pool manifest.
The exported `image_path` is made relative to `media_root`; construction fails if a file falls
outside that root, preventing local absolute paths from leaking into a release manifest. Pass the
same root through `--media-root` when validating files or running inference.

## Selection invariants

- CLIP ViT-B/32 cosine similarity must be strictly greater than `0.32` for matched pairs and strictly
  lower than `0.22` for mismatched pairs.
- No class-specific threshold override is allowed.
- Only `TFF` and `FFF` may be filled from independently sourced image/text pools.
- An image ID and a text ID may each occur at most once in the final benchmark.
- The random seed is explicit, and source-native candidates are sampled in deterministic round-robin
  order to avoid an accidental single-source prefix.
- Each class contains 1,100 items, for 8,800 total. The frozen split contains 800 calibration and
  8,000 test items; the split itself is not forced to contain identical per-class counts.

## Exact paper split

The canonical manifests under `data/metadata/` freeze the exact 8,800 records and 800/8,000 split
used by the paper. The Hugging Face `validation` folder corresponds to the paper's calibration split.
Regenerating from independently updated source datasets may produce a different, still valid
candidate set, so reported benchmark comparisons should use the released manifests and checksums.

The frozen experiment artifact preserves a limited amount of repeated upstream content. Its public
metadata includes image and normalized-text checksums plus content-group IDs so researchers can
audit overlap or create group-disjoint derived partitions. This does not change the official zero-shot
test protocol; it prevents accidental leakage in any new training or learned-calibration experiment.
