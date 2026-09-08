# Taxonomy

OctantFake factorizes a multimodal item along three binary axes in this fixed order:

1. **image veracity** — `F` when verifiable evidence supports a factual violation or manipulation;
2. **text veracity** — `F` when a verifiable textual claim is contradicted or fabricated; and
3. **image-text consistency** — `F` when image and text refer to incompatible content or context.

The Cartesian product yields `TTT`, `TTF`, `TFT`, `TFF`, `FTT`, `FTF`, `FFT`, and `FFF`.
`T` on a veracity axis means no violation was established within the stated verification budget; it
must not be interpreted as an unlimited proof of truth. The consistency axis is evaluated separately
from factuality, so a matching pair can still contain false content.

All software uses the paper's `T/F/T` notation. `from_legacy_label` is provided only to migrate old
internal manifests whose consistency suffix was `M` (match) or `X` (mismatch).
