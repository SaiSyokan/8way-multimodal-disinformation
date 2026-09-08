# Installation

## Supported setup

The repository requires Python 3.10 or later. Validation, evaluation, and tests are CPU-only. Dataset
construction and LLaVA inference require substantially more memory and should be configured for the
available hardware.

### Virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Install only the optional components needed for a run:

```bash
python -m pip install -e '.[builder]'    # CLIP-based dataset construction
python -m pip install -e '.[evidence]'   # Google search evidence collectors
python -m pip install -e '.[inference]'  # local model adapter prerequisites
python -m pip install -e '.[dataset]'    # Hugging Face upload helper
```

Use `python -m pip install -e '.[builder,evidence,inference]'` to install all groups. On
Windows, replace the activation command with `.venv\\Scripts\\activate`.

### Conda

```bash
conda env create -f environment.yml
conda activate octantfake
```

## GPU and LLaVA

Install a PyTorch build compatible with the local CUDA driver before installing the inference group.
The repository intentionally provides a thin LLaVA adapter instead of copying the upstream project.
Install the LLaVA source version required by the chosen LLaVA-1.6 checkpoint in the same environment.
Model weights are downloaded from their official host and are not part of this repository.

The `--model-path`, `--model-base`, and `--conversation-mode` options are recorded in each run's
metadata sidecar. Use `--temperature 0` for the deterministic decoding setting; record hardware,
checkpoint revision, CUDA, PyTorch, Transformers, and LLaVA versions for every published run.

## Evidence credentials

Direct text search requires `GOOGLE_CUSTOM_SEARCH_API_KEY` and
`GOOGLE_CUSTOM_SEARCH_ENGINE_ID`. Reverse-image web detection uses Google Application Default
Credentials. Keep credentials outside the repository:

```bash
export GOOGLE_CUSTOM_SEARCH_API_KEY='...'
export GOOGLE_CUSTOM_SEARCH_ENGINE_ID='...'
gcloud auth application-default login
```

Do not place service-account files in the project tree. Provider quotas, billing, and retention terms
apply to live collection.

## Verification

```bash
make test
make smoke
```

No dataset, model, network connection, or cloud credential is required for these checks.
