# Video storyboards

A storyboard sells a film before it is shot: what we see, hear and read, frame by frame, with timing. It should also give a director, an animator or an AI video tool enough to make the film.

## Start with the format

| Format | Frames (rough) | Notes |
|---|---|---|
| :06 bumper | 2 to 3 | One idea, one visual twist, logo throughout or at the end |
| :15 | 4 to 6 | Brand in first 3 s for social; single message |
| :30 | 8 to 12 | Setup, turn, payoff, end card |
| :60 | 14 to 20 | Room for story; still one message |
| Vertical social (9:16) | 1 frame per 1.5 to 2 s | Hook in first 1 to 2 s, built for sound off, supers carry the story, safe zones for UI |

About one frame per 2 to 3 seconds for broadcast. Fewer frames with strong moments beat many frames of coverage.

## Structure

Before frames, write:

```
TITLE: <route name> :<length> <aspect ratio>
THE IDEA: <one sentence>
STORY IN 3 BEATS: setup / turn / payoff
SOUND: music direction, VO casting, key SFX
```

Then the frame table:

| # | Time | Shot | Visual | VO / Dialogue | SUPER (on-screen text) | SFX / Music | Transition |
|---|---|---|---|---|---|---|---|
| 1 | 0:00–0:02 | CU, eye level, slow push in | ... | ... | ... | ... | cut |

Shot language: ECU, CU, MCU, MS, WS, EWS; angles (eye level, low, high, overhead, POV); movement (static, push in, pull out, pan, tilt, tracking, handheld, crane, whip pan).

End with an **end card** frame: logo, tagline, CTA, legal.

## Craft checks (add to the success criteria)

- **Sound-off test** (social): the story works on supers and visuals alone.
- **Hook**: something happens in the first 2 seconds for social or the first 5 for TV.
- **Brand early enough**: brand or product shown within 3 seconds for social, earlier than the end for TV.
- **One message**: the payoff matches the SMP.
- **Timing adds up**: frame timings sum to the length, and VO fits (about 2.5 words per second; a :30 holds about 65 to 70 words of VO).
- **Shootable**: each frame is something a crew or an AI tool can actually make. Flag hard shots (crowds, animals, kids, specific locations, product close-ups needing a real product).
- **Legal room**: supers and disclaimers have time on screen (at least 1 s per 3 words, longer for legal).

## Keeping frames consistent

Before writing frame prompts, define:

```
CONTINUITY SHEET
recipe: <recipe name>
characters: <name, age, look, wardrobe; one line each, reused word for word in every prompt>
location: <one line reused word for word>
product: <how it appears; real product shots needed? y/n>
palette / grade: <locked>
```

Reuse these lines word for word in every frame prompt. If the tool supports it, generate a character or key frame first and use it as a reference image for the rest.

## Check the super against every frame

Generators ignore "negative space for the super" more often than not. After placing images, look at each frame with the super on top. If the subject collides with it, fix it in the layout (a soft scrim in the background colour behind the super, or a re-crop) rather than moving the super. The super stays in one position for the whole video. For end cards, composite the packshot low on the brand background so the product name and CTA have clear space. Note in the delivery that real footage must be framed with that space.

## Outputs

1. **Board**: the frame table plus one image per frame (generated, or a prompt and a placeholder).
2. **Frame prompts**: one still prompt per frame (for boards), using the image dialects.
3. **Shot prompts**: one video prompt per shot for animatics or AI production (Veo, Sora, Kling, Runway), using the video dialects. Keep shots 4 to 8 seconds; split longer ones.
4. **Animatic notes** (optional): frame holds, transitions, temp music, VO read timing.

## Figma layout

One page per route. A title frame, then a grid of 16:9 (or 9:16) frames, three or four across, each with a caption block under it: frame number and time, shot, VO and SUPER in live text. End card as the last frame.
