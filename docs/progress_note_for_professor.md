Subject: APSA project: live experiment completed, results and draft paper

Respected Sir,

Following our earlier update, we are happy to report that the challenges we described have now been addressed. The APSA study has been run on live models, and the full analysis and a draft research paper are ready.

**How the five challenges were addressed**

1. **API rate limits.** The earlier run stopped because the experiment aborted on *any* HTTP 429 response, including short per-minute token limits. The runner now waits out per-minute limits, stops only on daily quotas, and resumes without repeating completed work. The main study then finished: **2,870 of 2,875 scheduled generations** across five models. The 5 missing generations are genuine model errors (a spurious tool call), recorded rather than imputed.
2. **Dataset validation.**
   - The 10 code-generation items are now checked by executing unit tests, and all reference solutions pass.
   - The 40 other scored items use explicit, auditable answer rules. A check of 40 randomly sampled verdicts found 39 correct, and the one error was fixed.
   - Full expert review of the reference answers is still outstanding.
3. **Semantic preservation.** A systematic audit of the perturbations found that 15 of 425 (3.5%) changed the meaning of the task, for example "valid orders" → "invalid orders" or "Liam Chen" → "Liam Ch3n". Results are reported both with and without them.
4. **Evaluation.** Correctness is now measured with answer keys and unit tests instead of text similarity alone. Text and embedding distances are reported as secondary measures, with their limitations stated.
5. **Experimental coverage.**
   - Models: Qwen 3.8 27B, GPT-OSS-120B, GPT-OSS-20B, ALLaM-2-7B and Gemini 3.1 Flash-Lite.
   - Prompts: 50 scorable prompts across all five categories.
   - Perturbations: 10 operators per prompt.
   - Controls: two unchanged-prompt repeats for every model and prompt (500 control pairs).

**Main findings**

- Small perturbations changed the output text in **66%** of cases, against **7%** when the identical prompt was re-sent (paired Wilcoxon *p* < 10⁻⁴⁰; significant for every model).
- Correctness changed in **4.3%** of perturbed cases and in **none** of the 500 controls.
- Strong models mostly kept their answers (0.9–3.1% flips); the 7B model flipped 14% of the time.
- Perturbations that accidentally altered the task produced wrong answers **17.6%** of the time, against **1.0%** for meaning-preserving edits.
- Examples: removing a "?" made one model name Heisenberg instead of Einstein, and appending a "." made another classify Spanish text as Portuguese.
- Sentence reordering was the most disruptive edit. The size of an edit barely predicted the size of its effect.

**Deliverables**

- Research paper draft (Markdown and Word): `docs/paper/APSA_research_paper.docx`
- Verification report for Phases 11–17: `docs/roadmap/phases_11_to_17_verification.md`
- An interactive viewer of all 2,620 output pairs and a demonstration script (`experiments/demo.py`)
- Test suite: 231 tests passing

**Remaining limitations and next steps**

- The semantic audit should be repeated by independent human annotators.
- Only temperature 0 was tested, with 50 of the 100 prompts.
- Research question 5 (adversarial search) was only approximated. A token-level search is planned as future work.

We would be grateful for your feedback on the results and the draft paper.

Regards,
Abhinav Arora & Aditya Kumar Giri
