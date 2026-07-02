# BC-ComboFlow

A Cinema 4D plugin that renders **every combination** of your product's
options automatically. Model the variants once, and BC-ComboFlow bakes and
renders the full matrix — e.g. 4 colors × 3 materials × 2 cameras = 24
images — with consistent, token-based file names and an optional CSV
manifest.

## Installation

1. Copy the plugin folder into your Cinema 4D `plugins` directory:
   - Windows: `C:\Users\<you>\AppData\Roaming\Maxon\<version>\plugins\BrandnerPlugin`
   - macOS: `~/Library/Preferences/Maxon/<version>/plugins/BrandnerPlugin`
2. Restart Cinema 4D.
3. Open via **Extensions → BC-ComboFlow**.

## How it works

BC-ComboFlow discovers your scene through four null-object groups
(created for you by **Set Up Project Hierarchy**):

```
BR_COMPONENTS
├── BR_VARIABLES     ← one child group per variable (e.g. "Color")
│   ├── Color        ← its children are the options (e.g. "Red", "Blue")
│   └── Material
├── BR_CAMERAS       ← cameras to render from
├── BR_CONSTANTS     ← objects always visible (environment, floor, ...)
└── BR_STAGE         ← created during bake; drives per-frame camera switching
```

Every render combination is one option from each variable plus one camera.
**Matching is by object name** — keep names unique (the plugin warns you
if they aren't).

## Workflow (the four tabs)

1. **Setup** — set the product name, create the hierarchy, then build your
   variables/options/cameras in the Object Manager and press
   **Refresh Scene**. Use *Prev/Next* to step through each combination in
   the viewport and verify it looks right.
2. **Output** — choose the output folder and the token-based filename
   pattern (**+ Token** inserts tokens). The prefix/delimiter/product
   tokens keep names consistent.
3. **Rules** — exclude or require combinations (see below).
4. **Render** — pick a render mode, then hit the big bake button at the
   bottom (visible from every tab; its label tells you what's blocking a
   render, if anything).

## Exclusion rules

One rule per line in the Rules tab. Build them with the dropdowns or type
them directly:

```
Red -> NEVER Studio_Cam            # never render Red with Studio_Cam
Oil Tank -> REQUIRE Landscape      # Oil Tank only renders with Landscape
(Red | Blue) & Close_Cam -> NEVER Chrome
# lines starting with # are comments
```

- `->` separates the IF side from the action.
- `&` = AND, `|` = OR (parentheses group OR terms).
- `NEVER` removes matching combinations; `REQUIRE` removes combinations
  where the target is missing. No keyword defaults to `NEVER`.
- The status line reports how many combinations your rules exclude, plus
  any lines that can't be parsed or reference renamed/deleted objects.

## Render modes

| Mode | What it does |
|------|--------------|
| Bake Only | Creates the baked file, renders nothing |
| Render to Picture Viewer | Interactive render of all combinations |
| Background Render | Threaded render while you keep working |
| Add to Render Queue (& Start) | Saves the baked file to `ComboFlow_Bakes/` and queues it — the BR_STAGE camera is pre-selected automatically |

"Generate CSV" writes a `<product>_metadata.csv` manifest of every
combination next to your renders.

## Good to know

- The top warning line flags duplicate names, filename patterns that would
  overwrite files, and broken rules — if it's blank, you're good.
- Documents saved with older plugin versions are migrated automatically
  when the plugin opens.
- Your naming preferences (prefix, delimiter, filename pattern, render
  mode) are remembered and become the defaults for new documents.
- Baked files are saved to `ComboFlow_Bakes/` next to your project file;
  your working scene is never modified by a bake.
