# OctantAgent prompt protocol

The canonical prompt version is `www26-v1`. The executable templates are defined in
`src/octantfake_www/method/prompts.py`; this file explains their roles without maintaining a second,
potentially divergent copy.

## Stages

1. **Image description.** A vision-language model summarizes visible objects, entities, scene cues,
   displayed text, and apparent editing cues without introducing unverifiable facts.
2. **Consistency description.** A separate description emphasizes event, entity, place, time, and
   context cues for comparison with the supplied text.
3. **Image check.** The model receives the image, factual description, and normalized reverse-image
   evidence and returns `T` or `F`, a confidence value, and a short explanation.
4. **Text check.** The model receives the text and normalized evidence from the top three search
   results. It judges only textual veracity, not cross-modal agreement.
5. **Consistency check.** The model compares the text with the consistency-oriented visual
   description and judges only whether they describe the same situation.
6. **Aggregation.** The three ordered decisions are mapped to one of the eight valid labels. The
   aggregator may correct a clear conflict only when it explains the correction.

## Output contract

Factor stages return one JSON object with `decision`, `confidence`, and `explanation`. The aggregator
returns `label`, `confidence`, and `explanation`. The parser accepts fenced JSON and minor formatting
noise but does not fabricate a fallback prediction when parsing fails. Invalid output is preserved as
invalid and counted as incorrect during evaluation.

## Versioning

Prompt changes can alter benchmark results. Any change to wording, evidence rendering, parsing, or
aggregation should increment `PROMPT_VERSION` and be recorded in the run metadata. Published
comparisons must use one frozen prompt version and evidence snapshot across matched backbones.
