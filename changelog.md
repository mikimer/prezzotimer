# Prezzotimer changelog

## No WIP.

---

## 2:38 PM PT Thursday September 17 2026

### Rebuilt the UI around a confirmation step

**Challenge:** Mike used Prezzotimer for the first time in ~6 months, with a brand-new
deck, and entered the slide count into the duration field. He didn't notice until he was
mid-presentation. Root cause isn't validation — it's that sporadic use plus a new deck
every time means there's no muscle memory to catch a wrong number.

**Current state:** Shipped and pushed (8 commits, `940fa35`..`e86080e`).

- Setup screen: emoji-labelled rows (⏳ Duration, 🎞️ Presenting, 🕰️ Start time, 🪗 Buffer),
  each coloured to match its part of the confirmation diagram. Duration and slides now
  start **empty** — a stale default is easy to walk past. Only start time and buffer
  (10 min) are pre-filled.
- New confirmation screen between setup and timer, drawing the run as a timeline from
  Mike's own sketch: start → arc labelled with seconds per slide → last slide → buffer →
  hard end. Seconds per slide is the number that exposes a swapped value; 24 sec/slide and
  2 min/slide don't look alike even though the inputs do.
- Start now button on the waiting screen: skips the countdown without moving the schedule,
  so the target slide sits at 1 until the real start time and the finish time is unchanged.
- README rewritten and tightened, with a three-panel "comic strip" image
  (`images/strip.png`) built by `compose_screenshot_strip.py`.

**Two bugs worth remembering, both macOS Tk traps:**

1. Every `tk.Label` had `bg='white'` but no `fg`. Tk's default foreground follows macOS
   dark mode, so the text rendered white on white and was invisible. Screen 1 appeared to
   show only emoji (colour glyphs render regardless of fg); screen 3 was entirely blank.
2. Repeated `pack_forget()` / `pack()` frame swapping does not reliably repaint on Aqua.
   The original app did one swap and survived; adding a third screen made screen 3 the
   second swap, and it stayed mapped-but-unpainted. Fixed by stacking all three screens in
   one grid cell with a centred body each and switching via `tkraise()`.

Widget-state probes (`winfo_ismapped`, `cget('text')`) said everything was fine in both
cases — neither bug is visible without looking at colour or at the actual painted window.

**Next steps:** None open. Mike declined Posty cards for the remaining observations:

- Past start time still silently rebases to now, pushing the end later than planned.
  Original behaviour, deliberately left alone; the confirmation screen now makes it visible.
- Timer screen puts "Time Remaining" above "Target slide:", and the big number sits low.
- README's 90/10/80 example is pinned to the current `strip.png`; regenerating the strip
  with different values means updating that sentence too.

**Key files:**

- `prezzotimer.py` — the app, all three screens
- `README.md` — public, repo is PUBLIC at github.com/mikimer/prezzotimer
- `~/Documents/claude_workspace/scripts/compose_screenshot_strip.py` — rebuilds
  `images/strip.png` from raw screenshots; auto-detects the app window and crops each
  panel to its content. `crop <screenshot> <dest>` for one panel, `strip` to rebuild.
