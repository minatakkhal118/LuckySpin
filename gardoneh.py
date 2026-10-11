import math
import os
import random
import struct
import tkinter as tk
import wave
import winsound
from tkinter import filedialog, messagebox


class ProfessionalWheel:

    def __init__(self, root):

        self.root = root

        # =====================================================
        # تنظیمات پنجره
        # =====================================================

        self.root.title("🎡 Professional Wheel of Names")
        self.root.geometry("1250x850")
        self.root.minsize(1050, 720)
        self.root.configure(bg="#111318")

        # =====================================================
        # متغیرهای اصلی
        # =====================================================

        self.names = []
        self.winners = []

        self.angle = 0.0

        self.spinning = False
        self.current_winner = None

        self.last_tick_index = -1

        self.tick_sound = None
        self.winner_sound = None

        self.fullscreen = False

        # =====================================================
        # رنگ‌ها
        # =====================================================

        self.BG = "#111318"
        self.PANEL = "#1D2027"
        self.PANEL_2 = "#252932"

        self.WHITE = "#FFFFFF"
        self.GRAY = "#9AA0AA"

        self.YELLOW = "#FFD54A"
        self.GREEN = "#35C759"
        self.RED = "#FF4D5A"
        self.BLUE = "#4D8DFF"

        # =====================================================
        # رنگ‌های گردونه
        # =====================================================

        self.wheel_colors = [
            "#FF4757",
            "#3742FA",
            "#FFA502",
            "#2ED573",
            "#A55EEA",
            "#18DCFF",
            "#FF6B81",
            "#1E90FF",
            "#FFC312",
            "#05C46B",
            "#C56CF0",
            "#12CBC4",
            "#ED4C67",
            "#9980FA",
            "#F79F1F",
            "#009432",
            "#5758BB",
            "#D980FA",
            "#FDA7DF",
            "#1289A7"
        ]

        # =====================================================
        # ساخت صدا
        # =====================================================

        self.create_sounds()

        # =====================================================
        # ساخت رابط کاربری
        # =====================================================

        self.create_interface()

        # =====================================================
        # اسامی نمونه
        # =====================================================

        initial_names = [
            "علی",
            "رضا",
            "محمد",
            "حسن",
            "مهدی",
            "امیر"
        ]

        for name in initial_names:
            self.add_name_internal(name)

        # =====================================================
        # رسم اولیه
        # =====================================================

        self.root.after(
            200,
            self.draw_wheel
        )

        self.canvas.bind(
            "<Configure>",
            lambda event: self.draw_wheel()
        )

        # =====================================================
        # کلیدهای میانبر
        # =====================================================

        # مهم:
        # Space دیگر مستقیماً start_spin را اجرا نمی‌کند.
        # ابتدا بررسی می‌کنیم که کاربر در حال تایپ نباشد.

        self.root.bind(
            "<space>",
            self.handle_space
        )

        self.root.bind(
            "<F11>",
            self.toggle_fullscreen
        )

        self.root.bind(
            "<Escape>",
            self.exit_fullscreen
        )

    # =========================================================
    # مدیریت کلید Space
    # =========================================================

    def handle_space(self, event=None):

        focused = self.root.focus_get()

        # اگر کاربر داخل کادر تایپ نام یا Text چندخطی باشد،
        # Space باید به صورت عادی وارد متن شود.

        if isinstance(
            focused,
            (tk.Entry, tk.Text)
        ):
            return

        # در غیر این صورت Space گردونه را می‌چرخاند.

        self.start_spin()

        # جلوگیری از رفتار پیش‌فرض Space
        return "break"

    # =========================================================
    # ساخت صداها
    # =========================================================

    def create_sounds(self):

        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.tick_sound = os.path.join(
            base_path,
            "wheel_tick.wav"
        )

        self.winner_sound = os.path.join(
            base_path,
            "wheel_winner.wav"
        )

        if not os.path.exists(
            self.tick_sound
        ):
            self.generate_tick_sound(
                self.tick_sound
            )

        if not os.path.exists(
            self.winner_sound
        ):
            self.generate_winner_sound(
                self.winner_sound
            )

    # =========================================================
    # تولید صدای تیک
    # =========================================================

    def generate_tick_sound(
        self,
        filename
    ):

        sample_rate = 44100
        duration = 0.045

        samples = int(
            sample_rate * duration
        )

        data = []

        for i in range(samples):

            t = i / sample_rate

            f1 = 1700
            f2 = 2900

            envelope = math.exp(
                -70 * t
            )

            value = (
                0.65 *
                math.sin(
                    2 *
                    math.pi *
                    f1 *
                    t
                )
                +
                0.25 *
                math.sin(
                    2 *
                    math.pi *
                    f2 *
                    t
                )
            )

            value *= envelope

            value = max(
                -1,
                min(
                    1,
                    value
                )
            )

            data.append(
                struct.pack(
                    "<h",
                    int(
                        value *
                        32767
                    )
                )
            )

        with wave.open(
            filename,
            "wb"
        ) as wav:

            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)

            wav.writeframes(
                b"".join(data)
            )

    # =========================================================
    # تولید صدای برنده
    # =========================================================

    def generate_winner_sound(
        self,
        filename
    ):

        sample_rate = 44100
        duration = 0.9

        notes = [
            523.25,
            659.25,
            783.99,
            1046.50
        ]

        data = []

        for i in range(
            int(
                sample_rate *
                duration
            )
        ):

            t = i / sample_rate

            note_index = min(
                int(t / 0.18),
                len(notes) - 1
            )

            frequency = notes[
                note_index
            ]

            local_t = (
                t -
                note_index * 0.18
            )

            envelope = (
                min(
                    1,
                    local_t * 30
                )
                *
                math.exp(
                    -2.5 *
                    local_t
                )
            )

            value = (
                math.sin(
                    2 *
                    math.pi *
                    frequency *
                    t
                )
                *
                envelope
                *
                0.55
            )

            value = max(
                -1,
                min(
                    1,
                    value
                )
            )

            data.append(
                struct.pack(
                    "<h",
                    int(
                        value *
                        32767
                    )
                )
            )

        with wave.open(
            filename,
            "wb"
        ) as wav:

            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)

            wav.writeframes(
                b"".join(data)
            )

    # =========================================================
    # رابط کاربری
    # =========================================================

    def create_interface(self):

        # =====================================================
        # عنوان
        # =====================================================

        title_frame = tk.Frame(
            self.root,
            bg=self.BG
        )

        title_frame.pack(
            fill="x",
            pady=(15, 5)
        )

        tk.Label(
            title_frame,
            text="🎡 گردونه شانس",
            font=(
                "Tahoma",
                28,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.BG
        ).pack()

        tk.Label(
            title_frame,
            text="برای چرخاندن گردونه روی آن کلیک کنید",
            font=(
                "Tahoma",
                11
            ),
            fg=self.GRAY,
            bg=self.BG
        ).pack(
            pady=(3, 0)
        )

        # =====================================================
        # بدنه اصلی
        # =====================================================

        main = tk.Frame(
            self.root,
            bg=self.BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        # =====================================================
        # پنل سمت چپ
        # =====================================================

        left = tk.Frame(
            main,
            bg=self.PANEL,
            width=330
        )

        left.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )

        left.pack_propagate(False)

        tk.Label(
            left,
            text="👥 شرکت‌کنندگان",
            font=(
                "Tahoma",
                17,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.PANEL
        ).pack(
            pady=(18, 10)
        )

        # =====================================================
        # کادر نام
        # =====================================================

        self.name_entry = tk.Entry(
            left,
            font=(
                "Tahoma",
                13
            ),
            justify="center",
            relief="flat",
            bg="white",
            fg="#222222"
        )

        self.name_entry.pack(
            padx=20,
            fill="x",
            ipady=8
        )

        self.name_entry.bind(
            "<Return>",
            lambda event:
            self.add_name()
        )

        # =====================================================
        # دکمه افزودن
        # =====================================================

        self.create_button(
            left,
            "➕ افزودن نام",
            self.add_name,
            self.GREEN
        ).pack(
            padx=20,
            pady=8,
            fill="x"
        )

        # =====================================================
        # ورود چند نام
        # =====================================================

        tk.Label(
            left,
            text="چند نام را یکجا وارد کنید:",
            font=(
                "Tahoma",
                10
            ),
            fg=self.GRAY,
            bg=self.PANEL
        ).pack(
            pady=(5, 4)
        )

        self.multi_text = tk.Text(
            left,
            height=4,
            font=(
                "Tahoma",
                11
            ),
            relief="flat",
            bg="white",
            fg="#222222"
        )

        self.multi_text.pack(
            padx=20,
            fill="x"
        )

        self.create_button(
            left,
            "➕ افزودن همه",
            self.add_multiple_names,
            self.BLUE
        ).pack(
            padx=20,
            pady=7,
            fill="x"
        )

        # =====================================================
        # تعداد
        # =====================================================

        self.count_label = tk.Label(
            left,
            text="تعداد شرکت‌کنندگان: 0",
            font=(
                "Tahoma",
                10,
                "bold"
            ),
            fg=self.YELLOW,
            bg=self.PANEL
        )

        self.count_label.pack(
            pady=5
        )

        # =====================================================
        # لیست اسامی
        # =====================================================

        list_frame = tk.Frame(
            left,
            bg=self.PANEL
        )

        list_frame.pack(
            padx=20,
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            list_frame
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.listbox = tk.Listbox(
            list_frame,
            font=(
                "Tahoma",
                11
            ),
            justify="center",
            bg="#FFFFFF",
            fg="#222222",
            selectbackground=self.BLUE,
            selectforeground="white",
            activestyle="none",
            yscrollcommand=
            scrollbar.set
        )

        self.listbox.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.listbox.yview
        )

        self.listbox.bind(
            "<Double-Button-1>",
            self.remove_name
        )

        # =====================================================
        # حذف
        # =====================================================

        self.create_button(
            left,
            "🗑 حذف نام انتخاب‌شده",
            self.remove_name,
            self.RED
        ).pack(
            padx=20,
            pady=(8, 4),
            fill="x"
        )

        self.create_button(
            left,
            "🧹 حذف همه",
            self.clear_all,
            "#555A65"
        ).pack(
            padx=20,
            pady=4,
            fill="x"
        )

        # =====================================================
        # حذف خودکار برنده
        # =====================================================

        self.remove_winner_var = tk.BooleanVar(
            value=False
        )

        tk.Checkbutton(
            left,
            text="برنده بعد از انتخاب حذف شود",
            variable=self.remove_winner_var,
            font=(
                "Tahoma",
                10
            ),
            fg=self.WHITE,
            bg=self.PANEL,
            activebackground=self.PANEL,
            activeforeground=self.WHITE,
            selectcolor="#30343C"
        ).pack(
            pady=7
        )

        # =====================================================
        # ذخیره / بارگذاری
        # =====================================================

        save_load = tk.Frame(
            left,
            bg=self.PANEL
        )

        save_load.pack(
            fill="x",
            padx=20,
            pady=(3, 15)
        )

        self.create_button(
            save_load,
            "💾 ذخیره",
            self.save_names,
            "#6C5CE7"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 3)
        )

        self.create_button(
            save_load,
            "📂 بارگذاری",
            self.load_names,
            "#0984E3"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(3, 0)
        )

        # =====================================================
        # قسمت گردونه
        # =====================================================

        wheel_area = tk.Frame(
            main,
            bg=self.BG
        )

        wheel_area.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            wheel_area,
            bg=self.BG,
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.canvas.bind(
            "<Button-1>",
            self.start_spin
        )

        # =====================================================
        # نتیجه
        # =====================================================

        result_frame = tk.Frame(
            self.root,
            bg=self.BG
        )

        result_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        self.result_label = tk.Label(
            result_frame,
            text="برای شروع روی گردونه کلیک کنید 🎡",
            font=(
                "Tahoma",
                20,
                "bold"
            ),
            fg=self.YELLOW,
            bg=self.BG
        )

        self.result_label.pack(
            pady=3
        )

        # =====================================================
        # دکمه چرخش
        # =====================================================

        self.spin_button = tk.Button(
            result_frame,
            text="🎡  چرخاندن گردونه",
            command=self.start_spin,
            font=(
                "Tahoma",
                13,
                "bold"
            ),
            bg=self.YELLOW,
            fg="#181818",
            activebackground="#FFC107",
            relief="flat",
            cursor="hand2",
            padx=45,
            pady=9
        )

        self.spin_button.pack()

    # =========================================================
    # ساخت دکمه
    # =========================================================

    def create_button(
        self,
        parent,
        text,
        command,
        color
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(
                "Tahoma",
                10,
                "bold"
            ),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=7
        )

    # =========================================================
    # افزودن داخلی
    # =========================================================

    def add_name_internal(
        self,
        name
    ):

        name = name.strip()

        if not name:
            return

        self.names.append(name)

        self.listbox.insert(
            tk.END,
            name
        )

        self.update_count()

    # =========================================================
    # افزودن نام
    # =========================================================

    def add_name(self):

        if self.spinning:
            return

        name = (
            self.name_entry
            .get()
            .strip()
        )

        if not name:

            messagebox.showwarning(
                "نام خالی",
                "لطفاً یک نام وارد کنید."
            )

            return

        self.add_name_internal(
            name
        )

        self.name_entry.delete(
            0,
            tk.END
        )

        self.name_entry.focus()

        self.draw_wheel()

    # =========================================================
    # افزودن چند نام
    # =========================================================

    def add_multiple_names(self):

        if self.spinning:
            return

        text = (
            self.multi_text
            .get(
                "1.0",
                tk.END
            )
            .strip()
        )

        if not text:
            return

        count = 0

        for line in text.splitlines():

            name = line.strip()

            if name:

                self.add_name_internal(
                    name
                )

                count += 1

        self.multi_text.delete(
            "1.0",
            tk.END
        )

        self.draw_wheel()

        self.result_label.config(
            text=f"{count} نام اضافه شد"
        )

    # =========================================================
    # حذف نام
    # =========================================================

    def remove_name(
        self,
        event=None
    ):

        if self.spinning:
            return

        selection = (
            self.listbox
            .curselection()
        )

        if not selection:

            messagebox.showwarning(
                "انتخاب نام",
                "ابتدا یک نام را انتخاب کنید."
            )

            return

        index = selection[0]

        deleted_name = self.names[
            index
        ]

        self.names.pop(
            index
        )

        self.listbox.delete(
            index
        )

        self.update_count()

        self.draw_wheel()

        self.result_label.config(
            text=f"«{deleted_name}» حذف شد"
        )

    # =========================================================
    # حذف همه
    # =========================================================

    def clear_all(self):

        if self.spinning:
            return

        if not self.names:
            return

        answer = messagebox.askyesno(
            "حذف همه",
            "آیا از حذف تمام نام‌ها مطمئن هستید؟"
        )

        if not answer:
            return

        self.names.clear()

        self.listbox.delete(
            0,
            tk.END
        )

        self.update_count()

        self.draw_wheel()

        self.result_label.config(
            text="همه نام‌ها حذف شدند"
        )

    # =========================================================
    # تعداد
    # =========================================================

    def update_count(self):

        self.count_label.config(
            text=
            f"تعداد شرکت‌کنندگان: {len(self.names)}"
        )

    # =========================================================
    # رسم گردونه
    # =========================================================

    def draw_wheel(self):

        self.canvas.delete(
            "all"
        )

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 300 or height < 300:
            return

        cx = width / 2
        cy = height / 2

        radius = (
            min(width, height)
            / 2
            - 55
        )

        # =====================================================
        # اگر اسمی وجود ندارد
        # =====================================================

        if not self.names:

            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill="#292D35",
                outline="#656B78",
                width=4
            )

            self.canvas.create_text(
                cx,
                cy,
                text="نامی وارد نشده است",
                fill=self.WHITE,
                font=(
                    "Tahoma",
                    20,
                    "bold"
                )
            )

            self.draw_pointer(
                cx,
                cy,
                radius
            )

            return

        # =====================================================
        # تعداد
        # =====================================================

        count = len(self.names)

        slice_angle = (
            360 / count
        )

        # =====================================================
        # سایه
        # =====================================================

        shadow_offset = 9

        self.canvas.create_oval(
            cx - radius + shadow_offset,
            cy - radius + shadow_offset,
            cx + radius + shadow_offset,
            cy + radius + shadow_offset,
            fill="#08090C",
            outline=""
        )

        # =====================================================
        # بخش‌های گردونه
        # =====================================================

        for i, name in enumerate(
            self.names
        ):

            start = (
                self.angle
                + i * slice_angle
            )

            color = (
                self.wheel_colors[
                    i %
                    len(
                        self.wheel_colors
                    )
                ]
            )

            self.canvas.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=start,
                extent=slice_angle,
                fill=color,
                outline="#FFFFFF",
                width=2
            )

            # =================================================
            # موقعیت متن
            # =================================================

            middle = (
                start
                + slice_angle / 2
            )

            rad = math.radians(
                middle
            )

            text_radius = (
                radius * 0.62
            )

            tx = (
                cx
                + math.cos(rad)
                * text_radius
            )

            ty = (
                cy
                - math.sin(rad)
                * text_radius
            )

            # =================================================
            # اندازه متن
            # =================================================

            if count <= 6:
                size = 18

            elif count <= 10:
                size = 15

            elif count <= 16:
                size = 12

            elif count <= 24:
                size = 10

            else:
                size = 8

            display_name = name

            if len(display_name) > 16:

                display_name = (
                    display_name[:14]
                    + "..."
                )

            self.canvas.create_text(
                tx,
                ty,
                text=display_name,
                fill="white",
                font=(
                    "Tahoma",
                    size,
                    "bold"
                )
            )

        # =====================================================
        # حاشیه بیرونی
        # =====================================================

        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="#FFFFFF",
            width=5
        )

        # =====================================================
        # مرکز
        # =====================================================

        center_radius = min(
            68,
            radius * 0.20
        )

        self.canvas.create_oval(
            cx - center_radius,
            cy - center_radius,
            cx + center_radius,
            cy + center_radius,
            fill="#17191F",
            outline="#FFFFFF",
            width=4
        )

        self.canvas.create_oval(
            cx - center_radius + 7,
            cy - center_radius + 7,
            cx + center_radius - 7,
            cy + center_radius - 7,
            fill="#FFD54A",
            outline=""
        )

        self.canvas.create_text(
            cx,
            cy,
            text="SPIN",
            fill="#17191F",
            font=(
                "Arial",
                15,
                "bold"
            )
        )

        # =====================================================
        # عقربه
        # =====================================================

        self.draw_pointer(
            cx,
            cy,
            radius
        )

    # =========================================================
    # رسم عقربه
    # =========================================================

    def draw_pointer(
        self,
        cx,
        cy,
        radius
    ):

        y = (
            cy
            - radius
            - 8
        )

        self.canvas.create_polygon(

            cx - 24,
            y - 24,

            cx + 24,
            y - 24,

            cx,
            y + 28,

            fill="#FFD54A",

            outline="#111111",

            width=3
        )

    # =========================================================
    # تشخیص عبور از بخش
    # =========================================================

    def check_tick(self):

        if len(self.names) < 2:
            return

        slice_angle = (
            360 / len(self.names)
        )

        normalized_angle = (
            self.angle % 360
        )

        current_index = int(
            normalized_angle
            / slice_angle
        )

        if (
            current_index
            != self.last_tick_index
        ):

            self.last_tick_index = (
                current_index
            )

            try:

                winsound.PlaySound(
                    self.tick_sound,
                    winsound.SND_FILENAME
                    |
                    winsound.SND_ASYNC
                    |
                    winsound.SND_NODEFAULT
                )

            except Exception:  # noqa: BLE001, S110
                pass

    # =========================================================
    # شروع چرخش
    # =========================================================

    def start_spin(
        self,
        event=None
    ):

        if self.spinning:
            return

        if len(self.names) < 2:

            messagebox.showwarning(
                "تعداد نام‌ها",
                "حداقل دو نام برای چرخش لازم است."
            )

            return

        self.spinning = True

        self.spin_button.config(
            state="disabled"
        )

        self.result_label.config(
            text="🎡 در حال چرخش..."
        )

        # =====================================================
        # انتخاب برنده
        # =====================================================

        winner_index = random.randrange(
            len(self.names)
        )

        slice_angle = (
            360 / len(self.names)
        )

        # =====================================================
        # زاویه نهایی
        # =====================================================

        desired_angle = (
            90
            -
            (
                winner_index
                * slice_angle
                +
                slice_angle / 2
            )
        )

        current = (
            self.angle % 360
        )

        difference = (
            desired_angle
            - current
        ) % 360

        # =====================================================
        # تعداد دورهای تصادفی
        # =====================================================

        full_rotations = random.randint(
            7,
            11
        )

        target_angle = (
            self.angle
            +
            full_rotations * 360
            +
            difference
        )

        # =====================================================
        # شروع تیک
        # =====================================================

        self.last_tick_index = -1

        self.animate_spin(
            target_angle,
            winner_index
        )

    # =========================================================
    # انیمیشن چرخش
    # =========================================================

    def animate_spin(
        self,
        target_angle,
        winner_index
    ):

        start_angle = self.angle

        total_rotation = (
            target_angle
            - start_angle
        )

        duration = 6500
        steps = 210

        current_step = 0

        def animate():

            nonlocal current_step

            current_step += 1

            progress = (
                current_step
                / steps
            )

            # =================================================
            # کاهش سرعت نرم
            # =================================================

            eased = (
                1
                -
                (1 - progress) ** 4
            )

            self.angle = (
                start_angle
                +
                total_rotation
                * eased
            )

            # =================================================
            # صدای تیک
            # =================================================

            self.check_tick()

            # =================================================
            # رسم
            # =================================================

            self.draw_wheel()

            # =================================================
            # ادامه
            # =================================================

            if current_step < steps:

                delay = max(
                    10,
                    int(
                        duration
                        / steps
                    )
                )

                self.root.after(
                    delay,
                    animate
                )

            else:

                self.angle = (
                    target_angle % 360
                )

                self.draw_wheel()

                self.spinning = False

                self.spin_button.config(
                    state="normal"
                )

                self.current_winner = (
                    self.names[
                        winner_index
                    ]
                )

                self.finish_spin(
                    self.current_winner
                )

        animate()

    # =========================================================
    # پایان چرخش
    # =========================================================

    def finish_spin(
        self,
        winner
    ):

        self.winners.append(
            winner
        )

        # =====================================================
        # صدای برنده
        # =====================================================

        try:

            winsound.PlaySound(
                self.winner_sound,
                winsound.SND_FILENAME
                |
                winsound.SND_ASYNC
                |
                winsound.SND_NODEFAULT
            )

        except Exception:  # noqa: BLE001, S110
            pass

        # =====================================================
        # نمایش نتیجه
        # =====================================================

        self.result_label.config(
            text=f"🏆 برنده: {winner}",
            fg=self.YELLOW,
            font=(
                "Tahoma",
                24,
                "bold"
            )
        )

        # =====================================================
        # پنجره برنده
        # =====================================================

        self.show_winner_window(
            winner
        )

        # =====================================================
        # حذف خودکار
        # =====================================================

        if self.remove_winner_var.get():

            try:

                index = self.names.index(
                    winner
                )

                self.names.pop(
                    index
                )

                self.listbox.delete(
                    index
                )

                self.update_count()

                self.draw_wheel()

            except ValueError:

                pass

    # =========================================================
    # پنجره برنده
    # =========================================================

    def show_winner_window(
        self,
        winner
    ):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "🎉 برنده مشخص شد"
        )

        window.geometry(
            "600x420"
        )

        window.configure(
            bg="#111318"
        )

        window.resizable(
            False,
            False
        )

        window.update_idletasks()

        sw = window.winfo_screenwidth()
        sh = window.winfo_screenheight()

        x = (
            sw - 600
        ) // 2

        y = (
            sh - 420
        ) // 2

        window.geometry(
            f"600x420+{x}+{y}"
        )

        tk.Label(
            window,
            text="🎉",
            font=(
                "Arial",
                55
            ),
            fg=self.YELLOW,
            bg="#111318"
        ).pack(
            pady=(18, 0)
        )

        tk.Label(
            window,
            text="برنده مشخص شد!",
            font=(
                "Tahoma",
                28,
                "bold"
            ),
            fg=self.YELLOW,
            bg="#111318"
        ).pack(
            pady=5
        )

        frame = tk.Frame(
            window,
            bg="#252932",
            highlightbackground=self.YELLOW,
            highlightthickness=3
        )

        frame.pack(
            padx=45,
            pady=18,
            fill="x"
        )

        tk.Label(
            frame,
            text=winner,
            font=(
                "Tahoma",
                34,
                "bold"
            ),
            fg=self.WHITE,
            bg="#252932"
        ).pack(
            pady=20
        )

        tk.Button(
            window,
            text="باشه",
            command=window.destroy,
            font=(
                "Tahoma",
                13,
                "bold"
            ),
            bg=self.GREEN,
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=55,
            pady=10
        ).pack(
            pady=10
        )

    # =========================================================
    # ذخیره اسامی
    # =========================================================

    def save_names(self):

        if not self.names:

            messagebox.showinfo(
                "ذخیره",
                "لیست اسامی خالی است."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="ذخیره اسامی",
            defaultextension=".txt",
            filetypes=[
                (
                    "Text File",
                    "*.txt"
                )
            ]
        )

        if not filename:
            return

        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.writelines(name + "\n" for name in self.names)

            messagebox.showinfo(
                "ذخیره شد",
                "لیست اسامی با موفقیت ذخیره شد."
            )

        except Exception as e:  # noqa: BLE001

            messagebox.showerror(
                "خطا",
                str(e)
            )

    # =========================================================
    # بارگذاری اسامی
    # =========================================================

    def load_names(self):

        if self.spinning:
            return

        filename = filedialog.askopenfilename(
            title="بارگذاری اسامی",
            filetypes=[
                (
                    "Text File",
                    "*.txt"
                )
            ]
        )

        if not filename:
            return

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                lines = file.readlines()

            self.names.clear()

            self.listbox.delete(
                0,
                tk.END
            )

            for line in lines:

                name = line.strip()

                if name:

                    self.add_name_internal(
                        name
                    )

            self.draw_wheel()

            self.result_label.config(
                text="لیست با موفقیت بارگذاری شد"
            )

        except Exception as e:  # noqa: BLE001

            messagebox.showerror(
                "خطا",
                str(e)
            )

    # =========================================================
    # تمام صفحه
    # =========================================================

    def toggle_fullscreen(
        self,
        event=None
    ):

        self.fullscreen = (
            not self.fullscreen
        )

        self.root.attributes(
            "-fullscreen",
            self.fullscreen
        )

    # =========================================================
    # خروج از تمام صفحه
    # =========================================================

    def exit_fullscreen(
        self,
        event=None
    ):

        self.fullscreen = False

        self.root.attributes(
            "-fullscreen",
            False
        )


# =============================================================
# اجرای برنامه
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ProfessionalWheel(
        root
    )

    root.mainloop()