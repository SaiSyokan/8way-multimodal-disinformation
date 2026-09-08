"""Prompts for independent factor checks and eight-way aggregation."""

PROMPT_VERSION = "www26-v1"

DESCRIPTION_PROMPT = """Describe only visible, decision-relevant content in this image.
Mention people, objects, setting, displayed text, and apparent editing cues. Do not infer facts
that cannot be seen. Return a concise paragraph."""

CONSISTENCY_DESCRIPTION_PROMPT = """Describe the main event, entities, place, time cues, and
context visible in this image so that another model can compare it with a caption. Do not judge the
caption and do not infer facts that cannot be seen. Return a concise paragraph."""

IMAGE_PROMPT = """You verify the factual integrity of an image. Use the image, its visual
description, and reverse-image evidence. Decide F only when there is evidence of a factual
violation or manipulation; otherwise decide T within the available verification budget.

Visual description:
{description}

Reverse-image evidence:
{image_evidence}

Return one JSON object only:
{{"decision":"T or F","confidence":0.0,"explanation":"brief evidence-grounded reason"}}"""

TEXT_PROMPT = """You verify the factual integrity of the supplied text. Use the search
evidence. Decide F only when a verifiable claim is contradicted or fabricated; otherwise decide
T within the available verification budget. Do not evaluate image-text matching in this step.

Text:
{text}

Search evidence:
{text_evidence}

Return one JSON object only:
{{"decision":"T or F","confidence":0.0,"explanation":"brief evidence-grounded reason"}}"""

CONSISTENCY_PROMPT = """Decide whether the image and text describe the same event, entity,
place, and context. T means consistent; F means mismatched. Judge only cross-modal consistency,
not whether either modality is independently true.

Text:
{text}

Visual description:
{description}

Return one JSON object only:
{{"decision":"T or F","confidence":0.0,"explanation":"brief evidence-grounded reason"}}"""

AGGREGATOR_PROMPT = """Map the three ordered decisions to one OctantFake label. The order is
image veracity, text veracity, image-text consistency. Valid labels are:
TTT, TTF, TFT, TFF, FTT, FTF, FFT, FFF.

Image check: {image_result}
Text check: {text_result}
Consistency check: {consistency_result}

Use the decisions as the default mapping. If their explanations contain a clear conflict, the final
label may correct it, but explain the correction explicitly.

Return one JSON object only:
{{"label":"one valid label","confidence":0.0,"explanation":"brief synthesis and any correction"}}"""
