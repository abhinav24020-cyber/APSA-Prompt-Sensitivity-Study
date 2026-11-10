# Control Experiment Methodology

## Purpose

Before testing adversarial or natural perturbations, it is critical to measure the natural output variability (stochastic variance) of the underlying Large Language Models (LLMs). This baseline variance serves as a control group.

LLM outputs are not strictly deterministic, even with settings like `temperature=0.0`. Variations can arise from floating-point non-determinism, backend infrastructure routing, or minor API updates. If a perturbation appears to change the model's response, we must be confident that the change was caused by the perturbation itself and not just the natural variance of the model.

## Methodology

1. **Baseline Repeated Sampling**: 
   For each baseline prompt $P$, we run the query through the selected model $M$ multiple times (e.g., $N \ge 3$ for the pilot) under identical generation settings (the exact same prompt, same temperature, same max tokens).

2. **Measuring Baseline Variance**: 
   We measure the output variability between these identical-prompt runs. Pairwise distances (such as Levenshtein distance, BERTScore disparity, or semantic embedding cosine distances) are calculated among all $N$ outputs.
   - For example, with $N=3$ outputs ($O_1, O_2, O_3$), we calculate the distances $d(O_1, O_2)$, $d(O_2, O_3)$, and $d(O_1, O_3)$.
   - We aggregate these to find the mean baseline variance and the maximum baseline variance for that specific prompt and model combination.

3. **Data Isolation**: 
   Control experiment results are stored separately from the perturbation experiment results (e.g., in `results/control_experiment/`). This guarantees that baseline metrics can be cleanly referenced during the final statistical analysis.

## Analysis and Significance Testing

**Core Rule:** Do not claim that a perturbation caused an output change unless the change exceeds or is statistically distinguishable from the relevant control variability.

When comparing a perturbed prompt $P'$ and its output $O'$ against the baseline output $O$:
- The observed distance $d(O, O')$ must be significantly greater than the maximum or mean baseline distance calculated in the control experiment for prompt $P$.
- If $d(O, O')$ falls within the control confidence interval (i.e., it is statistically indistinguishable from natural variance), we classify the output as "robust" (unchanged by the perturbation). 
- Only statistically significant deviations are recorded as successful adversarial or natural vulnerabilities.
