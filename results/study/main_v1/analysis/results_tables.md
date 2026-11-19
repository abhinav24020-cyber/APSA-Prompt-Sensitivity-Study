# APSA study results tables - main_v1
Generated 2026-11-19T20:30:39.164687+00:00 from `processed/analysis_pairs.csv`.

## Data reconciliation
| model | scheduled_generations | recorded_successes | recorded_failures | rate_limit_stops | not_attempted | truncated | empty_outputs | prompts_with_anchor |
|---|---|---|---|---|---|---|---|---|
| qwen/qwen3.8-27b | 575 | 575 | 0 | 0 | 0 | 5 | 0 | 50 |
| openai/gpt-oss-120b | 575 | 575 | 0 | 0 | 0 | 0 | 0 | 50 |
| openai/gpt-oss-20b | 575 | 570 | 5 | 0 | 5 | 1 | 0 | 50 |
| allam-2-7b | 575 | 575 | 0 | 0 | 0 | 0 | 0 | 50 |
| gemini-3.1-flash-lite | 575 | 575 | 2 | 1 | 0 | 0 | 0 | 50 |

## Treatment vs control (prompt-level paired differences)
| model | metric | n_model_prompt_units | mean_treatment | mean_control | mean_diff | diff_ci_low | diff_ci_high | p_value | rank_biserial |
|---|---|---|---|---|---|---|---|---|---|
| ALL MODELS | d_out_sem | 250 | 0.0612 | 0.0027 | 0.0585 | 0.0477 | 0.0700 | 6.27e-41 | 0.9841 |
| allam-2-7b | d_out_sem | 50 | 0.0945 | 0.0000 | 0.0945 | 0.0733 | 0.1179 | 8.26e-10 | 1.0000 |
| gemini-3.1-flash-lite | d_out_sem | 50 | 0.0407 | 0.0000 | 0.0407 | 0.0297 | 0.0523 | 7.79e-10 | 1.0000 |
| openai/gpt-oss-120b | d_out_sem | 50 | 0.0605 | 0.0102 | 0.0504 | 0.0300 | 0.0751 | 2.79e-08 | 0.9227 |
| openai/gpt-oss-20b | d_out_sem | 50 | 0.0764 | 0.0016 | 0.0748 | 0.0489 | 0.1036 | 2.21e-09 | 0.9960 |
| qwen/qwen3.8-27b | d_out_sem | 50 | 0.0338 | 0.0019 | 0.0319 | 0.0239 | 0.0404 | 2.74e-09 | 0.9673 |
| ALL MODELS | d_out_char | 250 | 0.2146 | 0.0129 | 0.2017 | 0.1721 | 0.2329 | 1.74e-41 | 0.9867 |
| allam-2-7b | d_out_char | 50 | 0.3534 | 0.0005 | 0.3529 | 0.2973 | 0.4045 | 7.79e-10 | 1.0000 |
| gemini-3.1-flash-lite | d_out_char | 50 | 0.1780 | 0.0000 | 0.1780 | 0.1389 | 0.2182 | 7.79e-10 | 1.0000 |
| openai/gpt-oss-120b | d_out_char | 50 | 0.1693 | 0.0365 | 0.1327 | 0.0975 | 0.1704 | 7.94e-13 | 0.9671 |
| openai/gpt-oss-20b | d_out_char | 50 | 0.1917 | 0.0090 | 0.1827 | 0.1283 | 0.2411 | 2.84e-09 | 0.9807 |
| qwen/qwen3.8-27b | d_out_char | 50 | 0.1806 | 0.0183 | 0.1623 | 0.1238 | 0.2038 | 2.74e-09 | 0.9673 |
| ALL MODELS | d_out_token | 250 | 0.2495 | 0.0161 | 0.2335 | 0.2035 | 0.2651 | 1.15e-40 | 0.9877 |
| allam-2-7b | d_out_token | 50 | 0.3860 | 0.0013 | 0.3848 | 0.3252 | 0.4404 | 8.26e-10 | 1.0000 |
| gemini-3.1-flash-lite | d_out_token | 50 | 0.2268 | 0.0000 | 0.2268 | 0.1803 | 0.2734 | 7.79e-10 | 1.0000 |
| openai/gpt-oss-120b | d_out_token | 50 | 0.1933 | 0.0516 | 0.1418 | 0.1006 | 0.1857 | 8.53e-08 | 0.9487 |
| openai/gpt-oss-20b | d_out_token | 50 | 0.2205 | 0.0065 | 0.2141 | 0.1569 | 0.2754 | 3.68e-09 | 0.9956 |
| qwen/qwen3.8-27b | d_out_token | 50 | 0.2208 | 0.0210 | 0.1998 | 0.1574 | 0.2458 | 2.29e-09 | 0.9722 |
| ALL MODELS | answer_changed | 234 | 0.1710 | 0.0085 | 0.1624 | 0.1258 | 0.2016 | 1.41e-18 | 0.9663 |
| allam-2-7b | answer_changed | 42 | 0.4909 | 0.0000 | 0.4909 | 0.3701 | 0.6086 | 1.68e-07 | 1.0000 |
| gemini-3.1-flash-lite | answer_changed | 50 | 0.0756 | 0.0000 | 0.0756 | 0.0277 | 0.1374 | 1.60e-03 | 1.0000 |
| openai/gpt-oss-120b | answer_changed | 50 | 0.0925 | 0.0200 | 0.0725 | 0.0255 | 0.1299 | 3.61e-03 | 0.8974 |
| openai/gpt-oss-20b | answer_changed | 42 | 0.1293 | 0.0238 | 0.1055 | 0.0459 | 0.1737 | 6.27e-04 | 0.8235 |
| qwen/qwen3.8-27b | answer_changed | 50 | 0.1110 | 0.0000 | 0.1110 | 0.0574 | 0.1756 | 2.55e-05 | 1.0000 |

## Per-operator effect on primary outcome (vs control)
| operator | family | n_pairs | mean_treatment | mean_diff_vs_control | ci_low | ci_high | p_holm | rank_biserial | cliffs_delta_vs_control | cliffs_magnitude |
|---|---|---|---|---|---|---|---|---|---|---|
| capitalization | surface | 250 | 0.0468 | 0.0441 | 0.0328 | 0.0560 | 1.91e-22 | 0.9385 | 0.4470 | medium |
| char_substitution | surface | 249 | 0.0606 | 0.0579 | 0.0446 | 0.0723 | 2.60e-29 | 0.9460 | 0.6039 | large |
| instruction_reordering | structural | 95 | 0.1210 | 0.1150 | 0.0879 | 0.1442 | 8.66e-15 | 0.9653 | 0.8004 | large |
| punctuation | surface | 249 | 0.0494 | 0.0467 | 0.0310 | 0.0640 | 2.13e-23 | 0.9128 | 0.4763 | large |
| random_edit | noise_control | 250 | 0.0909 | 0.0882 | 0.0680 | 0.1094 | 8.61e-35 | 0.9885 | 0.6852 | large |
| synonym | lexical | 170 | 0.0679 | 0.0648 | 0.0436 | 0.0881 | 5.33e-22 | 0.9900 | 0.5781 | large |
| whitespace | surface | 249 | 0.0616 | 0.0588 | 0.0451 | 0.0746 | 1.80e-29 | 0.9447 | 0.5888 | large |
| word_deletion | lexical | 244 | 0.0397 | 0.0369 | 0.0260 | 0.0498 | 3.79e-25 | 0.9370 | 0.4957 | large |
| word_insertion | lexical | 250 | 0.0623 | 0.0595 | 0.0466 | 0.0736 | 5.43e-30 | 0.9585 | 0.5830 | large |
| word_substitution | lexical | 114 | 0.0636 | 0.0596 | 0.0303 | 0.0945 | 2.04e-14 | 0.9437 | 0.5503 | large |

## Correctness flips by operator
| operator | n_pairs | c2i | i2c | any_flip_rate | ci_low | ci_high | net_accuracy_change | mcnemar_p_holm |
|---|---|---|---|---|---|---|---|---|
| capitalization | 250 | 3 | 5 | 0.0320 | 0.0120 | 0.0520 | 0.0080 | 1.0000 |
| char_substitution | 249 | 11 | 3 | 0.0562 | 0.0161 | 0.1084 | -0.0321 | 0.5737 |
| instruction_reordering | 95 | 5 | 1 | 0.0632 | 0.0105 | 0.1263 | -0.0421 | 1.0000 |
| punctuation | 249 | 5 | 5 | 0.0402 | 0.0200 | 0.0640 | 0.0000 | 1.0000 |
| random_edit | 250 | 18 | 8 | 0.1040 | 0.0480 | 0.1720 | -0.0400 | 0.6797 |
| synonym | 170 | 3 | 2 | 0.0294 | 0.0059 | 0.0529 | -0.0059 | 1.0000 |
| whitespace | 249 | 2 | 4 | 0.0241 | 0.0080 | 0.0440 | 0.0080 | 1.0000 |
| word_deletion | 244 | 1 | 5 | 0.0246 | 0.0082 | 0.0449 | 0.0164 | 1.0000 |
| word_insertion | 250 | 1 | 6 | 0.0280 | 0.0120 | 0.0480 | 0.0200 | 1.0000 |
| word_substitution | 114 | 0 | 4 | 0.0351 | 0.0087 | 0.0696 | 0.0351 | 1.0000 |

## Flip rates by model and condition
| model | condition | n_pairs | comparison_accuracy | c2i_mean | c2i_ci_low | c2i_ci_high | i2c_rate | any_flip_rate |
|---|---|---|---|---|---|---|---|---|
| allam-2-7b | control | 100 | 0.6000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| allam-2-7b | treatment | 425 | 0.6376 | 0.0471 | 0.0194 | 0.0839 | 0.0965 | 0.1435 |
| gemini-3.1-flash-lite | control | 100 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| gemini-3.1-flash-lite | treatment | 425 | 0.9906 | 0.0094 | 0.0000 | 0.0220 | 0.0000 | 0.0094 |
| openai/gpt-oss-120b | control | 100 | 0.9600 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| openai/gpt-oss-120b | treatment | 425 | 0.9459 | 0.0118 | 0.0023 | 0.0244 | 0.0000 | 0.0118 |
| openai/gpt-oss-20b | control | 100 | 0.9600 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| openai/gpt-oss-20b | treatment | 420 | 0.9357 | 0.0214 | 0.0071 | 0.0416 | 0.0000 | 0.0214 |
| qwen/qwen3.8-27b | control | 100 | 0.9800 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| qwen/qwen3.8-27b | treatment | 425 | 0.9600 | 0.0259 | 0.0094 | 0.0474 | 0.0047 | 0.0306 |
| ALL MODELS | control | 500 | 0.9000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ALL MODELS | treatment | 2120 | 0.8939 | 0.0231 | 0.0109 | 0.0391 | 0.0203 | 0.0434 |

## Model summary (treatment pairs)
| model | n | mean | ci_low | ci_high | answer_change_rate | flip_rate | c2i_rate | share_identical |
|---|---|---|---|---|---|---|---|---|
| allam-2-7b | 425 | 0.0963 | 0.0743 | 0.1200 | 0.5184 | 0.1435 | 0.0471 | 0.2400 |
| gemini-3.1-flash-lite | 425 | 0.0415 | 0.0305 | 0.0531 | 0.0800 | 0.0094 | 0.0094 | 0.2518 |
| openai/gpt-oss-120b | 425 | 0.0624 | 0.0403 | 0.0879 | 0.0965 | 0.0118 | 0.0118 | 0.3976 |
| openai/gpt-oss-20b | 420 | 0.0792 | 0.0514 | 0.1096 | 0.1793 | 0.0214 | 0.0214 | 0.4905 |
| qwen/qwen3.8-27b | 425 | 0.0338 | 0.0261 | 0.0421 | 0.1176 | 0.0306 | 0.0259 | 0.3365 |

## Anchor accuracy
| model | n | mean | ci_low | ci_high |
|---|---|---|---|---|
| allam-2-7b | 50 | 0.6000 | 0.4600 | 0.7400 |
| gemini-3.1-flash-lite | 50 | 1.0000 | 1.0000 | 1.0000 |
| openai/gpt-oss-120b | 50 | 0.9600 | 0.9000 | 1.0000 |
| openai/gpt-oss-20b | 50 | 0.9600 | 0.9000 | 1.0000 |
| qwen/qwen3.8-27b | 50 | 0.9800 | 0.9400 | 1.0000 |

## Task category summary (treatment)
| task_category | n | mean | ci_low | ci_high | flip_rate | answer_change_rate |
|---|---|---|---|---|---|---|
| classification | 415 | 0.0688 | 0.0500 | 0.0906 | 0.0337 | 0.1335 |
| code_generation | 449 | 0.0322 | 0.0255 | 0.0392 | 0.0379 | 0.0379 |
| logical_reasoning | 440 | 0.0841 | 0.0507 | 0.1209 | 0.0455 | 0.3552 |
| mathematical_reasoning | 441 | 0.0836 | 0.0573 | 0.1145 | 0.0567 | 0.2488 |
| question_answering | 375 | 0.0422 | 0.0260 | 0.0586 | 0.0427 | 0.2000 |

## Model pairwise (Wilcoxon, Holm)
| model_a | model_b | mean_a | mean_b | p_holm | rank_biserial |
|---|---|---|---|---|---|
| allam-2-7b | gemini-3.1-flash-lite | 0.0945 | 0.0407 | 0.0000 | 0.7678 |
| allam-2-7b | openai/gpt-oss-120b | 0.0945 | 0.0605 | 0.0914 | 0.4116 |
| allam-2-7b | openai/gpt-oss-20b | 0.0945 | 0.0764 | 0.7699 | 0.2194 |
| allam-2-7b | qwen/qwen3.8-27b | 0.0945 | 0.0338 | 0.0000 | 0.7443 |
| gemini-3.1-flash-lite | openai/gpt-oss-120b | 0.0407 | 0.0605 | 1.0000 | -0.1231 |
| gemini-3.1-flash-lite | openai/gpt-oss-20b | 0.0407 | 0.0764 | 0.6278 | -0.2502 |
| gemini-3.1-flash-lite | qwen/qwen3.8-27b | 0.0407 | 0.0338 | 1.0000 | 0.1482 |
| openai/gpt-oss-120b | openai/gpt-oss-20b | 0.0605 | 0.0764 | 0.3786 | -0.3245 |
| openai/gpt-oss-120b | qwen/qwen3.8-27b | 0.0605 | 0.0338 | 1.0000 | 0.1435 |
| openai/gpt-oss-20b | qwen/qwen3.8-27b | 0.0764 | 0.0338 | 0.4447 | 0.3012 |

## Control repeatability
| model | n_control_pairs | share_identical | mean_d_out_sem | max_d_out_sem | control_answer_change_rate | control_flip_rate |
|---|---|---|---|---|---|---|
| allam-2-7b | 100 | 0.9800 | 0.0000 | 0.0020 | 0.0000 | 0.0000 |
| gemini-3.1-flash-lite | 100 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| openai/gpt-oss-120b | 100 | 0.8300 | 0.0102 | 0.3774 | 0.0200 | 0.0000 |
| openai/gpt-oss-20b | 100 | 0.9500 | 0.0016 | 0.1407 | 0.0238 | 0.0000 |
| qwen/qwen3.8-27b | 100 | 0.8800 | 0.0019 | 0.0354 | 0.0000 | 0.0000 |

## Specification curve (ALL MODELS, treatment minus control)
| specification | metric | mean_diff | diff_ci_low | diff_ci_high | p_value |
|---|---|---|---|---|---|
| primary (all pairs) | d_out_sem | 0.0585 | 0.0477 | 0.0700 | 6.27e-41 |
| primary (all pairs) | d_out_char | 0.2017 | 0.1721 | 0.2329 | 1.74e-41 |
| primary (all pairs) | d_out_token | 0.2335 | 0.2035 | 0.2651 | 1.15e-40 |
| primary (all pairs) | answer_changed | 0.1624 | 0.1258 | 0.2016 | 1.41e-18 |
| exclude truncated/empty pairs | d_out_sem | 0.0582 | 0.0475 | 0.0696 | 6.73e-41 |
| exclude truncated/empty pairs | d_out_char | 0.2009 | 0.1715 | 0.2317 | 1.81e-41 |
| exclude truncated/empty pairs | d_out_token | 0.2325 | 0.2027 | 0.2642 | 1.19e-40 |
| exclude truncated/empty pairs | answer_changed | 0.1615 | 0.1249 | 0.2010 | 3.64e-18 |
| exclude high-risk operators (random_edit, char_substitution) | d_out_sem | 0.0542 | 0.0438 | 0.0658 | 9.54e-40 |
| exclude high-risk operators (random_edit, char_substitution) | d_out_char | 0.1957 | 0.1671 | 0.2261 | 9.05e-41 |
| exclude high-risk operators (random_edit, char_substitution) | d_out_token | 0.2243 | 0.1951 | 0.2560 | 2.15e-39 |
| exclude high-risk operators (random_edit, char_substitution) | answer_changed | 0.1526 | 0.1174 | 0.1908 | 1.13e-15 |
| exclude allam-2-7b (weakest instruction follower) | d_out_sem | 0.0494 | 0.0377 | 0.0626 | 1.58e-32 |
| exclude allam-2-7b (weakest instruction follower) | d_out_char | 0.1639 | 0.1332 | 0.1972 | 4.27e-33 |
| exclude allam-2-7b (weakest instruction follower) | d_out_token | 0.1956 | 0.1649 | 0.2289 | 3.06e-32 |
| exclude allam-2-7b (weakest instruction follower) | answer_changed | 0.0906 | 0.0540 | 0.1355 | 4.57e-12 |
| audit-valid only (exclude audited meaning-altering candidates and random_edit) | d_out_sem | 0.0523 | 0.0420 | 0.0637 | 1.16e-39 |
| audit-valid only (exclude audited meaning-altering candidates and random_edit) | d_out_char | 0.1921 | 0.1632 | 0.2229 | 9.38e-41 |
| audit-valid only (exclude audited meaning-altering candidates and random_edit) | d_out_token | 0.2212 | 0.1922 | 0.2531 | 1.73e-39 |
| audit-valid only (exclude audited meaning-altering candidates and random_edit) | answer_changed | 0.1448 | 0.1104 | 0.1817 | 8.62e-15 |

## Budgeted maxima
| budget_metric | epsilon | n_candidates_evaluated | mean_d_out_sem | max_observed_d_out_sem | argmax_pair | c2i_flips_within_budget |
|---|---|---|---|---|---|---|
| d_in_char | 0.0100 | 698 | 0.0528 | 0.6530 | allam-2-7b|CLASS-008|treatment|random_edit|1 | 20 |
| d_in_char | 0.0200 | 1053 | 0.0591 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|punctuation|1 | 37 |
| d_in_char | 0.0500 | 1456 | 0.0586 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|random_edit|1 | 40 |
| d_in_char | 0.1000 | 1731 | 0.0596 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|punctuation|1 | 42 |
| d_in_char | 1.0000 | 2120 | 0.0626 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|word_substitution|1 | 49 |
| d_in_sem | 0.0100 | 1311 | 0.0522 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|word_substitution|1 | 16 |
| d_in_sem | 0.0200 | 1571 | 0.0560 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|word_substitution|1 | 25 |
| d_in_sem | 0.0500 | 1865 | 0.0587 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|punctuation|1 | 35 |
| d_in_sem | 0.1000 | 2040 | 0.0610 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|word_substitution|1 | 45 |
| d_in_sem | 1.0000 | 2120 | 0.0626 | 0.7999 | openai/gpt-oss-120b|LOGIC-010|treatment|word_substitution|1 | 49 |

## Held-out operator selection (RQ5 proxy)
| model | chosen_operator | discovery_mean | validation_mean_chosen | validation_mean_random_edit | n_validation_prompts | p_value |
|---|---|---|---|---|---|---|
| allam-2-7b | whitespace | 0.1419 | 0.0906 | 0.1451 | 25 | 0.0279 |
| gemini-3.1-flash-lite | instruction_reordering | 0.0534 | 0.0601 | 0.0400 | 9 | 0.0547 |
| openai/gpt-oss-120b | instruction_reordering | 0.0886 | 0.1981 | 0.1263 | 9 | 0.9531 |
| openai/gpt-oss-20b | instruction_reordering | 0.2741 | 0.0871 | 0.1554 | 9 | 0.3125 |
| qwen/qwen3.8-27b | instruction_reordering | 0.0836 | 0.0964 | 0.0668 | 9 | 0.4609 |