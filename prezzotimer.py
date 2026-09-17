import tkinter as tk
from datetime import datetime, timedelta

# Sketch colours: green for the start, purple for the pacing arc, red for the finish.
GREEN = '#2e9e6b'
PURPLE = '#8b3fd6'
RED = '#d92d4a'
GREY = '#7a7a7a'
INK = '#1a1a1a'   # explicit: Tk's default fg follows macOS dark mode

CANVAS_W = 520
CANVAS_H = 200


def fmt_clock(dt):
    """9:30am — lowercase, no leading zero."""
    return dt.strftime('%-I:%M%p').lower()


class PrezzotimerApp:
    """
    PrezzotimerApp is a Tkinter-based timer for pacing slide presentations.
    It helps presenters keep on track by showing the ideal slide number based on elapsed time.

    Three screens: input -> confirmation -> timer. The confirmation screen exists because
    the input fields are just numbers, and a number in the wrong field looks fine until
    you are mid-presentation. The confirmation restates the setup as times and seconds
    per slide, which is where a swapped value becomes obvious.
    """

    def __init__(self, root):
        """
        Initialize the PrezzotimerApp with input, confirmation and timer screens.
        """
        self.root = root
        root.title('Prezzotimer')
        root.geometry('680x520')
        root.configure(bg='white')

        self._build_input_screen()
        self._build_confirm_screen()
        self._build_timer_screen()

        self.timer_running = False
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        for screen in (self.input_frame, self.confirm_frame, self.timer_frame):
            screen.grid(row=0, column=0, sticky='nsew')
        self.input_frame.tkraise()
        self.duration_entry.focus_set()

    # ------------------------------------------------------------ input screen

    def _build_input_screen(self):
        """
        Build the setup screen. Duration and slides are deliberately left empty —
        they change with every deck, and a stale default is easy to walk past.
        Only start time and buffer are pre-filled, since those are near enough
        every time to be worth a head start.

        Each row is coloured to match its part of the confirmation sketch.
        """
        self.input_frame = tk.Frame(self.root, bg='white')
        self.input_body = tk.Frame(self.input_frame, bg='white')
        self.input_body.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.input_body, text='Prezzotimer', font=('Helvetica Neue', 24, 'bold'),
                 bg='white', fg=INK).grid(row=0, column=0, columnspan=4, pady=(0, 22))

        # Duration — left empty on purpose
        self.duration_var, self.duration_entry = self._field(
            1, 'Duration', '\u23f3', '', 'minutes', PURPLE)

        # Total slides — left empty on purpose
        self.slides_var, _ = self._field(
            2, 'Presenting', '\U0001f39e\ufe0f', '', 'slides', INK)

        # Start time, defaulting to the next half hour or hour
        now = datetime.now()
        if now.minute < 30:
            default_start = now.replace(minute=30, second=0, microsecond=0)
        else:
            default_start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        self.start_time_var, _ = self._field(
            3, 'Start time', '\U0001f570\ufe0f', fmt_clock(default_start), '', GREEN)

        # Buffer — end the pacing early to leave room for Q&A
        self.buffer_var, _ = self._field(
            4, 'Buffer', '\U0001fa97', '10', 'minutes', RED)

        self.input_error = tk.Label(self.input_body, text='', font=('Helvetica Neue', 13),
                                    fg=RED, bg='white')
        self.input_error.grid(row=5, column=0, columnspan=4, pady=(14, 0))

        tk.Button(self.input_body, text='Review setup', font=('Helvetica Neue', 15),
                  command=self.show_confirmation).grid(row=6, column=0, columnspan=4, pady=14)

    def _field(self, row, label, emoji, default, unit, colour):
        """
        Add one input row: right-aligned name, emoji, entry, unit.

        The emoji sits in its own widget so the name column stays cleanly
        right-aligned regardless of how wide the glyph renders.
        """
        tk.Label(self.input_body, text=label, font=('Helvetica Neue', 19, 'bold'),
                 bg='white', fg=colour, anchor='e').grid(row=row, column=0, sticky='e', pady=7)
        tk.Label(self.input_body, text=emoji, font=('Helvetica Neue', 20),
                 bg='white').grid(row=row, column=1, padx=(10, 16))

        var = tk.StringVar(value=default)
        entry = tk.Entry(self.input_body, textvariable=var, font=('Helvetica Neue', 17),
                         width=10, bg='white', fg=INK, insertbackground=INK,
                         relief='solid', bd=1, highlightthickness=0)
        entry.grid(row=row, column=2, sticky='w', ipady=3)

        tk.Label(self.input_body, text=unit, font=('Helvetica Neue', 15),
                 bg='white', fg=colour, anchor='w').grid(row=row, column=3, sticky='w', padx=(10, 0))
        return var, entry

    # ----------------------------------------------------- confirmation screen

    def _build_confirm_screen(self):
        """Build the confirmation screen: the sketch, one summary line, two buttons."""
        self.confirm_frame = tk.Frame(self.root, bg='white')
        self.confirm_body = tk.Frame(self.confirm_frame, bg='white')
        self.confirm_body.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.confirm_body, text='Does this look right?',
                 font=('Helvetica Neue', 20, 'bold'), bg='white', fg=INK).pack(pady=(10, 4))

        self.canvas = tk.Canvas(self.confirm_body, width=CANVAS_W, height=CANVAS_H,
                                bg='white', highlightthickness=0)
        self.canvas.pack()

        self.confirm_summary = tk.Label(self.confirm_body, text='',
                                        font=('Helvetica Neue', 13), fg=GREY, bg='white')
        self.confirm_summary.pack(pady=(0, 16))

        buttons = tk.Frame(self.confirm_body, bg='white')
        buttons.pack()
        tk.Button(buttons, text='←  Go back', font=('Helvetica Neue', 14),
                  command=self.back_to_input).pack(side='left', padx=8)
        tk.Button(buttons, text='Start timer  ▶', font=('Helvetica Neue', 14),
                  command=self.begin_timer).pack(side='left', padx=8)

    def draw_confirmation(self):
        """
        Draw the setup as the sketch: start time, an arc labelled with seconds per slide,
        the moment the last slide lands, then the buffer running on to the hard end.
        """
        c = self.canvas
        c.delete('all')

        # The pacing arc, from the start time over to the last slide.
        c.create_line(50, 140, 120, 75, 180, 52, 250, 70, 320, 132,
                      smooth=True, width=5, fill=PURPLE, arrow='last',
                      arrowshape=(16, 20, 7), capstyle='round')
        # The buffer, running from the last slide to the hard end.
        c.create_line(348, 118, 424, 118, width=5, fill=RED, arrow='last',
                      arrowshape=(16, 20, 7), capstyle='round')

        c.create_text(50, 148, text=fmt_clock(self.start_time), anchor='n',
                      font=('Helvetica Neue', 21, 'bold'), fill=GREEN)
        c.create_text(50, 176, text='start', anchor='n',
                      font=('Helvetica Neue', 12), fill=GREEN)

        c.create_text(185, 64, text=f'{self.seconds_per_slide}sec', anchor='n',
                      font=('Helvetica Neue', 23, 'bold'), fill=PURPLE)
        c.create_text(185, 94, text='per slide', anchor='n',
                      font=('Helvetica Neue', 12), fill=PURPLE)

        c.create_text(320, 140, text=fmt_clock(self.last_slide_time), anchor='n',
                      font=('Helvetica Neue', 21, 'bold'), fill=RED)
        c.create_text(320, 168, text=f'{int(self.buffer_minutes)}m buffer', anchor='n',
                      font=('Helvetica Neue', 12), fill=RED)

        c.create_text(462, 126, text=fmt_clock(self.end_time), anchor='n',
                      font=('Helvetica Neue', 21, 'bold'), fill=RED)
        c.create_text(462, 154, text='end', anchor='n',
                      font=('Helvetica Neue', 12), fill=RED)

        self.confirm_summary.config(
            text=f'\U0001f39e️ {self.total_slides} slides   ·   '
                 f'⏳ {int(self.duration_minutes)} min'
        )

    def show_confirmation(self):
        """Validate the inputs, work out the schedule, and show it for a second look."""
        try:
            self.read_inputs()
        except ValueError as e:
            self.input_error.config(text=str(e))
            return
        self.input_error.config(text='')
        self.confirm_frame.tkraise()
        self.draw_confirmation()

    def back_to_input(self):
        self.input_frame.tkraise()
        self.duration_entry.focus_set()

    # -------------------------------------------------------------- the maths

    def parse_start_time(self, start_time_str):
        """
        Parse the start time string into a datetime object (24h or 12h format).
        Accepts '1400', '14:00', '2pm', '2:30pm', '2.20', etc.
        """
        s = start_time_str.strip().lower().replace(' ', '')
        # Handle '2.20' or '14.20' as '2:20' or '14:20'
        if '.' in s and s.replace('.', '').isdigit():
            parts = s.split('.')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                s = f'{int(parts[0])}:{int(parts[1]):02d}'
        if len(s) == 4 and s.isdigit():
            s = s[:2] + ':' + s[2:]
        elif 'am' in s or 'pm' in s:
            ampm = 'am' if 'am' in s else 'pm'
            time_part = s.replace('am', '').replace('pm', '')
            if ':' in time_part:
                hour, minute = time_part.split(':')
            else:
                hour, minute = time_part, '00'
            hour = int(hour)
            minute = int(minute)
            if ampm == 'pm' and hour != 12:
                hour += 12
            if ampm == 'am' and hour == 12:
                hour = 0
            s = f'{hour:02d}:{minute:02d}'
        now = datetime.now()
        return datetime.strptime(s, '%H:%M').replace(year=now.year, month=now.month, day=now.day)

    def calculate_ideal_slide(self, elapsed_seconds, total_seconds, total_slides):
        """
        Calculate the ideal slide number based on elapsed time.
        """
        ideal_slide = int(round((elapsed_seconds / total_seconds) * total_slides))
        if ideal_slide < 1:
            ideal_slide = 1
        if ideal_slide > total_slides:
            ideal_slide = total_slides
        return ideal_slide

    def read_inputs(self):
        """
        Read and validate the four fields, then work out the schedule the
        confirmation screen draws and the timer runs on.
        """
        try:
            self.duration_minutes = float(self.duration_var.get())
        except ValueError:
            raise ValueError('Duration needs a number of minutes.')
        try:
            self.total_slides = int(self.slides_var.get())
        except ValueError:
            raise ValueError('Total slides needs a whole number.')
        try:
            self.buffer_minutes = float(self.buffer_var.get())
        except ValueError:
            raise ValueError('Buffer needs a number of minutes.')
        if self.duration_minutes <= 0:
            raise ValueError('Duration must be more than 0.')
        if self.total_slides <= 0:
            raise ValueError('Total slides must be more than 0.')
        if self.buffer_minutes < 0:
            raise ValueError('Buffer cannot be negative.')

        effective_duration = self.duration_minutes - self.buffer_minutes
        if effective_duration <= 0:
            raise ValueError('Buffer must be less than duration.')

        try:
            parsed_start_time = self.parse_start_time(self.start_time_var.get())
        except ValueError:
            raise ValueError("Can't read that start time — try 2:30pm or 1430.")

        now = datetime.now()
        # If start time is in the past or now, start from now and run for effective duration
        if parsed_start_time <= now:
            self.start_time = now
        else:
            self.start_time = parsed_start_time
        self.effective_duration = effective_duration
        self.last_slide_time = self.start_time + timedelta(minutes=effective_duration)
        self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        self.seconds_per_slide = int(round(effective_duration * 60 / self.total_slides))

    # ------------------------------------------------------------ timer screen

    def _build_timer_screen(self):
        self.timer_frame = tk.Frame(self.root, bg='white')
        self.timer_body = tk.Frame(self.timer_frame, bg='white')
        self.timer_body.place(relx=0.5, rely=0.5, anchor='center')
        self.timer_label = tk.Label(self.timer_body, text='', font=('Helvetica Neue', 24),
                                    bg='white', fg=INK)
        self.timer_label.pack(pady=20)
        self.time_remaining_label = tk.Label(self.timer_body, text='',
                                             font=('Helvetica Neue', 18), bg='white', fg=INK)
        self.time_remaining_label.pack()
        self.target_slide_label = tk.Label(self.timer_body, text='Target slide:',
                                           font=('Helvetica Neue', 18), bg='white', fg=INK)
        self.target_slide_label.pack()
        self.slide_number_label = tk.Label(self.timer_body, text='--',
                                           font=('Helvetica Neue', 96), bg='white', fg=INK)
        self.slide_number_label.pack()
        self.elapsed_label = tk.Label(self.timer_body, text='', font=('Helvetica Neue', 14),
                                      bg='white', fg=INK)
        self.elapsed_label.pack(pady=5)

    def begin_timer(self):
        """
        Leave the confirmation screen, switch to the timer screen, and begin updates.
        """
        self.timer_frame.tkraise()
        self.skip_countdown = False
        self.timer_running = True
        self.update_timer()

    def start_now(self):
        """
        Skip the countdown and show the live display straight away.

        The schedule itself does not move. Until the scheduled start arrives the
        target slide simply sits at 1, so the finish time stays exactly what the
        confirmation screen showed.
        """
        self.skip_countdown = True

    def update_timer(self):
        """
        Update the timer display every second, showing elapsed time and ideal slide.
        If waiting for a future start time, show a waiting message.
        """
        if not self.timer_running:
            return
        now = datetime.now()
        if now < self.start_time and not self.skip_countdown:
            # Waiting for the scheduled start time
            self.timer_label.config(text=f'Waiting to start at {fmt_clock(self.start_time)}')
            self.time_remaining_label.config(text='')
            self.target_slide_label.config(text='')
            self.slide_number_label.config(text='--')
            self.elapsed_label.config(text='')
            # Show current time in a smaller font below
            if not hasattr(self, 'current_time_label'):
                self.current_time_label = tk.Label(self.timer_body, text='',
                                                   font=('Helvetica Neue', 10), bg='white', fg=INK)
                self.current_time_label.pack()
            self.current_time_label.config(text=f'(Current time: {fmt_clock(now)})')
            # Show 'preso to begin in' in small font
            minutes_to_start = int((self.start_time - now).total_seconds() // 60)
            seconds_to_start = int((self.start_time - now).total_seconds() % 60)
            if not hasattr(self, 'begin_in_label'):
                self.begin_in_label = tk.Label(self.timer_body, text='',
                                               font=('Helvetica Neue', 14), bg='white', fg=INK)
                self.begin_in_label.pack()
            if minutes_to_start > 0:
                self.begin_in_label.config(text=f'preso to begin in {minutes_to_start} min')
            else:
                self.begin_in_label.config(text=f'preso to begin in {seconds_to_start} sec')
            # Let Mike jump straight to the live display rather than watch a countdown
            if not hasattr(self, 'start_now_button'):
                self.start_now_button = tk.Button(self.timer_body, text='Start now',
                                                  font=('Helvetica Neue', 13),
                                                  command=self.start_now)
                self.start_now_button.pack(pady=(14, 0))
            self.root.after(1000, self.update_timer)
            return
        # Remove the current time and begin_in labels if they exist
        if hasattr(self, 'current_time_label'):
            self.current_time_label.destroy()
            del self.current_time_label
        if hasattr(self, 'begin_in_label'):
            self.begin_in_label.destroy()
            del self.begin_in_label
        if hasattr(self, 'start_now_button'):
            self.start_now_button.destroy()
            del self.start_now_button
        # Clear the waiting message
        self.timer_label.config(text='')
        # Restore the target slide label
        self.target_slide_label.config(text='Target slide:')
        elapsed = now - self.start_time
        total_seconds = self.effective_duration * 60
        elapsed_seconds = elapsed.total_seconds()
        if elapsed_seconds < 0:
            elapsed_seconds = 0
        if elapsed_seconds > total_seconds:
            elapsed_seconds = total_seconds
            self.timer_running = False
        elapsed_str = str(timedelta(seconds=int(elapsed_seconds)))
        self.elapsed_label.config(text=f'Elapsed: {elapsed_str}')
        ideal_slide = self.calculate_ideal_slide(elapsed_seconds, total_seconds, self.total_slides)
        self.slide_number_label.config(text=str(ideal_slide))
        self.time_remaining_label.config(
            text=f'Time Remaining: {str(timedelta(seconds=int(total_seconds - elapsed_seconds)))}')
        if self.timer_running:
            self.root.after(1000, self.update_timer)


if __name__ == '__main__':
    root = tk.Tk()
    app = PrezzotimerApp(root)
    root.mainloop()
