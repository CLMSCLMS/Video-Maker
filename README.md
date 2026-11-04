# What a Minute's Worth — music video

A music video for an original country song: building CLMS in Ohio, chasing big dreams, loving
Cheyenne, raising a family, and learning what success is really worth. It stars you, Cheyenne,
your son, the dogs, the crew, the three buildings and the farm.

## How it works

1. Record the song and save it as `media/song.mp3`.
2. Film or gather the shots below. Name each file after its shot id, e.g. `media/s14-cheyenne-porch.jpg`
   or `media/s14-cheyenne-porch.mov`. Photos and phone videos both work, portrait or landscape.
3. Run `python3 make_video.py --preview` for a fast 720p check, then `python3 make_video.py` for the final 1080p.
   Output goes to `out/music_video.mp4`, plus `out/lyrics.srt` for YouTube/Facebook captions.

Any shot you don't have yet appears as a storyboard card, so you can watch the whole thing at any stage.
Run `python3 make_video.py --list` to see what's still missing.

## Syncing to your recording

In `project.json`, set each section's `"start"` (seconds) to when it begins in the real recording.
Until you do, the planned timings get stretched to fit the song length automatically.
For exact lyric timing, a line can be written as `{"t": 57.5, "text": "..."}`.

Per-shot options: `"in": 12` (start a clip 12s in), `"speed": 0.5` (slow motion),
`"weight": 2` (give a shot twice the screen time), `"move": "in" | "out" | "left" | "right" | "none"` (photo motion).
Set `"show_lyrics": false` to turn off on-screen lyrics.

## Filming tips

- Shoot landscape (sideways phone) when you can. Golden hour (the hour after sunrise or before sunset) does most of the work.
- Clips of 10–15 seconds are plenty; hold steady and let things happen in the frame.
- Verses = work and pressure (cooler, busier). Choruses = home, Cheyenne, the dogs (warm, golden).
  The bridge is slow and quiet. The final chorus is the big payoff, so save your best drone/family shots for it.
- Old photos (first truck, wedding, baby pictures) work great; just scan or photograph them.

## Shot list (54 shots)

### Intro  (starts 0:00)

- [ ] `s01-farm-sunrise` — Wide shot of the farm at first light, fog on the fields. Title appears.
- [ ] `s02-coffee-boots` — Close-up: coffee mug steaming on a truck hood, boots lacing up.

### Verse 1  (starts 0:12)

- [ ] `s03-trucks-startup` — CLMS trucks firing up in the yard before dawn, headlights on, breath in the cold air.
- [ ] `s04-logo-door` — Close-up of the CLMS logo on a truck door.
- [ ] `s05-boots-dirt` — Your boots in Ohio dirt, walking toward the crew.
- [ ] `s06-mowing-summer` — Summer: crew mowing, fresh-cut stripes in the grass.
- [ ] `s07-snow-plow` — Winter: plow trucks pushing snow (last winter's footage works).
- [ ] `s08-crew-huddle` — Morning huddle with the crew - the faces counting on you.
- [ ] `s09-buildings-drive` — Driving past each of the three buildings.
- [ ] `s10-farm-gate` — You at the farm gate looking out over the land.
- [ ] `s11-desk-night` — You at the desk late, phone in hand, plans spread out.

### Chorus  (starts 0:52)

- [ ] `s12-two-lane-road` — CLMS truck on a two-lane country road at golden hour (drone or from a following car).
- [ ] `s13-driving-home` — You driving, glancing at a photo of Cheyenne on your phone or visor.
- [ ] `s14-cheyenne-porch` — Cheyenne waiting on the porch, dogs at her feet.
- [ ] `s15-son-sleeping` — Your little boy asleep, shot from the doorway.
- [ ] `s16-building-sign` — Your name/CLMS sign on one of the buildings.
- [ ] `s17-sunset-field` — Sunset over the farm.
- [ ] `s18-holding-hands` — Close-up: you and Cheyenne holding hands.
- [ ] `s19-dogs-run` — The dogs running across the field toward camera.

### Verse 2  (starts 1:28)

- [ ] `s20-meeting` — You in a meeting or walking into a bank/office, sharper clothes.
- [ ] `s21-handshake` — Handshake across a table.
- [ ] `s22-working-hands` — Close-up of your hands - dirt, scars, a wrench or shovel.
- [ ] `s23-truck-alone` — You alone in the parked truck, engine off, thinking.
- [ ] `s24-front-door` — Coming through the front door tired, still on the phone.
- [ ] `s25-phone-down` — You set the phone face-down; Cheyenne looks up.
- [ ] `s26-rain` — Rain on a window or a storm rolling over the fields.
- [ ] `s27-kitchen-hug` — Cheyenne hugging you in the kitchen.

### Chorus  (starts 2:08)

- [ ] `s28-dogs-truck` — Dogs hanging out in the truck (parked or rolling slowly on the farm).
- [ ] `s29-fence-walk` — You, Cheyenne and the dogs walking the fence line.
- [ ] `s30-porch-sunset` — You and Cheyenne on the porch at sunset.
- [ ] `s31-old-photos` — Old photos from the early days: first truck, first jobs.
- [ ] `s32-drone-properties` — Drone over the properties.

### Verse 3  (starts 2:44)

- [ ] `s33-crew-families` — Company cookout - the crew with their families.
- [ ] `s34-crew-laugh` — Shaking hands with an employee, both laughing.
- [ ] `s35-son-boots` — Your son clomping around in your boots or hard hat.
- [ ] `s36-son-falls` — Your son trips; you kneel and help him up.
- [ ] `s37-teach-son` — Teaching your son something - riding the mower with you, using a tool.
- [ ] `s38-plant-tree` — Planting a tree together on the farm.
- [ ] `s39-son-dogs` — Your son playing with the dogs.

### Bridge  (starts 3:24)

- [ ] `s40-rocking-chairs` — Two empty rocking chairs on the porch. Slow.
- [ ] `s41-cheyenne-slowmo` — Slow motion: Cheyenne turning to camera in golden light.
- [ ] `s42-wedding-photos` — Wedding / early relationship photos.
- [ ] `s43-house-night` — The house at night, porch light on, warm windows.
- [ ] `s44-forehead-kiss` — You kissing Cheyenne's forehead.

### Final Chorus  (starts 4:04)

- [ ] `s45-drone-rise` — Big drone rise over the farm at sunrise.
- [ ] `s46-fleet-lineup` — Whole CLMS fleet lined up, crew waving.
- [ ] `s47-two-pairs-boots` — Your boots and your son's little boots side by side in the dirt.
- [ ] `s48-family-field` — Hero shot: you, Cheyenne, your son and the dogs in the field.
- [ ] `s49-bonfire` — Night bonfire, everyone laughing.
- [ ] `s50-barn-dance` — You and Cheyenne slow dancing in the barn or kitchen.

### Outro  (starts 4:44)

- [ ] `s51-building-dusk` — One of the buildings at dusk, lights coming on.
- [ ] `s52-cheyenne-smile` — Cheyenne smiling at camera.
- [ ] `s53-son-dad` — Your son running into your arms.
- [ ] `s54-stars-farm` — Stars over the farm. Hold, fade to black.
