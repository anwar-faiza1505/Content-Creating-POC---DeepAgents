---
name: ABC-article
description: >
  Use this skill for article-style or long-form marketing content where ABC
  tone, structure, and reader flow matter. Produces a complete ABC-standard
  article using a 4-agent pipeline: researcher → outline_writer → content_writer
  → compliance_editor.
---

# ABC Article Skill

## Required Workflow

1. Call `write_todos` first.
2. Read the research brief and any workspace context files.
3. Delegate research to `researcher` — current information, proof points, or source discovery.
4. Delegate outlining to `outline_writer` — structures the article in ABC's reader-first flow.
5. Draft the full article in one pass using `content_writer` — one coherent voice, not disconnected sections.
6. Send the full draft to `compliance_editor` for a ABC tone, flow, and FCA compliance pass.
7. Write the final publication-ready article to `output/final/<slug>.md`.

**Do not skip any step.** Each agent builds on the previous one's output.

---

## The Four Agents

| Step | Agent | What it does | Reads | Writes |
|------|-------|-------------|-------|--------|
| 1 | `researcher` | Gathers topic knowledge from the web | (web search) | `output/research/<slug>.md` |
| 2 | `outline_writer` | Structures article in ABC reader-first flow | research file | `output/outlines/<slug>.md` |
| 3 | `content_writer` | Writes the complete article (800–1200 words) | research + outline | `output/drafts/<slug>.md` |
| 4 | `compliance_editor` | Tone pass + FCA disclaimers + final polish | draft file | `output/final/<slug>.md` |

---

## Step-by-Step Delegation

### Step 1 — Research the Topic

```
task(
  subagent_type="researcher",
  description="Research '[TOPIC]' for a ABC UK marketing article.
               Save findings to output/research/<slug>.md"
)
```

Wait for the researcher to finish before moving on.

### Step 2 — Create the Article Outline

```
task(
  subagent_type="outline_writer",
  description="Read output/research/<slug>.md.
               Create a ABC reader-first article outline.
               Save to output/outlines/<slug>.md"
)
```

### Step 3 — Write the Full Article

```
task(
  subagent_type="content_writer",
  description="Read output/research/<slug>.md and output/outlines/<slug>.md.
               Write the complete ABC article (800–1200 words) in one coherent pass.
               Save draft to output/drafts/<slug>.md"
)
```

### Step 4 — Compliance & Tone Review

```
task(
  subagent_type="compliance_editor",
  description="Read output/drafts/<slug>.md.
               Improve ABC tone and flow. Add FCA disclaimers.
               Fix any unsupported claims. Save final article to output/final/<slug>.md"
)
```

---

## Content Expectations

- Start with the main reader benefit — the outcome, not the definition.
- Maintain one consistent voice across the whole piece.
- Prefer natural section flow over formulaic transitions.
- Use UK English, active voice, and practical wording.
- Match the language patterns in `AGENTS.md` tone references without reusing copy.
- Keep claims grounded in research brief and evidence only.

---

## Article Structure

```
# [Title — benefit-led or question-style, not a definition]

**Important information** – the value of investments and the income from them,
can go down as well as up, so you may get back less than you invest.

[Opening 2–3 sentences — directly answer the core question, lead with reader benefit]

[Context paragraph — why this matters now]

#### [Section heading — specific, practical]
[2–3 short paragraphs. Concrete examples. Active voice.]

#### [Section heading]
[2–3 short paragraphs.]

... (4–6 sections total)

#### Key takeaways
- [Actionable point]
- [Actionable point]
- [Actionable point]

#### Next steps
[One practical action — review, calculate, or explore. No pressure.]

**Important information** – investors should note that the views expressed may no
longer be current and may have already been acted upon. This information is not a
personal recommendation for any particular investment. If you are unsure about the
suitability of an investment you should speak to one of ABC's advisers or an
authorised financial adviser of your choice.
```

---

## Slug Naming Convention

Convert the topic to a URL-friendly slug:
- Lowercase, spaces to hyphens, remove punctuation.

Examples:
- "What is a Stocks and Shares ISA?" → `what-is-a-stocks-and-shares-isa`
- "How to start investing" → `how-to-start-investing`
- "Understanding pension drawdown" → `understanding-pension-drawdown`

---

## Guardrails

- Do not write disconnected sections independently.
- Do not copy research notes or style references verbatim.
- Do not add product claims or numbers unless supported by the research brief.
- Do not expose internal planning steps in the final output.
- The compliance_editor reviews the full document — not isolated fragments.

---

## After Completion

Confirm:
1. Final file path: `output/final/<slug>.md`
2. A 2-sentence summary of what the article covers.
3. Word count of the final article.
