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
2. **Search budget.** The web-search tool has a per-session cap that was reached during the first
   pass, after roughly two-thirds of the platforms. Platforms collected later (all or part of Decagon,
   Parloa, PolyAI, Vapi, Kore.ai, LivePerson, Genesys, Amazon Connect, Salesforce, Zendesk, Ada) were
   collected from vendor documentation indexes (`llms.txt`, sitemaps, public help-centre search APIs)
   and direct page fetches instead of web searches. To even this out, a **gap pass** re-ran one
   standard web search (template above) for every `not_found` cell of every platform; notes of cells
   touched in the gap pass say so.
3. **Coding rules made explicit** after the collectors raised borderline cases, applied to all
   platforms in the gap pass:
   - `aiact`: counts only if the page states the vendor's own approach, role or measures regarding the
     EU AI Act (company-wide pages count and are labelled as such). A badge, a line in a certificate
     list, or a page that only explains the law is `not_found`, with the badge mentioned in the note.
   - `residency_eu`: needs a statement that customer data is stored or processed in an EU region, data
     centre or instance. An EU API endpoint alone is `not_found`, mentioned in the note.
   - `eval_judge_cal`: needs a page telling users to compare or tune the AI grader against human
     judgment, or a feature that measures agreement between AI and human ratings. "Review results and
     refine criteria" alone is `not_found`.
   - `eval_repeat`: needs the same test run several times **and** a result reported across the runs
     (pass count over iterations, pass rate, majority vote, consistency score). "Tests can be re-run",
     or variations of a scenario, is `not_found`.
   - `aicaller`: agent-to-agent (A2A) endpoints alone, and answering-machine detection, do not count.
   - `cert_iso27001`: "aligned with ISO 27001" is not a certification and is `not_found`.
