# 8-Way Multimodal Disinformation

Official repository for our WWW 2026 short paper on **8-way multimodal disinformation analysis**.

This project introduces a unified **8-way taxonomy** of multimodal disinformation, in which each image-text pair is analyzed along three axes: **image veracity**, **text veracity**, and **cross-modal consistency**. By combining these three binary properties, the task is formulated as a closed-set classification problem with **eight exhaustive classes**.

This repository serves as the official project page for the benchmark. It currently provides the task overview, label taxonomy, example data format, and release roadmap. The full dataset, benchmark resources, and additional code will be released in future updates.

---

## News

- **[Feb 2026]** Repository initialized.
- **[Mar 2026]** README, task description, and example annotation format released.
- **[To Do]** Dataset download link will be added after the conference presentation.
- **[To Do]** Additional benchmark code, evaluation scripts, and release details will be updated in this repository.

---

## Overview

Multimodal disinformation is not limited to a single binary distinction such as *real* vs. *fake*. In real-world image-text content, misinformation may arise from multiple sources:

- the **image itself** may be false or manipulated,
- the **text itself** may be false or misleading,
- the **image and text may be semantically inconsistent**, even when one or both modalities appear individually plausible.

Existing formulations often treat these cases inconsistently, using different label spaces, partial taxonomies, or task-specific definitions. Our work aims to provide a more complete and systematic formulation.

We define multimodal disinformation using three binary axes:

- **Image veracity**: whether the image content has a verifiable factual violation or not,
- **Text veracity**: whether the textual content has a verifiable factual violation or not,
- **Cross-modal consistency**: whether the image and text are semantically consistent with each other.

This leads to a unified **8-way label space**, which covers the full combination of the three axes.

---

## Task Formulation

Given an **image-text pair**, the goal is to predict one of the **eight classes** defined by:

- image truth value: **T / F**
- text truth value: **T / F**
- image-text consistency: **T / F**

![tri-axis](/Users/cuishuhan/Desktop/tri-axis.png)

This formulation provides:

- a more fine-grained perspective than binary fake news detection,
- a more structured alternative to loosely defined fine-grained labels,
- a unified benchmark setting for multimodal disinformation analysis,
- an attribution-friendly label space that reveals *why* a pair is problematic.

---

## 8-Way Label Taxonomy

The eight labels are constructed from three binary decisions:

- **I**: Image veracity
- **T**: Text veracity
- **C**: Cross-modal consistency

For readability, each class can be denoted by a three-letter code:

- first position: image veracity
- second position: text veracity
- third position: consistency

For example, `TTT` means:
- the image is true,
- the text is true,
- the image and text are consistent.

### Label Space

| Label | Image | Text | Consistency | Description |
|------|------|------|-------------|-------------|
| TTT | True | True | True | Both modalities are individually true and mutually consistent. |
| TTF | True | True | False | Both image and text are individually true, but they do not refer to the same event/context/claim. |
| TFT | True | False | True | The image is true, the text is false, and the text is about the image in a semantically aligned but misleading way. |
| TFF | True | False | False | The image is true, the text is false, and the pair is also cross-modally inconsistent. |
| FTT | False | True | True | The image is false, the text is true, and the text matches the false image content. |
| FTF | False | True | False | The image is false, the text is true, but the pair is cross-modally inconsistent. |
| FFT | False | False | True | Both modalities are false, but they are mutually aligned. |
| FFF | False | False | False | Both modalities are false, and they are also inconsistent with each other. |

> **Note**
>  
> The precise operational definitions used in the benchmark will be documented in the released task documentation and annotation guideline. The descriptions above are intended as an intuitive overview for the label space.

---

## Why 8-Way Classification?

Our formulation is motivated by two limitations in existing multimodal disinformation research.

First, many existing settings collapse fundamentally different failure modes into a single “fake” category. However, an image-text pair can be problematic because the image is false, because the text is false, because the two modalities are mismatched, or because multiple issues happen simultaneously.

Second, even works that address more fine-grained cases often use incomplete or inconsistent taxonomies. This makes comparison across papers difficult and leaves some realistic multimodal scenarios under-defined.

By explicitly modeling **image truth**, **text truth**, and **cross-modal consistency** together, the 8-way formulation offers a more complete and interpretable task space.

---

## Repository Structure

```text
8way-multimodal-disinformation/
├── README.md
├── LICENSE
├── .gitignore
├── assets/
├── docs/
│   ├── task_definition.md
│   ├── label_taxonomy.md
│   ├── dataset_format.md
│   └── roadmap.md
├── examples/
│   ├── sample_annotations.json
│   └── README.md
├── data/
│   └── README.md
├── src/
│   └── README.md
└── bibtex/
    └── citation.bib
```

---

## Directory Guide

- assets/: figures used in the README or documentation
- docs/: detailed documentation for task definition, label taxonomy, data format, and release plan
- examples/: toy examples showing annotation format and sample entries
- data/: dataset release entry point and download instructions
- src/: code-related resources to be added in future updates
- bibtex/: citation file for the paper

---

## Example Data Format

The full dataset is not yet released, but the benchmark will follow a structured annotation format similar to the example below.

```
{
  "id": "sample_0001",
  "image_path": "images/sample_0001.jpg",
  "text": "A caption or claim associated with the image.",
  "label": "TFF",
  "image_veracity": true,
  "text_veracity": false,
  "consistency": false,
  "source": "source_name",
  "split": "test"
}
```

---

## Example Fields

- id: unique sample identifier
- image_path: relative path to the image file
- text: associated textual claim, caption, or post content
- label: 8-way class label
- image_veracity: binary label for image truthfulness
- text_veracity: binary label for text truthfulness
- consistency: binary label for semantic consistency between image and text
- source: source dataset or collection origin
- split: benchmark split (e.g., train / val / test)

Please note that the final released version may include additional metadata fields and more detailed annotation-related information.

---

## What Is Available Now

At the current stage, this repository provides:
- a high-level introduction to the 8-way task,
- the unified label taxonomy,
- an example data format,
- the project structure and release roadmap.

--- 

## Citation

If you find this repository useful, please cite our paper.

```bibtex
@inproceedings{cui2026eightway,
  author    = {Shuhan Cui and Ruimin Chu and Hanrui Wang and Patrick H. Chen and Ching-Chun Chang and Isao Echizen},
  title     = {An 8-Way Taxonomy for Multimodal Disinformation and Detection Benchmark},
  booktitle = {Proceedings of the ACM Web Conference 2026 (WWW '26)},
  year      = {2026},
  location  = {Dubai, United Arab Emirates},
  publisher = {ACM},
  address   = {New York, NY, USA},
  numpages  = {4},
  doi       = {10.1145/3774904.3792906}
}
```
