# Building mood boards

Use this when the person has no mood board, asks for one, or wants more directions than they have. Build boards from **image search, not image generation**. Search costs almost nothing; generating 30 images per board burns credits and gives you the model's idea of the look, not the world's.

## Usage notice (always)

The first time you deliver a board in a conversation, say this in one or two lines, in your own words:

> These mood boards are for internal reference only. The images belong to their owners and are linked to their sources. You are responsible for how you use them, including any rights or licensing needed before anything goes into published or client-facing work.

The HTML board carries the same notice. Keep every image's source link.

## 1. Inputs to directions

From the brief and whatever they said about the look (adjectives, references, brands, eras, films, places, things to avoid), write **three territories** that are genuinely different, not three shades of one idea. For each:

```
TERRITORY: <2 to 4 word name a team would say out loud>
LINE: <one-line feel>
KEYWORDS: <6 to 8 across facets: setting, light, palette, material/texture, casting/people, composition, graphic or type>
QUERIES: <5 to 8 searches>
```

If they asked for one specific look, make one territory and go deeper (10 to 12 queries).

## 2. Write queries that find pictures, not articles

- **Noun first, then one visual quality:** "travertine bathroom morning light", "dappled shadow on linen", "editorial beauty portrait sunlight". Not "luxury", "premium", "aspirational": abstract words return stock clichés.
- **One facet per query.** Cover every facet in the territory: a setting query, a light query, a texture query, a people query, a colour query.
- **Add a visual-source word** when results are text-heavy: "editorial", "photography", "interior", "lookbook", "campaign", "still life".
- **Never put confidential information in a query.** No client name, unreleased product, campaign line or anything from the brief that is not public. Search for the look, not the job. Competitor and category references are fine.

## 3. Search

Pick the path by what is available (see step 0 of SKILL.md):

**A. Web search (default, no key).** Run your web search tool once per query. From the results, pick the pages most likely to be visual: photo pages, portfolios, editorial and magazine galleries, interior and design sites, Pinterest pins, Behance, Are.na, brand lookbooks. Skip how-to articles, forums and listicles without strong lead images. Pass the URLs to the script:

```
python3 <skill>/scripts/moodboard.py add <job>/boards "<Territory>" URL URL ... --line "<line>" --keywords "<a, b, c>"
```

It pulls each page's preview image (or the image itself for a direct image link), drops near-duplicates and rebuilds a numbered contact sheet. Sites that block automated access are skipped and listed; do not try to get around them, pick other results.

**B. Image search APIs (when a key is set).** Write a plan file with all territories and run one search:

```json
{"boards": [{"name": "Sunlit Stillness", "line": "...", "keywords": ["..."], "queries": ["...", "..."]}]}
```
```
python3 <skill>/scripts/moodboard.py search plan.json <job>/boards --per 6
```

Uses Brave or Google image search, Pexels or Unsplash, whichever keys exist. Add `--sources openverse,wikimedia` only for art history, eras, places or materials; those archives are weak for mood.

Aim for **20 to 30 candidates per territory.** Two search rounds at most: one wide pass, then one targeted pass for any facet that is missing.

## 4. Curate (this is the craft)

Look at each territory's `contact.jpg` (one image per territory, not one per photo). Keep **8 to 12** that agree with each other. Cut:

- images that belong to a different territory (move them if they fit there)
- stock clichés, obvious ads, heavy text, watermarks, UI screenshots, collages
- near-duplicates and anything off-palette
- anything that would embarrass the team in a client room

A strong board has variety in **scale** (a wide setting, a mid shot, a detail, a texture), one or two people images if the brief has people, and a clear shared palette and light. Then keep them:

```
python3 <skill>/scripts/moodboard.py keep <job>/boards <territory-slug> 3,5,8,11,...
```

This copies the keepers and extracts a palette from them.

## 5. Assemble

- **Figma connected:** build one board per territory on a page named `prmpr / <job> / mood boards`. See "Mood boards" in `figma.md`.
- **No Figma:** `python3 <skill>/scripts/moodboard.py html <job>/boards` writes `boards.html`, a local page with every board, palette, keywords and source links. Offer to open it.
- **Neither:** a markdown summary per territory with the kept image links.

## 6. Pick and lock

Show the three territories side by side with their name, line and palette. Ask which one to take forward, or what to mix ("Territory 1's light with Territory 3's palette"). Then turn the choice into the visual recipe with `moodboard.md`, citing the board images that define each field.

## Gaps

If search cannot find a key image (a very specific product, setting or casting), say what is missing and offer options: a different search angle, the person supplies one, or generate just that image (tell them it uses generation credits and ask first).
