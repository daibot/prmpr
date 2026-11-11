# Model prompt dialects

Turn a visual recipe plus a frame or execution into a prompt for each model. Each model reads prompts differently. These forms match the prmpr library renderers so a style looks the same across tools.

Fields come from the recipe: `style`, `subject`, `details`, `look[]`, `light`, `ar`, and for video `action`, `camera`, `seconds`. Add composition notes (negative space for headline, product placement) to `details`.

## Image

**Midjourney**
`<style> of <subject>, <details>, <look, comma separated>, <light> --ar <ar> --v 7`
Add `--style raw` for photography. Use `--sref <url>` with a mood board image if they have one. Midjourney has no API, so give the prompt for them to paste.

**ChatGPT / GPT Image**
`Create a <style> of <subject>, <details>. Style: <look>. Lighting: <light>. Use a <ar> <orientation> format.`
Plain sentences work best. Strong for editing a supplied image and for exact text, if a comp with type is wanted.

**Gemini / Imagen**
`Generate an image: <style> of <subject>, <details>. <Look>. <Light>. <Orientation> <ar> aspect ratio.`
Good for keeping a character or product consistent across edits with a reference image.

**Flux**
`<Style> of <subject>, <details>. <Look as short sentences>. <Light>.`
Descriptive prose. Set the aspect ratio in the tool settings, not the prompt.

**Ideogram**
`<Style>, <subject>, <details>, <look>, <light>`
The best choice when type must be inside the image (posters, comps). Put the exact text in quotes.

Leave out `light` for flat or graphic styles.

## Video

Keep each shot 4 to 8 seconds. One action and one camera move per shot.

**Sora**
`<Style>. Subject: <subject>. Action: <action>. Camera: <camera>. Look: <look>. <seconds> seconds, <ar>.`

**Veo**
`A <seconds>-second <style> shot of <subject>. <Action>. <Camera>. <Look>. <Audio: dialogue in quotes, or "no dialogue", plus ambience and music>.`
Veo generates sound, so always say what audio you want.

**Kling**
`<subject>, <action>, <camera>, <style>, <look>`
Works best from a start frame (image to video). Give the still prompt as well.

**Runway**
`[<camera>] <Subject>: <action>. <Style>, <look>.`
Best from a reference still.

**Midjourney video**
Two steps: a still with `/imagine`, then Animate (Manual, Low or High motion) with the action and camera as the motion prompt.

## Delivering prompts

Group prompts by frame or execution, one copyable code block per model. Do not repeat all models for every frame unless they ask: default to the two that fit best (for example Midjourney + GPT Image for adcepts, a still model + Veo or Kling for storyboards) and offer the rest.
