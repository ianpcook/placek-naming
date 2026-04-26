# Placek Naming Skill

An agent skill for naming companies, products, features, projects, and platforms using David Placek / Lexicon Branding–style methodology.

This is not a loose brainstorming prompt. It is a structured naming process built around product understanding, category contrast, linguistic filters, and the productive tension that makes names memorable.

## What it does

The skill guides an agent through:

1. **Product / category intake** — learn what is actually being named before asking category-relative questions.
2. **Comfort Trap Interview** — surface the user’s bias toward safe, descriptive names.
3. **Landscape audit** — map competitor/category naming conventions so the work can avoid them.
4. **Deep product understanding** — clarify users, buyers, advantages, and strategic naming goals.
5. **Ultimate benefit discovery** — climb from feature to feeling.
6. **Treasure hunt generation** — explore roots, mythology, adjacent domains, sound symbolism, blends, and distant associations.
7. **Linguistic filtering** — evaluate fluency, memorability, sound, and distinctiveness.
8. **Believability testing** — put names in real contexts instead of spreadsheets.
9. **Final evaluation** — score names for originality, surprise, searchability, cross-market risk, and compounding value.

## Key interaction rule

The skill now explicitly requires a **proper back-and-forth**:

- Ask one intake question at a time.
- Wait for the user’s answer.
- Use any supplied context doc before asking redundant questions.
- Do not run the Comfort Trap Interview until the product/category is understood.
- Ask Comfort Trap questions one at a time as well.

No firing squads of five questions. No naming theater in the void.

## Files

```text
SKILL.md
references/
  roots-and-morphemes.md
  sound-symbolism.md
  treasure-hunt-sources.md
scripts/
  naming-roots.py
```

## Usage

Install or copy this folder into an agent skills directory, then invoke it for requests like:

- “Help me name this product.”
- “What should I call this platform?”
- “Rename this feature.”
- “Generate brand name candidates.”
- “Evaluate these names.”

The agent should read `SKILL.md` and follow the methodology before generating candidates.

## Philosophy

Great names do three things:

1. Get attention.
2. Hold attention.
3. Surprise.

Safe names often feel good in meetings and disappear in the market. This skill is designed to push toward the tension zone where names have energy.

## License

MIT-0, unless you choose otherwise.
