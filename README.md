# PREZZOTIMER ⏰ 🤔

Shows the slide number you *should* be on, so a big deck doesn't run overtime.

![Set it up, check it, present](images/strip.png)

## Run it

Python 3 with tkinter. No other dependencies.

```
git clone https://github.com/mikimer/prezzotimer.git
cd prezzotimer
python3 prezzotimer.py
```

Homebrew Python may need `brew install python-tk` first.

## Using it

| Field | |
|---|---|
| ⏳ Duration | the whole session, wall clock |
| 🎞️ Presenting | total slides |
| 🕰️ Start time | `2:30pm`, `1430`, `14:00` and `2.30` all work |
| 🪗 Buffer | minutes held back at the end for Q&A |

Duration includes both time presenting plus the buffer. So an 80-minute duration with a 10-minute buffer paces the speaker to present for 70 minutes.

For my presentations I use two monitors. Here's my implementation:

<img src="Mac-External-Displays-Arrangment.jpg" width="420" alt="Two monitors set to screen extension, not mirroring">

## My problem

I believe in [one-idea-per-slide](https://www.youtube.com/shorts/qKDvUO-hK5s). I run a [workshop](https://lu.ma/nascent) where I present ~250 slides over 2 hours with lots of audience participation, so it's easy to run long — and I want to respect my audience's time. I used to keep time by [hand-writing a table](IMG_0532.jpeg) of clock time vs. target slide. Tedious, and it distracts from the preso.


