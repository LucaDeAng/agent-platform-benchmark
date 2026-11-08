# Method

Written on 2026-11-08, before any evidence was collected. Changes made after collection started are
listed at the bottom with the reason.

## Question

What do the public documents of voice and chat AI agent platforms for enterprise customer service say,
as of November 2026, about the capabilities a deployment lead has to check before choosing one?

This is a benchmark of **public documentation**, not of the products. A capability that is not found
in public pages may still exist (behind a login, in a sales deck, in a private beta). A capability
that is documented has not been tested by us. Nothing here was verified hands-on.

## Scope and rules

- Sources: vendor product documentation, help centres, API references, developer docs, trust and
  security centres, pricing pages, legal pages (DPA, sub-processor lists), vendor blogs and press
  releases, and reputable press (press is used only for the inclusion rule, never for a capability).
- Not used: anything behind a login, paywalled analyst reports, forms, demos, trials, accounts,
  contact with vendors, pages disallowed by robots.txt.
- Access date of every row is recorded. Public pages change; the dataset is a snapshot.
- No prices are reproduced, only the billing unit a vendor publishes.
- Tooling: evidence collection, the gap pass and the re-verification were carried out by LLM agents
  with web-search and page-fetch tools, under the author's supervision. The author wrote the rubric,
  reviewed the agents' reports and decided borderline cases. The re-verification therefore uses the
  same kind of tooling as the collection and is not an independent audit.

## Entity selection rule

Candidate list: vendors commonly evaluated for enterprise customer-service AI agents, written by the
author before collection (the 18 names in the table below). A candidate is **included** if it meets
all of A, B and at least one of C:

- **A. Product.** It sells an AI agent that holds customer-service conversations autonomously in voice
  or chat (not only agent-assist, not only a raw model or telephony API).
- **B. Public docs.** It has product documentation or a help centre readable without a login.
  (Relaxed after collection started; see "Changes after collection started".)
- **C. Market-presence signal** (at least one, with a public URL recorded in `data/platforms.csv`):
  - C1. The product belongs to a publicly listed company or to a subsidiary of one.
  - C2. Disclosed equity funding, or a disclosed acquisition price, of at least USD 20 million in a
    vendor press release or reputable press.
  - C3. The product is part of a hyperscaler or CRM suite (cloud provider, CRM or CCaaS suite).

Candidates: Sierra, Decagon, Parloa, PolyAI, ElevenLabs Agents, Cognigy (NICE), Kore.ai, Genesys
Cloud AI, Google Customer Engagement Suite, Amazon Connect, Microsoft Copilot Studio / Dynamics 365
Contact Center, Salesforce Agentforce, Intercom Fin, Zendesk AI agents, Ada, Retell AI, Vapi,
LivePerson.

Disclosure: the USD 20 million threshold in C2 was set while drafting this rule, after the author had
already looked up the funding of Vapi (USD 20 million Series A, December 2024) and Retell AI (a
USD 4.6 million seed round in 2024; no later round found). The threshold therefore was not blind to
those two cases. Under it, Vapi is included and Retell AI is excluded; the check is in
`data/platforms.csv`.

Where a vendor sells several products, the entity is the vendor's customer-service AI agent offering
as a whole (e.g. Microsoft = Copilot Studio + Dynamics 365 Contact Center; Google = Customer Engagement
Suite including Conversational Agents / Dialogflow CX). Evidence from any of those products counts.

## Criteria

Each (platform, criterion) cell gets one **status**:

| Status | Meaning |
|---|---|
| `documented` | Stated in product documentation, help centre, API reference, trust/security centre, pricing page or legal page (pages that describe how the feature is configured, or a contractual/compliance fact). |
| `vendor_states` | Stated only on marketing pages, blog posts, press releases or announcements. Reported as "vendor states", not as a verified capability. |
| `not_found` | Not found with the search procedure below. Means unknown, **not** absent. |
| `not_applicable` | The criterion depends on another one that is not found (rules below). Set by the script, not by hand. |

Everything in this dataset is vendor-published. Even `documented` means "the vendor documents it",
not "it works as described". Certifications listed on a trust centre were not checked against
auditor reports.

Some cells also carry a short **value** (e.g. which messaging channels, which billing unit).

| ID | Criterion | `documented` / `vendor_states` when the source says... | Value |
|---|---|---|---|
| `ch_voice` | Voice channel | The AI agent handles phone or voice conversations. | — |
| `ch_chat` | Chat channel | The AI agent handles web or in-app chat. | — |
| `ch_email` | Email channel | The AI agent answers email or email tickets. | — |
| `ch_messaging` | Messaging channels | The AI agent works on at least one messaging channel (WhatsApp, SMS, Messenger, Apple Messages, RCS, etc.). | channels named |
| `tel_native` | Native telephony | Phone numbers / PSTN can be provisioned within the platform (including via an embedded partner the platform bills for). | — |
| `tel_byoc` | Bring your own carrier | SIP trunk, BYOC, or connection to the customer's carrier or existing contact-centre telephony. | — |
| `lang_it` | Italian | Italian is listed as a supported conversation language in the vendor's own pages. | scope (chat / voice) if stated |
| `lang_eu` | Other EU languages | A supported-languages list includes at least 5 EU official languages other than Italian. | count of the 24 EU official languages listed |
| `tools_api` | Tools via APIs | The agent can call customer-defined APIs, functions or webhooks during a conversation. | — |
| `tools_mcp` | MCP | The agent can use tools exposed by Model Context Protocol servers (client), or the vendor exposes its platform as an MCP server. | `client`, `server` or both |
| `eval_sim` | Simulated users | Test conversations with simulated (LLM-driven) customers. | — |
| `eval_regression` | Regression suites | Saved test cases or suites re-run against agent versions, with pass/fail. | — |
| `eval_repeat` | Repeated trials | The same test is run several times and a consistency or pass-rate-over-trials metric is reported (pass^k or similar). | — |
| `eval_judge` | LLM judge | An LLM or AI grader scores conversations against criteria (in testing or QA). | — |
| `eval_judge_cal` | Judge calibration | The vendor documents checking or tuning the AI grader against human labels or human review. | — |
| `obs_qa` | Observability and QA | Conversation transcripts or traces plus analytics, and/or automated QA scoring of conversations. | elements named |
| `handoff` | Human handoff with context | Escalation to a human agent passes context (transcript, summary or collected data). | what is passed |
| `aicaller` | AI callers / declared agents | Detection of AI or synthetic-voice callers, or support for a protocol through which a customer's own AI agent declares itself (PAP, PACT or similar). Answering-machine detection for outbound calls does **not** count. | mechanism |
| `residency_eu` | EU data residency | Customer data can be hosted or processed in an EU region. | — |
| `cert_iso27001` | ISO/IEC 27001 | Listed as held (not "in progress"). | — |
| `cert_soc2` | SOC 2 | SOC 2 (Type I or II) listed as held. | type |
| `aiact` | EU AI Act posture | A vendor page addresses the EU AI Act specifically (approach, role, transparency features). Generic "responsible AI" pages do not count. | — |
| `pricing_model` | Public pricing model | A public page states the billing unit. "Contact sales" alone is `not_found`. | `per_minute`, `per_resolution`, `per_conversation`, `per_message`, `per_seat`, `usage_credits`, `platform_fee`, `contact_sales_only` |
| `deploy_model` | Deployment model | Vendor pages describe a self-serve sign-up, a vendor-led deployment team (forward-deployed / professional services / agent engineers), or both. | `self_serve`, `vendor_led`, `both`, `partner_led` |

`not_applicable` rules, applied by the script: `tel_native` and `tel_byoc` are not applicable when
`ch_voice` is `not_found`; `eval_judge_cal` is not applicable when `eval_judge` is `not_found`.

## Search procedure (identical for every platform)

1. Record the vendor's documentation root, trust/security page and pricing page, if public.
2. For each criterion, run up to **2 web searches** with the template `<vendor product> <keywords>`
   (keywords below), optionally restricted to the vendor's domains, and fetch up to **3 vendor pages**.
   Prefer documentation over marketing.
3. Record the best source: if a documentation page supports the criterion, `documented`; if only
   marketing/blog/press pages do, `vendor_states`; otherwise `not_found` with the queries tried in the
   note.
4. The note is a short paraphrase (no long quotes) of what the page says.

| Criterion | Keywords |
|---|---|
| channels | `voice`, `chat`, `email`, `WhatsApp SMS messaging channels` |
| telephony | `phone numbers`, `SIP trunk`, `BYOC`, `telephony integration` |
| languages | `supported languages`, `Italian` |
| tools | `function calling`, `API actions`, `tools`, `MCP`, `Model Context Protocol` |
| evaluation | `simulation`, `simulated conversations`, `test cases`, `regression`, `evaluation`, `LLM judge` |
| observability | `analytics`, `transcripts`, `quality assurance`, `monitoring` |
| handoff | `handoff`, `escalation`, `transfer to human agent` |
| AI callers | `AI agent detection`, `synthetic voice detection`, `personal agent`, `PAP`, `PACT` |
| compliance | `trust center`, `SOC 2`, `ISO 27001`, `data residency EU`, `EU AI Act` |
| pricing / deployment | `pricing`, `forward deployed`, `professional services`, `sign up` |

## Re-verification

After collection, the script draws a random 10% of all cells (fixed seed `20261108`). Each sampled
cell is re-checked: cells with a URL by refetching that URL and judging whether it still supports the
recorded status; `not_found` cells by re-running one standard query. Results go to
`data/reverification.csv`; the script reports the agreement rate.

## Dimension scores and synthetic index

Added on 2026-11-08, after evidence collection had finished. The rules in this section were
written and committed **before any dimension or index score was computed**, but they are **not
blind to the cell-level data**: the full status matrix was already public in `docs/results.md`. The
reasoning behind the choices is in [docs/evaluating-agents.md](docs/evaluating-agents.md).

### Three dimensions

Each of the 24 criteria belongs to exactly one dimension. The mapping is the `dimension_id` column of
`data/criteria.csv`, and the dimensions are defined in `data/dimensions.csv`.

| Dimension | Question it answers | Criteria (n) |
|---|---|---|
| `eval_qa` Evaluation and quality assurance | Can a buyer measure the agent's quality before and after go-live with the vendor's own tooling? | `eval_sim`, `eval_regression`, `eval_repeat`, `eval_judge`, `eval_judge_cal`, `obs_qa` (6) |
| `prod_gov` Production and governance readiness | Can the agent be integrated, escalated, secured and contracted under jurisdiction-neutral enterprise controls? | `tools_api`, `tools_mcp`, `handoff`, `aicaller`, `cert_iso27001`, `cert_soc2`, `pricing_model`, `deploy_model` (8) |
| `voice_eu` Voice, channels and European fit | Can the agent reach European customers on the channels and languages they use, under EU-specific data and AI rules? | `ch_voice`, `ch_chat`, `ch_email`, `ch_messaging`, `tel_native`, `tel_byoc`, `lang_it`, `lang_eu`, `residency_eu`, `aiact` (10) |

Why these three:

- The starting proposal (evaluation and QA; production and governance; voice and European fit) was
  kept, because it matches the three questions the study identifies for a deployment lead: can I
  measure it, can I run it under control, can it serve my customers. The study did not find a
  better-founded split for criteria that record only whether something is documented.
- `obs_qa` sits in `eval_qa`, not in production: production monitoring is the post-launch half of
  evaluation (NIST AI RMF, MEASURE 2.4; see the study).
- `handoff` and `aicaller` sit in `prod_gov`: they are controls on how a live agent fails safely or
  meets an unexpected counterpart. The criteria record whether the feature exists, not how good the
  escalation is, so they are not evaluation criteria.
- `residency_eu` and `aiact` sit in `voice_eu`, not in `prod_gov`. The rule: a requirement specific
  to serving customers in the EU goes to `voice_eu`; a control that applies in any jurisdiction
  (ISO 27001, SOC 2) goes to `prod_gov`.
- `pricing_model` and `deploy_model` sit in `prod_gov` as commercial transparency: a published
  billing unit lets a buyer estimate cost per resolved contact, and a stated deployment model says
  who does the work. Neither says anything about product quality.
- `voice_eu` also contains chat, email and messaging: it is about reach, with voice and EU
  requirements as the part this benchmark adds.

### Level-to-value table

Each cell's status becomes a value between 0 and 1. A cell without evidence has no single value: it
gets a lower and an upper value.

| Status | Lower value | Upper value | Why |
|---|---|---|---|
| `documented` | 1 | 1 | The vendor documents the capability in product docs, trust, pricing or legal pages. |
| `vendor_states` | 0.5 | 0.5 | The vendor claims it on marketing, blog or press pages only. A buyer cannot check configuration or scope from public documentation. |
| `not_found` | 0 | 1 | Unknown. The lower bound assumes the capability is absent, the upper bound assumes it is documented. |
| `not_applicable` | 0 | 1 | Unknown, because the parent criterion (voice channel, LLM judge) was not found. Treated like `not_found`. |

Only the status is scored. Recorded values (which channels, which billing unit, voice-only Italian,
and so on) are not scored; every criterion uses the same table. The value 0.5 for `vendor_states`
is a judgement, so the sensitivity analysis also runs it at 0 and at 1.

### Dimension scores, ranges and coverage

For each platform and dimension:

- **lower bound** = mean of the criteria's lower values (`not_found` counts as 0);
- **upper bound** = mean of the criteria's upper values (`not_found` counts as 1);
- **coverage** = share of the dimension's cells with evidence (`documented` or `vendor_states`).

By construction, upper minus lower = 1 − coverage. A score is always reported as a range, never as a
single number. No midpoint is published, because a midpoint would amount to imputing 0.5 to every
unknown cell.

### Synthetic index

- **Default:** weighted arithmetic mean of the three dimension scores with equal weights (1/3 each),
  computed separately for the lower and the upper bound. Index coverage = the same weighted mean of
  the dimension coverages, so that index upper − lower = 1 − index coverage. The raw number of cells
  with evidence (out of 24) is reported alongside.
- Equal weights across dimensions mean unequal weights across criteria: each `eval_qa` criterion
  weighs 1/18, each `prod_gov` criterion 1/24 and each `voice_eu` criterion 1/30 of the index.
- Linear aggregation is compensatory: a high score in one dimension offsets a low score in another.
  Weights are trade-offs, not measures of importance (OECD/JRC Handbook, p. 31–33).

### Sensitivity analysis

All scenarios are computed for both the lower and the upper bound:

1. **Weightings** (dimension weights `eval_qa` / `prod_gov` / `voice_eu`): equal 1/3 each (default);
   evaluation-heavy 1/2, 1/4, 1/4; governance-heavy 1/4, 1/2, 1/4; EU-heavy 1/4, 1/4, 1/2;
   criterion-equal 6/24, 8/24, 10/24 (every criterion weighs 1/24).
2. **Value table:** `vendor_states` = 0 and `vendor_states` = 1, with equal weights.
3. **Leave one criterion out:** each of the 24 criteria dropped in turn, equal weights, the dimension
   score being the mean of its remaining criteria.

Ranks use competition ranking: rank = 1 + the number of platforms with a strictly higher score, so
tied platforms share a rank. For each platform the script reports its rank range (best and worst
rank) across scenarios, separately for lower-bound and upper-bound scores, and the most influential
criteria in the leave-one-out runs.

**Possible rank under missing data.** With the default weights, a platform's best possible rank is
reached when its unknown cells are all 1 and every other platform's are all 0, and its worst possible
rank in the opposite case: best = 1 + the number of platforms whose lower bound exceeds its upper
bound; worst = 1 + the number of platforms whose upper bound exceeds its lower bound.

### When a ranking is shown, and bands otherwise

A ranked list of platforms by index is published only if **both** hold:

- (a) fewer than half of all platform pairs have overlapping default index ranges (two ranges
  overlap unless one's lower bound exceeds the other's upper bound); and
- (b) every platform's rank range across the sensitivity scenarios spans at most 3 positions (best
  and worst rank differ by at most 2), for lower-bound and for upper-bound ranks alike.

Otherwise `docs/scores.md` lists platforms alphabetically with their ranges and assigns **bands**
by interval dominance on the default index. Platform B dominates platform A when B's lower bound
exceeds A's upper bound. Band 1 holds the platforms that no platform dominates; band 2 the platforms
dominated only by band-1 platforms; and so on. A band says which platforms the public evidence can
separate. It is not a quality grade, and platforms within a band are not ordered.

## Limits

- Public visibility is not capability, and absence from public pages is not absence.
- Large suites have far more documentation than start-ups; a start-up that documents less is not
  necessarily less capable. Counts reward documentation, not product quality.
- Pages were read through an automated fetch-and-summarise tool; a cell may be wrong where the tool
  misread a page. The re-verification sample estimates that error rate.
- The web search used is US-located; EU-specific pages may rank lower.
- The candidate list is the author's; the inclusion rule filters it but does not generate it, so the
  benchmark is not exhaustive.

## Changes after collection started

All decided on 2026-11-08 after the first collection pass, i.e. **not blind** to the data.

1. **Rule B relaxed.** As written, rule B excluded Sierra, Decagon and Parloa: their product
   documentation requires a login (docs.sierra.ai, docs.decagon.ai, the Parloa AMP and developer
   docs), and no public help centre was found. Excluding three of the most-discussed vendors would make
   the benchmark less useful to its readers, so B now reads: *the vendor publishes product pages,
   documentation or a help centre readable without a login*. Whether the product documentation itself
   is public is recorded in the new `public_docs` column of `data/platforms.csv` (`yes`, `partial`,
   `no`). For vendors with `public_docs = no`, most cells can only be `vendor_states` or `not_found`;
   that reflects where they publish, not what their products do.
2. **Search budget: the search procedure was not applied evenly.** The web-search tool has a
   per-session cap (200 calls, refilling at about 100 per hour) that was reached during the first
   pass. Each platform's coverage is recorded in the `search_coverage` column of `data/platforms.csv`:
   - `full` (web searches available for every cell): Sierra, Cognigy, Intercom, Microsoft, Google, ElevenLabs.
   - `partial` (searches ran out part-way): Decagon, Vapi, Amazon Connect, Salesforce, Zendesk.
   - `none` (no web searches): Parloa, PolyAI, Kore.ai, LivePerson, Genesys, Ada.

   Platforms without full coverage were collected from vendor documentation indexes (`llms.txt`,
   sitemaps, public help-centre search APIs) and direct page fetches. A **gap pass** then re-checked
   every `not_found` cell of every platform the same way (indexes and direct fetches), and applied the
   coding rules below; it changed 17 cells. Standard web searches, meant to give every remaining `not_found`
   cell one search, reached only 8 cells (7 Sierra, 1 Decagon) across the gap pass and a follow-up
   sweep before the cap was hit again; none of them found a vendor page. Notes record which of these steps touched
   each cell. Consequence: a `not_found` on a platform with `search_coverage` `partial` or `none` rests
   on a narrower search than one on a `full` platform.
3. **Coding rules made explicit** after the collectors raised borderline cases, applied to all
   platforms in the gap pass:
   - `aiact`: counts only if the page states the vendor's own approach, role or measures regarding the
     EU AI Act (company-wide pages count and are labelled as such). A badge, a line in a certificate
     list, or a page that only explains the law is `not_found`, with the badge mentioned in the note.
   - `residency_eu`: needs a statement that customer data is stored or processed in an EU region, data
     centre or instance. An EU API endpoint alone is `not_found`, mentioned in the note.
   - `eval_judge_cal`: needs a page saying the AI grader is compared with, or tuned against, human
     judgment: guidance telling users to do it, a feature that measures AI-human agreement, or the
     vendor stating that it validates its own grader with human labels. "Review results and refine
     criteria" alone is `not_found`.
   - `eval_repeat`: needs the same test run several times **and** a result reported across the runs
     (pass count over iterations, pass rate, majority vote, consistency score). "Tests can be re-run",
     or variations of a scenario, is `not_found`.
   - `aicaller`: agent-to-agent (A2A) endpoints alone, and answering-machine detection, do not count.
   - `cert_iso27001`: "aligned with ISO 27001" is not a certification and is `not_found`.
4. **Re-verification of `not_found` cells.** The plan was to re-run one standard query for each
   sampled `not_found` cell. Because the search cap had been reached again, 1 of the 10 sampled
   `not_found` cells was re-checked with a web search and 9 by direct fetch of vendor pages.
5. **Per-platform raw files removed.** Collection used one file per platform (`data/raw/`, visible in
   the git history); after the gap pass they were merged into `data/evidence.csv`, which is the only
   canonical data file. Corrections from re-verification were made there directly.
6. **Changes after an external review (2026-11-08).**
   - `parloa,residency_eu`: `not_found` to `vendor_states` (Parloa Labs post of 1 Oct 2026: the
     app.parloa.com stamp is hosted in Germany). A Parloa FAQ quoted by the reviewer on regional data
     centres could not be confirmed in the fetched page text, so it is not cited.
   - `parloa,deploy_model`: `partner_led` to `vendor_led;partner_led` (FAQ: Parloa engineers, success
     teams and partners guide rollout).
   - `elevenlabs,aiact`: `documented` to `not_found` under the `aiact` rule (a use policy that only
     bans prohibited uses and leaves compliance to the customer states no vendor posture).
   - Every remaining `not_found` cell of Parloa (6) and PolyAI (4) received one standard web search
     (one query covered both Parloa language cells); none found a vendor page that could be read. A
     Parloa docs page on supported languages appeared in the results but returns an error page, so it
     was not counted.
   - Names: "Fin (formerly Intercom)" (renamed 12 May 2026; acquired by Salesforce, completed
     10 Sep 2026, so its inclusion signal is now C1), "ElevenAgents (ElevenLabs)", "Google Gemini
     Enterprise for CX (formerly Customer Engagement Suite)". Platform IDs are unchanged.
   - Wording and minor value fixes: protocol status written as "in development" (PAP) and
     "specification in progress" (PACT); Sierra pricing adds `per_conversation`; Zendesk regression
     cites the conversation-simulator page.
   - The results table now reports, per criterion, how many `not_found` cells are on platforms with
     `partial` or `none` search coverage.
7. **Dimension scores and synthetic index added (2026-11-08).** Three dimensions, a level-to-value
   table, score ranges, an equal-weight index and a sensitivity analysis were added after collection
   (section "Dimension scores and synthetic index" above). The rules were committed before any
   dimension or index score was computed, in a separate commit, but with the cell-level matrix
   already known. No evidence cell was changed for this step.
