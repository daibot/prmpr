# Mood board to visual recipe

A mood board is a set of signals. Your job is to find what the references share and write it down precisely enough that any image or video model can reproduce the look.

## Sources

- **Figma**: frames, pages or a FigJam board. Use `get_screenshot` to see them and `get_variable_defs` or `get_design_context` for exact brand colours, type and spacing (see `figma.md`).
- **Screenshots, exports, PDFs**: look at each one.
- **URLs**: fetch only if the person okays it and the page is public.
- **Brand guidelines**: these win over mood references when they conflict. Say where they conflict.
- **A pasted prmpr style block** (starts with `prmpr style:`, copied from a thumbnail on prmpr.com): it is already a recipe. Map its fields straight in (`style`, `details`, `look`, `light`, `aspect` to `ar`, and for motion `action`, `camera`, `seconds`). The `subject` always comes from the brief, never from the style. If it is pasted alongside other references, it sets the base look and the brand guidelines and mood board refine it. Use `why it works` to explain the choice back to the person.
- **A prmpr style name** with no block (for example "risograph print", "cinemagraph"): describe that look from its name and ask them to paste the block from prmpr.com if they want it exact.

## How to read it

1. Look at each reference and note what stands out: palette, light, lens, composition, texture, casting, styling, type, motion.
2. Find the **common thread**. Ignore one-offs unless the person points to them.
3. Note **tensions**, for example half the board is moody and half is bright. Ask which way to go, or split them into two recipes.
4. Name the recipe in 2 to 4 words that a team would say out loud ("sunlit kitchen realism").

## Visual recipe (same schema as the prmpr library)

```
RECIPE: <name>
style:   <medium and genre, e.g. "35mm editorial photograph">
subject: <default subject; replaced per frame or execution>
details: <setting, styling, props, casting notes>
look:    [<palette>, <texture or grain>, <lens or rendering>, <composition>, ...]
light:   <lighting setup, or "flat" for graphic styles>
ar:      <aspect ratio of the primary format>
# video only
action:  <the typical movement in frame>
camera:  <camera movement and framing>
seconds: <typical shot length>
# brand layer
palette_hex: [<exact brand colours if known>]
type:    <typefaces and how type is set: weight, case, size>
logo:    <placement and clear space>
avoid:   [<what this look never does>]
```

## Verbal tone (for copy)

```
TONE: <3 adjectives>, not <1 adjective>
VOICE NOTES: sentence length, person (we / you), humour level, words the brand uses, words it never uses
SAMPLE LINE: one line written in that voice
```

## Show it back

Show the recipe and tone in one short block, then ask: "Does this capture the board? Anything to add or remove?" One round of correction is usually enough.
