# Working with Figma

Use Figma when its tools are available. If they are not, ask for screenshots or exports and carry on.

## Before the first call

- Ask which file(s) to use, or take the URL they gave. Parse the file key and node ID from the URL (`node-id=1-2` becomes `1:2`).
- Call `create_session` with the file key and a short task description before any other file tool. Reuse the session ID.
- Confirm the account is the right one for this client. Agency people often have several Figma accounts or teams. Do not pull one client's files into another client's work.

## Reading (mood boards, brand, existing work)

- `get_screenshot` on frames or pages to see the mood board.
- `get_variable_defs` for brand colour, type and spacing tokens. Put exact values into the recipe's `palette_hex` and `type`.
- `get_metadata` to map a large file before taking screenshots of everything.
- `search_design_system` and `get_libraries` to find the brand's components (logo lockups, CTA buttons, end cards) to reuse when building.
- FigJam boards: use `get_figjam`.

## Building boards

Load the Figma plugin's `figma-use` skill (or the MCP resource `skill://figma/figma-use/SKILL.md`) before calling `use_figma`. For bigger layouts, `figma-generate-design` also helps. Let those skills handle the Figma mechanics. This skill decides what goes on the board.

Default build:
- **Where**: a new page named `prompr / <job> / <date>` in a file they chose, or a new file via `create_new_file`. Never edit their existing frames unless they ask.
- **Adcepts**: see the layout in `adcepts.md`. Live text layers for the headline, body, tagline and CTA, using the brand's fonts and colour variables when they exist. The image is a placeholder rectangle with the key visual prompt in a notes text layer, or the generated image if one exists.
- **Storyboards**: see the layout in `storyboards.md`. Frames on a grid with auto layout, captions as live text.
- Name every layer clearly (`R1 / Exec 1 / Headline`) so the team can take over.

## AI features inside Figma

Figma's own generation tools (`generate_image`, `generate_vector_illustration`, Weave) use the account's AI credits. Ask before using them. By default, write prompts and leave placeholders.

## No Figma

Ask for: a screenshot or export of the mood board, brand guidelines (PDF or screenshots of colour and type pages), and any existing campaign work. Deliver boards as markdown with image prompts, and offer a layout spec a designer can build from.
