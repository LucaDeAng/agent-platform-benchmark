# Evaluating AI agents and agent platforms: what the sources say (November 2026)

This note grounds the dimensions and the index in [scores.md](scores.md). It covers how agents
are evaluated, how buyers and analysts evaluate platforms, and how composite indices are built.
Sources, all accessed on 2026-11-08, are listed at the end. LLM agents found and summarised them;
the author chose what to keep. Section 4 draws the consequences.

## 1. Evaluating the agent

**Task success with simulated users, and pass^k.** τ-bench [1] has an LLM play the customer while
the agent works with domain tools and a written policy. Success is judged on the final database
state, compared with an annotated goal. It also introduced pass^k: the probability that *all* k
independent trials of the same task succeed. pass@k is the probability that at least one succeeds.
Customer-facing agents need consistency: a 75% per-trial success rate falls to roughly 42% for
three passes in a row [4]. In τ-bench, gpt-4o solved fewer than half the tasks, with pass^8 in
retail below 25%.

**Fidelity of the simulated user.** τ²-bench [2] lets the user act on a shared environment too, as in
technical support, and constrains the simulator through tools and observable state. Agents score
noticeably lower when they have to guide a user than when they act alone.

**Faults and channel conditions.** τ-Voice [3] runs the same kind of tasks over full-duplex voice,
with accents, background noise and turn-taking. One frontier model reaches about 85% in text. Voice
agents reach 31–51% in clean audio and 26–38% in realistic audio. EVA-Bench [21], from ServiceNow
AI Research, scores voice agents on two composites: EVA-A (accuracy: task completion, faithfulness,
speech fidelity) and EVA-X (experience: progression, conciseness, turn-taking). It uses bot-to-bot
audio conversations, with automatic checks that regenerate conversations when the simulated user
errs. None of the 12 systems tested exceeds 0.5 on both composites. Full-Duplex-Bench [19] isolates
pause handling, backchannels, turn-taking and interruptions. For voice deployments, text scores are
not a proxy.

**Safety and policy violations.** A task that ends in the right state can still have broken the
policy along the way. Cao et al. [5] re-scored τ-bench runs with procedure-aware gating: 27–78% of
reported successes hid policy or integrity violations, and gating changed model rankings. CRAFT and
τ-break [6] show that policy-aware adversarial users push agents into violations that simple
defences do not stop. Violation rate should be measured separately from success, and used as a gate.

**Handoff and escalation.** τ-bench domain policies include a transfer-to-human tool and a rule for
when it may be used [7], so escalation is part of the graded behaviour. Our searches found no
dedicated public benchmark for escalation quality. A useful evaluation counts both missed and
premature escalations, and checks what context reaches the human.

**Calibration.** The word has two meanings here.

- *Judge calibration.* An LLM grader has to agree with humans. Zheng et al. [8] found GPT-4
  agreeing with human preferences over 80% of the time, about as often as humans agree with each
  other. They also documented position, verbosity and self-enhancement biases. Anthropic [4]
  recommends checking model graders against human experts and giving them an "unknown" option.
- *Confidence calibration.* Whether stated confidence matches accuracy. HELM [9] lists it among its
  seven core metrics. Rabanser, Kapoor et al. [20] split agent reliability into four dimensions
  (consistency, robustness, predictability, safety) measured by twelve metrics. Across 15 models,
  they find that capability gains have brought only small reliability gains.

**Latency and cost per resolved contact.** Kapoor et al. [10] show that accuracy-only leaderboards
reward expensive designs; they argue for accuracy–cost Pareto curves. HAL [11] ran 21,730 rollouts
across 9 models and 9 benchmarks, with cost tracked. In a contact centre the equivalent figure is
total cost divided by resolved contacts, with "resolved" defined by the buyer. Several platforms
publish a per-resolution billing unit (`pricing_model` in the results), which makes the vendor's
definition of resolution part of the contract.

**In production.** The NIST AI RMF MEASURE function [12] asks for documented test sets and metrics
(2.1), performance shown under deployment-like conditions (2.3), monitoring in production (2.4),
safe failure (2.6), and assessors independent of the developers (1.3).

**EU transparency rules.** Article 50 of the AI Act [13] has applied since 2 August 2026 [22, 23].

- Article 50(1) requires that people be told when they interact with an AI system, unless that is
  obvious.
- Article 50(2) requires machine-readable marking of synthetic audio, which matters for voice agents.
  Systems placed on the market before 2 August 2026 have until 2 December 2026.
- The Digital Omnibus on AI (Regulation (EU) 2026/1744) [24] replaced only Article 50(7) and set
  that deadline in Article 111(4). It left Article 50(1) unchanged.
- The Commission adopted guidelines on Article 50, and the AI Office published a voluntary Code of
  Practice on the transparency of AI-generated content, both in July 2026 [22, 23].

## 2. How buyers and analysts evaluate platforms

**Analyst rubrics.** In Forrester's published Wave methodology [14], the analyst chooses
differentiating criteria and assigns weights. Evidence comes from vendor questionnaires, briefings
and demos, and references that the vendor supplies. Vendors can be assessed without participating.

**Public procurement.** EU Directive 2014/24/EU [15], Article 67(5), requires buyers to publish the
relative weight of each award criterion in advance. Where weighting is not possible, they publish
the criteria in order of importance. Recital 45 says that criteria and weights must not change
during the procedure.

**Known weaknesses.**

- *Weights are value judgements.* The OECD/JRC Handbook [16] says so explicitly. In a weighted sum
  they act as trade-off rates, not as importance coefficients. Paruolo, Saisana and Saltelli [17]
  show that, once indicators are correlated, the declared importance of an indicator can differ
  sharply from its actual influence on the index.
- *Evidence supplied by the vendor.* Questionnaires and vendor-chosen references come from the party
  being assessed. This benchmark has the same limit: every cell is vendor-published.
- *Missing data treated as zero.* A non-response or a gated document scored as "absent" penalises
  silence as if it were a gap. The Handbook [16] warns that imputation can make users believe the
  data are complete. Data that are missing not at random, and here missingness follows gated docs
  and uneven search, need explicit modelling, which is hard to justify.

## 3. Composite indices: the OECD/JRC Handbook

The Handbook [16] sets out ten steps: (1) theoretical framework, (2) data selection, (3) imputation
of missing data, (4) multivariate analysis, (5) normalisation, (6) weighting and aggregation,
(7) uncertainty and sensitivity analysis, (8) back to the data, (9) links to other indicators,
(10) visualisation. The points that matter here:

- **Normalisation.** Options include ranking, z-scores, min-max, distance to a reference and
  categorical scales. Categorical scales suit qualitative data, at the cost of detail.
- **Weighting.** Equal weighting is common, but it is a choice, not the absence of weights. Equal
  weights on indicators give unequal weights to dimensions that hold different numbers of
  indicators, and the reverse.
- **Aggregation.** Linear aggregation is fully compensatory: a surplus in one dimension offsets a
  deficit in another. Geometric aggregation is less compensatory.
- **Uncertainty and sensitivity analysis.** Inputs to vary: including or excluding indicators, the
  imputation scheme, the normalisation, the weights, the aggregation. Results are reported as ranks
  with uncertainty bounds rather than as point ranks. Saisana, Saltelli and Tarantola [18] present
  this as a quality test for whether a ranking can be defended.

## 4. Design choices this implies for the benchmark

1. **What is measured.** The benchmark cannot measure pass^k, violation rates or latency: no product
   was tested. It can record whether a platform documents the tooling a buyer needs to measure them
   (simulated users, regression suites, repeated trials, LLM judges and their calibration,
   production QA). That becomes one dimension, *Evaluation and quality assurance*.
2. **Framework before data (step 1).** The three dimensions answer three buyer questions: can I
   measure it, can I run it under control, can it reach my customers in Europe. Each criterion
   belongs to exactly one dimension.
3. **Normalisation.** A categorical scale written down before scoring, as procurement rules require
   for weights [15]: documented 1; vendor states 0.5 to 1. The scale is monotone, so publishing more
   never lowers a bound. The first version broke this (METHOD.md, change 8).
4. **Missing data: partial-identification bounds.** Missingness is not random, so each score is the
   pair of worst-case and best-case values (Manski [25]). Unknown cells count 0 and 1, claims 0.5 and
   1, and coverage is reported. Without an assumption about why documentation is missing, these
   bounds are the narrowest statement the data support. They make the effect of the missing data
   visible instead of hiding it [16]. Here every upper bound is 1, so the floor and the coverage
   carry the information.
5. **Weights.** Equal weights across dimensions by default, stated as a value judgement, with the
   implied criterion weights published.
6. **Aggregation.** Linear, for transparency. Because it is compensatory, dimension scores are
   always shown next to the index.
7. **Sensitivity (step 7).** Alternative weights, alternative values for vendor claims,
   leave-one-criterion-out runs, and the width of the rank interval that the missing data allows.
8. **Ranking.** A ranking rule was fixed in advance. Absolute ranks are never published, only how
   wide each platform's rank interval is.
9. **Not done, and why.**
   - No Monte Carlo imputation: there is no defensible distribution for an unknown cell.
   - No multivariate weighting (step 4): 17 platforms with near-binary data give unstable
     correlations.
   - No geometric aggregation: lower bounds can be 0.

## Sources (all accessed 2026-11-08)

1. Yao, Shinn, Razavi, Narasimhan. *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*. arXiv:2406.12045, 2024. https://arxiv.org/abs/2406.12045
2. Barres, Dong, Ray, Si, Narasimhan. *τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment*. arXiv:2506.07982, 2025. https://arxiv.org/abs/2506.07982
3. Ray, Dhandhania, Barres, Narasimhan. *τ-Voice: Benchmarking Full-Duplex Voice Agents on Real-World Domains*. arXiv:2603.13686, 2026. https://arxiv.org/abs/2603.13686
4. Anthropic. *Demystifying evals for AI agents* (engineering guide), 9 January 2026. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
5. Cao, Driouich, Thomas. *Beyond Task Completion: Revealing Corrupt Success in LLM Agents through Procedure-Aware Evaluation*. arXiv:2603.03116, 2026. https://arxiv.org/abs/2603.03116
6. Nakash et al. *Effective Red-Teaming of Policy-Adherent Agents*. arXiv:2506.09600, 2025. https://arxiv.org/abs/2506.09600
7. sierra-research/tau2-bench, airline domain policy. https://raw.githubusercontent.com/sierra-research/tau2-bench/main/data/tau2/domains/airline/policy.md
8. Zheng et al. *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685, 2023. https://arxiv.org/abs/2306.05685
9. Liang et al. *Holistic Evaluation of Language Models*. arXiv:2211.09110, 2022. https://arxiv.org/abs/2211.09110
10. Kapoor, Stroebl, Siegel, Nadgir, Narayanan. *AI Agents That Matter*. arXiv:2407.01502, 2024. https://arxiv.org/abs/2407.01502
11. Kapoor et al. *Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation*. arXiv:2510.11977, 2025. https://arxiv.org/abs/2510.11977 ; project site https://hal.cs.princeton.edu/
12. NIST. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, January 2023, MEASURE function. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
13. Regulation (EU) 2024/1689 (AI Act), Article 50(1). https://eur-lex.europa.eu/eli/reg/2024/1689/oj
14. Forrester. *The Forrester Wave Methodology*. https://www.forrester.com/policies/forrester-wave-methodology/
15. Directive 2014/24/EU on public procurement, Article 67(5) and recital 45. https://eur-lex.europa.eu/eli/dir/2014/24/oj
16. OECD and European Commission JRC (Nardo, Saisana, Saltelli, Tarantola, Hoffmann, Giovannini). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD, 2008; steps p. 20, normalisation p. 27–30, weighting and aggregation p. 31–33, uncertainty and sensitivity p. 34–35, imputation p. 24–25. https://knowledge-for-policy.ec.europa.eu/sites/default/files/jrc47008_handbook_final.pdf
17. Paruolo, Saisana, Saltelli. *Ratings and rankings: voodoo or science?* Journal of the Royal Statistical Society A 176(3), 2013, 609–634. Preprint: https://arxiv.org/abs/1104.3009
18. Saisana, Saltelli, Tarantola. *Uncertainty and sensitivity analysis techniques as tools for the quality assessment of composite indicators*. Journal of the Royal Statistical Society A 168(2), 2005, 307–323. https://econpapers.repec.org/RePEc:bla:jorssa:v:168:y:2005:i:2:p:307-323
19. Lin et al. *Full-Duplex-Bench: A Benchmark to Evaluate Full-duplex Spoken Dialogue Models on Turn-taking Capabilities*. arXiv:2503.04721, 2025. https://arxiv.org/abs/2503.04721
20. Rabanser, Kapoor, Kirgis, Liu, Utpala, Narayanan. *Towards a Science of AI Agent Reliability*. arXiv:2602.16666, 2026. https://arxiv.org/abs/2602.16666
21. Bogavelli et al. (ServiceNow AI Research). *EVA-Bench: A New End-to-end Framework for Evaluating Voice Agents*. arXiv:2605.13841, 2026. https://arxiv.org/abs/2605.13841
22. Houthoff. *AI Act transparency obligations and the AI Omnibus Regulation*, 1 September 2026 (law-firm summary). https://www.houthoff.com/insights/news/ai-act-transparency-obligations-and-the-ai-omnibus-regulation/
23. Baker Botts. *EU AI Act Article 50 transparency obligations go live*, 10 September 2026 (law-firm summary). https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live
24. Regulation (EU) 2026/1744 (Digital Omnibus on AI), 8 July 2026: amendment of Article 50(7) and new Article 111(4). https://eur-lex.europa.eu/eli/reg/2026/1744/oj
25. Manski. *Anatomy of the Selection Problem*. Journal of Human Resources 24(3), 1989, 343–360. https://ideas.repec.org/a/uwp/jhriss/v24y1989i3p343-360.html
