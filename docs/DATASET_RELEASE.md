# Publishing the OctantFake dataset

The dataset belongs in a dedicated Hugging Face Dataset repository. Keep this GitHub repository for
code, documentation, and exact JSONL metadata; do not commit the 1.3 GB image tree to Git history.

## 1. Prepare a clean release directory

Run the converter against the frozen author artifact:

```bash
python scripts/prepare_dataset_release.py \
  --legacy-root /path/to/final_dataset_clean \
  --output /path/to/OctantFake-dataset-v1.0.0 \
  --copy-images
```

The converter verifies the expected 8,800 records and 800/8,000 split, assigns stable public IDs,
copies each image under its release split, records content checksums and group IDs, creates both
canonical manifests and Hugging Face ImageFolder metadata, and copies the current dataset card and
terms into the release root.

## 2. Authenticate and upload privately

Create a Hugging Face account or organization namespace, create a write token, and authenticate:

```bash
python -m pip install -e '.[dataset]'
hf auth login
python scripts/upload_dataset.py \
  --dataset-dir /path/to/OctantFake-dataset-v1.0.0 \
  --repo-id Syokan/OctantFake
```

The helper creates or updates a **private** dataset repository by default. Uploads use the Hub client,
which supports resumable large-folder transfer. Do not pass `--public` during the first upload.

## 3. Inspect the private repository

Before opening access, confirm that:

- the dataset card and terms render correctly;
- the viewer exposes `validation` with 800 rows and `test` with 8,000 rows;
- images and labels are visible for a sample from each split;
- `dataset_info.json` matches the displayed counts;
- the three canonical metadata checksums match `checksums/metadata.sha256`; and
- no credential, absolute local path, raw API response, or downloaded search-result cache appears.

Run a clean download and full checksum validation on a second location when practical:

```bash
hf download Syokan/OctantFake --repo-type dataset --local-dir /tmp/OctantFake-check
octantfake validate /tmp/OctantFake-check/metadata/octantfake.jsonl \
  --check-files --media-root /tmp/OctantFake-check
```

## 4. Choose access mode

Review the redistribution status of the underlying sources with the authors or institution before
broad release. If gated access is appropriate, make the repository public from its settings page,
enable **Access requests**, and choose automatic or manual approval. Gating records requesting users'
Hub identity and email but does not replace upstream licenses or permission.

Finally, create the `v1.0.0` tag or release note, update the dataset badge/link in this repository if
the namespace changed, and preserve the local frozen package used for the upload.

## Excluded material

Do not include raw Google API responses, downloaded search-result images, credentials, model weights,
logs, or machine-specific paths. A normalized evidence snapshot may be released separately only after
reviewing provider retention and redistribution terms.
