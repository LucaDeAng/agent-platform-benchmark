# Agent platform benchmark: what public docs say (November 2026)

What do the public pages of 17 voice and chat AI agent platforms for enterprise customer service say
about the capabilities a deployment lead has to check before choosing one? This repository answers
that question cell by cell, with a dated public URL behind every documented cell.

It is a benchmark of **public documentation, not of products**. Nothing was tested hands-on, no
accounts were created and no vendor was contacted. A cell marked "not found" means the capability was
not found in public pages with the search procedure in [METHOD.md](METHOD.md). It does not mean the
capability is absent. A cell marked "documented" means the vendor documents it, not that it works as
described.

- Snapshot: pages accessed on 2026-11-08.
- Platforms (17): Ada, Amazon Connect, Cognigy (NICE), Decagon, ElevenAgents (ElevenLabs), Fin
  (formerly Intercom), Genesys Cloud AI, Google Gemini Enterprise for CX (formerly Customer Engagement
  Suite), Kore.ai, LivePerson, Microsoft Copilot Studio / Dynamics 365 Contact Center, Parloa, PolyAI,
  Salesforce Agentforce, Sierra, Vapi, Zendesk AI agents. One candidate, Retell AI, was excluded by
  the inclusion rule (see `data/platforms.csv`).
- Criteria (24): channels, telephony, Italian and other EU languages, tools (APIs, MCP), evaluation
  (simulated users, regression suites, repeated trials, LLM judge, judge calibration), observability,
  human handoff, AI-caller detection and declared-agent protocols, EU data residency, ISO 27001,
  SOC 2, EU AI Act posture, public billing unit, deployment model.
- Full matrix with a link in every documented cell: [docs/results.md](docs/results.md).

## Method in brief

The rubric, the inclusion rule and the search procedure were written in [METHOD.md](METHOD.md) and
committed before any evidence was collected. Each cell is one of:

- **documented**: in product docs, help centre, trust centre, pricing or legal pages;
- **vendor states**: only on marketing pages, blogs or press releases;
- **not found**: unknown;
- **not applicable**: the criterion depends on another one that was not found.

Every count below is computed by `scripts/benchmark.py` from `data/evidence.csv`. Some rules were
made explicit, or changed, after collection started. METHOD.md lists all of them and says they were
not blind to the data.

**How the work was done.** Evidence collection, the gap pass and the re-verification were carried out
by LLM agents using web-search and page-fetch tools, under the author's supervision. The author set
the rubric, reviewed the agents' reports and decided borderline cases. Because the same kind of
tooling did both the collection and the re-checking, the re-verification below is **not an
independent audit**.

## Findings

Counts are out of 17 platforms. "D" means documented, "V" means vendor states. Where a finding rests
on not-found cells, the share of those cells that come from platforms with `partial` or `none`
search coverage is given, because those cells rest on a narrower search (see Limits).

1. **Simulated-user testing is widely published, but repeated-trial metrics are not.**
   - 14 platforms describe testing with simulated customers (11 D, 3 V).
   - Only 4 document running the same test several times and reporting a result across the runs:
     ElevenLabs, Cognigy, Vapi and Zendesk, all D. None calls it pass^k, the metric introduced with
     Sierra's τ-bench ([arXiv 2406.12045](https://arxiv.org/abs/2406.12045)). Zendesk passes a
     scenario on a majority of runs; Cognigy reports a success rate across up to 150 runs.
   - We did not find it for the other 13; 9 of those 13 are on partial/none-coverage platforms.
   - 9 platforms say how the AI grader is checked against human judgment (8 D, 1 V). For 4 of them
     (Google, Genesys, Amazon Connect, Zendesk) the evidence comes from a QA product whose pages
     describe conversations handled by human agents, without saying whether AI-agent conversations
     are covered. Not found for 8, 4 of them on partial/none-coverage platforms.

   A buyer who wants consistency figures on repeated runs will mostly have to ask for them.
2. **Italian is listed by 13 platforms (12 D, 1 V).**
   - Not found for Sierra, Decagon, Parloa and Kore.ai (3 of the 4 on partial/none-coverage
     platforms).
   - Sierra, Decagon and Parloa keep their product docs behind a login. Sierra and Parloa publish
     language counts (over 55, 140+) but no language list. A Parloa docs page on supported languages
     surfaced in search but now returns an error page, so it was not counted. Kore.ai's current docs
     have no language list.
   - In some cases Italian is listed only for one channel or depends on a third-party speech
     provider; see the `lang_it` values in the results.
3. **Handling AI callers is new, and appears only in vendor announcements.** 4 platforms address AI
   callers or declared personal agents, all V and all from posts dated October 2026:
   - **Sierra:** fleming-1, real-time scoring of caller audio for signs of AI generation, alongside
     the Personal Agent Protocol (PAP, in development).
   - **ElevenAgents (ElevenLabs):** synthetic-voice detection, initially for enterprise customers
     through its forward-deployed team; ElevenLabs has joined the PAP working group, with support
     planned.
   - **Decagon:** Personal Agent Gateway and the PACT protocol (specification in progress).
   - **Parloa:** middleware for personal agents, built with design partners and not generally
     available.

   We did not find it in any platform's product docs. For the 13 platforms where nothing was found,
   9 are on partial/none-coverage platforms. Answering-machine detection was not counted.
4. **Where a vendor publishes decides what can be verified.**
   - Sierra, Decagon and Parloa keep their product docs behind a login. They account for 48 of the
     62 vendor-states cells, and have 0, 2 and 3 documented cells respectively.
   - For these three, most capabilities can be checked only through sales material or an NDA, not
     through public documentation.
   - Rule B was relaxed so that they could be included (METHOD.md, change 1).
5. **Compliance basics are well documented; an EU AI Act posture much less so.**
   - 8 platforms document all three of EU data residency, ISO 27001 and SOC 2. EU data residency on
     its own appears for 13 (11 D, 2 V). SOC 2 appears for all 17 (16 D, 1 V).
   - 7 platforms state their own approach to the EU AI Act (4 D, 3 V), and several of those pages are
     company-wide rather than about the product. We did not find one for 10, 7 of them on
     partial/none-coverage platforms. Badges or bare list items (Sierra, Decagon, Cognigy, Kore.ai),
     pages that only explain the law, and use policies that only ban prohibited uses (ElevenLabs)
     were counted as not found.

Other counts:

- 11 platforms document that their agent can use external MCP servers as tools.
- 14 publish a billing unit: per minute, per resolution or outcome, per conversation, credits or seats.
  Cognigy, LivePerson and Ada show "contact sales" only.

## Limits, and how a score can be misread

- **Uneven search coverage.** Because of a per-session cap on the web-search tool, six platforms
  (Parloa, PolyAI, Kore.ai, LivePerson, Genesys, Ada) were collected without web searches and five
  only partly with them. Those platforms were collected from vendor documentation indexes and direct
  page fetches instead. After review, every not-found cell of Parloa and PolyAI received one standard
  web search; the other partial/none platforms did not. Their not-found cells therefore rest on a
  narrower search: on average about 6.2 not-found cells per platform without search coverage, against
  3.8 for platforms with full coverage. See the `search_coverage` column, the last column of the
  counts table in the results, and METHOD.md, change 2.
- **Volume is not quality.** Large suites document more than start-ups. More "D" cells means more
  public documentation, not a better product. Rows are in alphabetical order; this is not a ranking.
- **Suites are scored as a whole.** For Microsoft, Google, Amazon, Salesforce and Genesys, evidence can
  come from different products in the suite, or from company-wide compliance pages. Some QA and
  judge-calibration evidence (Google Quality AI, Zendesk QA, Genesys AI scoring, Amazon evaluations)
  comes from QA products whose pages describe human agents' conversations without saying whether
  they cover AI-agent conversations.
- **Vendor statements are unverified.** Certifications listed on trust centres were not checked
  against audit reports. Announcement-stage features (October 2026) may not be generally available.
- **Tooling.** Pages were read by LLM agents through an automated fetch-and-summarise tool. Some trust
  centres and JavaScript-rendered pages could not be read, and some Salesforce docs were read as `.md`
  files. A summarising tool can misread a page; the re-verification estimates how often, but with the
  same kind of tool.
- **Ownership changes and names.**
  - The company formerly called Intercom renamed itself Fin on 12 May 2026, and Salesforce completed
    its acquisition of Fin on 10 September 2026. **Salesforce therefore owns two of the 17 platforms**
    (Salesforce Agentforce and Fin), which are scored separately.
  - LivePerson was acquired by SoundHound AI (completed September 2026), and Cognigy by NICE (2025).
  - Google now calls its suite "Gemini Enterprise for CX", and Amazon's docs say "Connect Customer".
    Platform names in the tables give the name in use on the access date, with the former name in
    brackets where it changed in 2026. Amazon Connect keeps the name from the candidate list, although
    Amazon's admin docs now say "Connect Customer".

## Re-verification

A random 10% of cells (41 of 408, seed 20261108) were re-checked after collection. **39 of 41
agreed (95%)**. As noted above, the re-check was done with the same kind of LLM tooling as the
collection, so it is not independent.

- The 2 disagreements were both deployment-model cells (Cognigy, Kore.ai). Both were corrected to
  not found and are listed in `data/reverification.csv`.
- 31 of the sampled cells were re-checked by refetching the cited URL.
- Of the 10 sampled not-found cells, 1 was re-checked with a standard web search and 9 by direct
  fetch of vendor pages, because the search cap had been reached again.
- A later review changed 3 more cells (Parloa EU residency and deployment model, ElevenLabs AI Act);
  see METHOD.md, change 6.

## Repository

| Path | Content |
|---|---|
| `METHOD.md` | Scope, inclusion rule, rubric, search procedure, limits, changes after collection |
| `data/platforms.csv` | Platforms, inclusion signal and source, `public_docs`, `search_coverage` |
| `data/criteria.csv` | Criterion IDs, labels, groups |
| `data/evidence.csv` | One row per (platform, criterion): status, value, source type, URL, access date, paraphrase |
| `data/reverification.csv` | The 10% re-verification sample and its outcome |
| `scripts/benchmark.py` | Validation, not-applicable rules, sampling, `docs/results.md` generation |
| `docs/results.md` | Capability matrix, per-criterion counts, recorded values |

```
uv run python scripts/benchmark.py check   # validate data/evidence.csv
uv run python scripts/benchmark.py build   # regenerate docs/results.md
uv run pytest
```

## Disputing a cell

Public pages change, and a cell can be wrong. To dispute one, open an issue naming the platform and
criterion ID, with a **public** URL (no login) that supports a different status. Vendors are welcome
to do this. Cells are only changed on the basis of public sources, and the change is logged in the
row's note with its date.

## Licence

- Data and documentation (`data/`, `docs/`, `METHOD.md`, this README): [CC BY 4.0](LICENSE-DATA).
- Code (`scripts/`, `tests/`): [MIT](LICENSE).
- Product and company names are trademarks of their owners. The dataset contains short paraphrases
  and links, not copies of vendor pages.
