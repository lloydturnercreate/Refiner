"""
CustomTkinter-based UI with tabs for conversion and compression.
"""

import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from utils import normalize_extension, get_valid_output_formats, generate_output_filename, validate_file_path, convert_size
from converters import convert_file
from compressors import compress_file, simulate_compression
from logger import logger
from constants import (
    BACKGROUND_PRIMARY as BG_PRIMARY,
    BACKGROUND_SECONDARY as BG_SECONDARY,
    SURFACE_PRIMARY,
    SURFACE_SECONDARY,
    SURFACE_ELEVATED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    ACCENT_PRIMARY,
    ACCENT_SECONDARY as ACCENT_HOVER,
    ACCENT_WARNING,
    BORDER_PRIMARY,
    BORDER_SECONDARY,
    WINDOW_TITLE,
    WINDOW_SIZE,
    WINDOW_RESIZABLE,
    APPEARANCE_MODE,
    COLOR_THEME
)

# Global widget references used by event handlers
entry_input = None
entry_output = None
format_dropdown = None
conversion_label = None
convert_button = None
progress_convert = None
entry_input_comp = None
entry_output_comp = None
slider_comp = None
slider_level_label = None
preview_pane_conv = None
preview_label_conv = None
preview_pane_comp = None
preview_label_comp = None
_gif_anim_job = None
fps_slider = None
fps_level_label = None
fps_row_sep = None
fps_row_label = None
fps_row_frame = None
label_predicted = None
compress_button = None
progress_compress = None
prediction_job_id = None
_convert_anim_job = None
_compress_anim_job = None
_convert_anim_dir = [1]
_compress_anim_dir = [1]
root = None

# Maps display label → file extension and vice versa
_FORMAT_LABELS = {
    "JPG": ".jpg", "PNG": ".png", "WEBP": ".webp", "AVIF": ".avif",
    "BMP": ".bmp", "SVG": ".svg",
    "MP4": ".mp4", "WEBM": ".webm", "MOV": ".mov", "GIF": ".gif",
}
_EXT_TO_LABEL = {v: k for k, v in _FORMAT_LABELS.items()}


def browse_file(entry_widget):
    """Open file picker, populate entry, and refresh the format dropdown."""
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_path)
        _refresh_format_dropdown(file_path)
        update_conversion_label()
        _render_preview(file_path, preview_label_conv, preview_pane_conv)


def _refresh_format_dropdown(input_path: str):
    """Repopulate the format dropdown with valid output formats for input_path."""
    valid_exts = get_valid_output_formats(input_path)
    labels = [_EXT_TO_LABEL[e] for e in valid_exts if e in _EXT_TO_LABEL]
    if not labels:
        labels = ["—"]
    format_dropdown.configure(values=labels, state="normal")
    format_dropdown.set(labels[0])
    on_format_changed(labels[0])


def on_format_changed(label: str):
    """Update the output path extension when the user picks a different format."""
    input_path = entry_input.get()
    if not input_path:
        return
    ext = _FORMAT_LABELS.get(label)
    if not ext:
        return
    base = os.path.splitext(input_path)[0]
    suggested = base + ext
    entry_output.delete(0, ctk.END)
    entry_output.insert(0, suggested)
    update_conversion_label()


def browse_output(entry_widget):
    """Open a save dialog pre-set to the format chosen in the dropdown."""
    input_path = entry_input.get()
    if not input_path:
        messagebox.showerror("Error", "Please select an input file first")
        return
    is_valid, error_msg = validate_file_path(input_path)
    if not is_valid:
        messagebox.showerror("Error", f"Invalid input file: {error_msg}")
        return
    label = format_dropdown.get()
    ext = _FORMAT_LABELS.get(label, ".png")
    base = os.path.splitext(os.path.basename(input_path))[0]
    initial_file = base + ext
    file_path = filedialog.asksaveasfilename(
        defaultextension=ext,
        initialfile=initial_file,
        initialdir=os.path.dirname(input_path),
    )
    if file_path:
        # Enforce the selected extension even if user typed something else
        chosen_ext = normalize_extension(os.path.splitext(file_path)[1])
        if chosen_ext != ext:
            file_path = os.path.splitext(file_path)[0] + ext
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_path)
        update_conversion_label()


def update_conversion_label():
    """Update the converter label to show input→output filenames."""
    input_path = entry_input.get()
    output_path = entry_output.get()
    if input_path and output_path:
        conversion_label.configure(text=f"{os.path.basename(input_path)} → {os.path.basename(output_path)}")
    elif input_path:
        conversion_label.configure(text=f"{os.path.basename(input_path)} → --")
    else:
        conversion_label.configure(text="-- → --")


def process_conversion():
    """Validate inputs and run file conversion on a background thread."""
    input_path = entry_input.get()
    output_path = entry_output.get()
    if not input_path or not output_path:
        messagebox.showerror("Error", "Please select input and output files")
        return
    is_valid, error_msg = validate_file_path(input_path)
    if not is_valid:
        messagebox.showerror("Error", f"Invalid input file: {error_msg}")
        return
    input_ext = normalize_extension(os.path.splitext(input_path)[1])
    format_selected = normalize_extension(os.path.splitext(output_path)[1])
    if format_selected == ".svg" and input_ext != ".svg":
        messagebox.showerror("Error", "Converting to SVG is not supported.")
        return

    _set_convert_busy(True)

    def _run():
        logger.log_conversion_start(input_path, output_path)
        try:
            convert_file(input_path, output_path)
            logger.log_conversion_success(input_path, output_path)
            root.after(0, lambda: _on_convert_done(
                True, os.path.basename(input_path), os.path.basename(output_path), None
            ))
        except Exception as e:
            logger.log_conversion_error(input_path, output_path, str(e))
            root.after(0, lambda err=str(e): _on_convert_done(False, None, None, err))

    threading.Thread(target=_run, daemon=True).start()


def _set_convert_busy(busy: bool):
    """Disable/enable the Convert button, label, and progress bar."""
    if busy:
        convert_button.configure(text="Converting…", state="disabled")
        _start_progress(progress_convert, _convert_anim_dir, "_convert_anim_job")
    else:
        convert_button.configure(text="Convert", state="normal")
        _stop_progress(progress_convert, "_convert_anim_job")


def _on_convert_done(success: bool, input_name: str, output_name: str, error: str):
    """Called on the main thread when a conversion finishes."""
    _set_convert_busy(False)
    if success:
        messagebox.showinfo("Success", f"Converted {input_name} to {output_name}")
    else:
        messagebox.showerror("Error", f"Conversion failed: {error}")


def browse_file_comp(entry_widget):
    """Open file picker for compressor and set default output name."""
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_path)
        output_file = generate_output_filename(file_path)
        entry_output_comp.delete(0, ctk.END)
        entry_output_comp.insert(0, output_file)
        _update_fps_row(file_path)
        schedule_prediction_update()
        _render_preview(file_path, preview_label_comp, preview_pane_comp)


def _update_fps_row(file_path: str):
    """Show/hide and configure the FPS row based on whether input is a GIF."""
    is_gif = normalize_extension(os.path.splitext(file_path)[1]) == ".gif"
    if is_gif:
        fps_row_sep.grid()
        fps_row_label.grid()
        fps_row_frame.grid()
        fps_slider.configure(state="normal")
        try:
            from compressors import VideoCompressor
            detected_fps = VideoCompressor()._get_source_fps(file_path)
            clamped = max(1, min(60, round(detected_fps)))
            fps_slider.set(clamped)
            fps_level_label.configure(text=f"{clamped} fps")
        except Exception:
            fps_slider.set(15)
            fps_level_label.configure(text="15 fps")
    else:
        fps_slider.configure(state="disabled")
        fps_row_sep.grid_remove()
        fps_row_label.grid_remove()
        fps_row_frame.grid_remove()
    root.update_idletasks()
    root.geometry(f"450x{root.winfo_reqheight()}")


_PREVIEW_HEIGHT = 200
_IMAGE_EXTS = {'.png', '.jpg', '.webp', '.bmp', '.avif'}


def _show_preview(pane):
    pane.configure(height=_PREVIEW_HEIGHT)
    pane.pack_configure(pady=(0, 12))
    root.update_idletasks()
    root.geometry(f"450x{root.winfo_reqheight()}")


def _hide_preview(pane):
    pane.configure(height=0)
    pane.pack_configure(pady=0)
    root.update_idletasks()
    root.geometry(f"450x{root.winfo_reqheight()}")


def _render_preview(path: str, label_widget, pane_widget):
    """Render a file preview. Step 1: raster images only."""
    global _gif_anim_job
    ext = normalize_extension(os.path.splitext(path)[1])

    # Stop any running GIF animation
    if _gif_anim_job is not None:
        root.after_cancel(_gif_anim_job)
        _gif_anim_job = None

    _VIDEO_EXTS = {'.mp4', '.webm', '.mov'}
    _PREVIEWABLE = _IMAGE_EXTS | {'.svg', '.gif'} | _VIDEO_EXTS
    if ext not in _PREVIEWABLE:
        _hide_preview(pane_widget)
        return

    try:
        from PIL import Image as PILImage
        pane_w = max(pane_widget.winfo_width(), 410)

        if ext == '.svg':
            import cairosvg
            from io import BytesIO
            png_bytes = cairosvg.svg2png(url=path, output_width=820, output_height=_PREVIEW_HEIGHT * 2)
            img = PILImage.open(BytesIO(png_bytes)).convert("RGBA")
            img.thumbnail((pane_w, _PREVIEW_HEIGHT), PILImage.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            label_widget.configure(image=ctk_img, text="")
            label_widget._preview_ref = ctk_img
            _show_preview(pane_widget)

        elif ext == '.gif':
            src = PILImage.open(path)
            frames = []
            delays = []
            try:
                while True:
                    frame = src.copy().convert("RGBA")
                    frame.thumbnail((pane_w, _PREVIEW_HEIGHT), PILImage.LANCZOS)
                    frames.append(ctk.CTkImage(light_image=frame, dark_image=frame, size=frame.size))
                    delays.append(src.info.get("duration", 80))
                    src.seek(src.tell() + 1)
            except EOFError:
                pass

            label_widget._gif_frames = frames  # prevent GC

            def _tick(idx=0):
                global _gif_anim_job
                if not frames:
                    return
                label_widget.configure(image=frames[idx], text="")
                _gif_anim_job = root.after(delays[idx], _tick, (idx + 1) % len(frames))

            _show_preview(pane_widget)
            _tick()

        elif ext in _VIDEO_EXTS:
            import subprocess, tempfile
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True
            )
            try:
                duration = float(probe.stdout.strip())
                seek = duration / 2
            except (ValueError, AttributeError):
                seek = 0

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                tmp_path = tf.name

            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(seek), "-i", path,
                 "-vframes", "1", "-q:v", "2", tmp_path],
                capture_output=True
            )
            try:
                img = PILImage.open(tmp_path).convert("RGBA")
                img.thumbnail((pane_w, _PREVIEW_HEIGHT), PILImage.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                label_widget.configure(image=ctk_img, text="")
                label_widget._preview_ref = ctk_img
                _show_preview(pane_widget)
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        else:
            img = PILImage.open(path).convert("RGBA")
            img.thumbnail((pane_w, _PREVIEW_HEIGHT), PILImage.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            label_widget.configure(image=ctk_img, text="")
            label_widget._preview_ref = ctk_img
            _show_preview(pane_widget)

    except Exception:
        _hide_preview(pane_widget)


def browse_output_comp(entry_widget):
    """Save-as dialog for compressor output — must keep same file type."""
    input_path = entry_input_comp.get()
    if not input_path:
        messagebox.showerror("Error", "Please select an input file first")
        return
    is_valid, error_msg = validate_file_path(input_path)
    if not is_valid:
        messagebox.showerror("Error", f"Invalid input file: {error_msg}")
        return
    input_ext = normalize_extension(os.path.splitext(input_path)[1])
    file_path = filedialog.asksaveasfilename(
        defaultextension=input_ext,
        title=f"Save As — must be {input_ext.lstrip('.').upper()}",
    )
    if file_path:
        # Always enforce the source extension — silently correct whatever the user typed
        file_path = os.path.splitext(file_path)[0] + input_ext
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_path)


def schedule_prediction_update():
    """Debounce predicted-size calculation after slider/file changes."""
    global prediction_job_id
    if prediction_job_id is not None:
        root.after_cancel(prediction_job_id)
    if slider_comp and slider_level_label:
        slider_level_label.configure(text=f"{int(slider_comp.get())}%")
    prediction_job_id = root.after(500, update_prediction)


def update_prediction():
    """Compute and display predicted output size for current settings."""
    global prediction_job_id
    prediction_job_id = None
    input_path = entry_input_comp.get()
    if input_path and os.path.exists(input_path):
        try:
            is_gif = normalize_extension(os.path.splitext(input_path)[1]) == ".gif"
            target_fps = int(fps_slider.get()) if is_gif else None
            predicted_size = simulate_compression(input_path, slider_comp.get(), target_fps)
            label_predicted.configure(text=convert_size(predicted_size))
        except Exception as e:
            label_predicted.configure(text="—")
    else:
        label_predicted.configure(text="—")


def process_compression():
    """Validate inputs and run compression on a background thread."""
    input_path = entry_input_comp.get()
    output_path = entry_output_comp.get()
    compression_level = slider_comp.get()
    if not input_path or not output_path:
        messagebox.showerror("Error", "Please select input and output files")
        return
    is_valid, error_msg = validate_file_path(input_path)
    if not is_valid:
        messagebox.showerror("Error", f"Invalid input file: {error_msg}")
        return

    is_gif = normalize_extension(os.path.splitext(input_path)[1]) == ".gif"
    target_fps = int(fps_slider.get()) if is_gif else None

    _set_compress_busy(True)

    def _run():
        logger.log_compression_start(input_path, output_path, int(compression_level))
        try:
            compress_file(input_path, output_path, compression_level, target_fps)
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            logger.log_compression_success(input_path, output_path, original_size, compressed_size)
            root.after(0, lambda: _on_compress_done(
                True, os.path.basename(input_path), os.path.basename(output_path), None
            ))
        except Exception as e:
            logger.log_compression_error(input_path, output_path, str(e))
            root.after(0, lambda err=str(e): _on_compress_done(False, None, None, err))

    threading.Thread(target=_run, daemon=True).start()


def _set_compress_busy(busy: bool):
    """Disable/enable the Compress button, label, and progress bar."""
    if busy:
        compress_button.configure(text="Compressing…", state="disabled")
        _start_progress(progress_compress, _compress_anim_dir, "_compress_anim_job")
    else:
        compress_button.configure(text="Compress", state="normal")
        _stop_progress(progress_compress, "_compress_anim_job")


def _on_compress_done(success: bool, input_name: str, output_name: str, error: str):
    """Called on the main thread when a compression finishes."""
    _set_compress_busy(False)
    if success:
        messagebox.showinfo("Success", f"Compressed {input_name} to {output_name}")
    else:
        messagebox.showerror("Error", f"Compression failed: {error}")


def _start_progress(bar, dir_holder: list, job_global: str):
    """Begin a bouncing indeterminate animation on bar."""
    this_module = sys.modules[__name__]

    def _tick():
        val = bar.get()
        new_val = val + 0.03 * dir_holder[0]
        if new_val >= 1.0:
            dir_holder[0] = -1
            new_val = 1.0
        elif new_val <= 0.0:
            dir_holder[0] = 1
            new_val = 0.0
        bar.set(new_val)
        setattr(this_module, job_global, root.after(20, _tick))

    bar.set(0)
    dir_holder[0] = 1
    _tick()


def _stop_progress(bar, job_global: str):
    """Cancel the animation and reset bar to zero."""
    this_module = sys.modules[__name__]
    job = getattr(this_module, job_global, None)
    if job is not None:
        root.after_cancel(job)
        setattr(this_module, job_global, None)
    bar.set(0)



class MainApplication:
    def __init__(self):
        """Build the application window and tabs."""
        global root, entry_input, entry_output, format_dropdown, conversion_label, convert_button, progress_convert
        global preview_pane_conv, preview_label_conv, preview_pane_comp, preview_label_comp
        global entry_input_comp, entry_output_comp, slider_comp, slider_level_label, fps_slider, fps_level_label, fps_row_sep, fps_row_label, fps_row_frame, label_predicted, compress_button, progress_compress

        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        root = ctk.CTk()
        self.root = root
        root.title(WINDOW_TITLE)
        root.geometry(WINDOW_SIZE)
        root.resizable(WINDOW_RESIZABLE, WINDOW_RESIZABLE)
        root.configure(fg_color=BG_PRIMARY)
        self._set_window_icon()

        container = ctk.CTkFrame(root, fg_color=BG_PRIMARY, corner_radius=0, border_width=0)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # ── Top bar: logo left, tab switcher right ────────────────────────
        topbar = ctk.CTkFrame(container, fg_color="transparent")
        topbar.pack(fill="x", pady=(20, 0))

        logo_image = self._load_logo()
        if logo_image:
            self._logo_ref = logo_image
            ctk.CTkLabel(topbar, image=logo_image, text="",
                         fg_color="transparent").pack(side="left")
        else:
            ctk.CTkLabel(topbar, text="Refiner",
                         font=("Helvetica Neue", 18, "bold"),
                         text_color=TEXT_PRIMARY,
                         fg_color="transparent").pack(side="left")

        # Tab content frames — swapped in/out on selection
        converter_frame = ctk.CTkFrame(container, fg_color="transparent", corner_radius=0)
        compressor_frame = ctk.CTkFrame(container, fg_color="transparent", corner_radius=0)

        def _switch_tab(value):
            v = value.strip()
            if v == "Converter":
                compressor_frame.pack_forget()
                converter_frame.pack(fill="both", expand=True, pady=(14, 0))
            else:
                converter_frame.pack_forget()
                compressor_frame.pack(fill="both", expand=True, pady=(14, 0))
            root.update_idletasks()
            root.geometry(f"450x{root.winfo_reqheight()}")

        _tab_values = ["  Converter  ", "  Compressor  "]
        ctk.CTkSegmentedButton(
            topbar,
            values=_tab_values,
            command=_switch_tab,
            height=36, corner_radius=3,
            fg_color=BG_SECONDARY,
            selected_color=ACCENT_PRIMARY,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=BG_SECONDARY,
            unselected_hover_color=SURFACE_ELEVATED,
            font=("Helvetica Neue", 13, "bold"),
            text_color=TEXT_PRIMARY,
            text_color_disabled=TEXT_MUTED,
        ).pack(side="right")

        # Show converter tab initially
        converter_frame.pack(fill="both", expand=True, pady=(14, 0))

        # ── Shared styles ─────────────────────────────────────────────────
        CARD   = dict(corner_radius=3, fg_color=SURFACE_PRIMARY, border_width=0)
        SEP    = dict(height=1, fg_color=BORDER_PRIMARY, corner_radius=0)
        LBL    = dict(font=("Helvetica Neue", 15), text_color=TEXT_SECONDARY, width=100, anchor="w")
        ENTRY  = dict(height=40, border_width=0, corner_radius=3,
                      fg_color=SURFACE_SECONDARY, text_color=TEXT_PRIMARY,
                      font=("Helvetica Neue", 15))
        BTN    = dict(text="Browse", width=76, height=34, corner_radius=3,
                      fg_color=SURFACE_ELEVATED, hover_color=BORDER_SECONDARY,
                      text_color=TEXT_PRIMARY, font=("Helvetica Neue", 13), border_width=0)
        ACTION = dict(font=("Helvetica Neue", 16, "bold"), height=50, corner_radius=3,
                      fg_color=ACCENT_PRIMARY, hover_color=ACCENT_HOVER,
                      text_color="#FFFFFF", border_width=0)

        def _card(parent):
            c = ctk.CTkFrame(parent, **CARD)
            c.pack(fill="x")
            c.columnconfigure(1, weight=1)
            return c

        def _sep(card, row):
            ctk.CTkFrame(card, **SEP).grid(row=row, column=0, columnspan=3, sticky="ew")

        def _row(card, row_idx, label, widget, has_browse=False, browse_cmd=None):
            ctk.CTkLabel(card, text=label, **LBL).grid(
                row=row_idx, column=0, padx=(18, 0), pady=16, sticky="w")
            if has_browse:
                widget.grid(row=row_idx, column=1, sticky="ew", padx=(0, 8), pady=16)
                ctk.CTkButton(card, command=browse_cmd, **BTN).grid(
                    row=row_idx, column=2, padx=(0, 16), pady=16)
            else:
                widget.grid(row=row_idx, column=1, columnspan=2, sticky="ew",
                            padx=(0, 16), pady=16)

        # ── CONVERTER TAB ─────────────────────────────────────────────────
        ct = converter_frame

        preview_pane_conv = ctk.CTkFrame(ct, fg_color=SURFACE_PRIMARY, corner_radius=3, height=0)
        preview_pane_conv.pack_propagate(False)
        preview_pane_conv.pack(fill="x", pady=0)
        preview_label_conv = ctk.CTkLabel(preview_pane_conv, text="", fg_color="transparent")
        preview_label_conv.pack(expand=True)

        cv = _card(ct)

        entry_input = ctk.CTkEntry(cv, **ENTRY)
        _row(cv, 0, "Source", entry_input, has_browse=True,
             browse_cmd=lambda: browse_file(entry_input))

        _sep(cv, 1)

        format_dropdown = ctk.CTkOptionMenu(
            cv, values=["—"], command=on_format_changed,
            height=40, corner_radius=3,
            fg_color=SURFACE_SECONDARY, button_color=ACCENT_PRIMARY,
            button_hover_color=ACCENT_HOVER, text_color=TEXT_PRIMARY,
            font=("Helvetica Neue", 15), state="disabled", anchor="w",
        )
        _row(cv, 2, "Format", format_dropdown)

        _sep(cv, 3)

        entry_output = ctk.CTkEntry(cv, **ENTRY)
        _row(cv, 4, "Save As", entry_output, has_browse=True,
             browse_cmd=lambda: browse_output(entry_output))

        conversion_label = ctk.CTkLabel(
            ct, text="—", font=("Helvetica Neue", 12),
            text_color=TEXT_MUTED, fg_color="transparent",
        )
        conversion_label.pack(pady=(12, 0))

        convert_button = ctk.CTkButton(ct, text="Convert",
                                       command=process_conversion, **ACTION)
        convert_button.pack(fill="x", pady=(8, 0))

        progress_convert = ctk.CTkProgressBar(
            ct, height=3, corner_radius=3,
            fg_color=BG_PRIMARY, progress_color=ACCENT_PRIMARY)
        progress_convert.set(0)
        progress_convert.pack(fill="x", pady=(5, 0))

        # ── COMPRESSOR TAB ────────────────────────────────────────────────
        cpt = compressor_frame

        preview_pane_comp = ctk.CTkFrame(cpt, fg_color=SURFACE_PRIMARY, corner_radius=3, height=0)
        preview_pane_comp.pack_propagate(False)
        preview_pane_comp.pack(fill="x", pady=0)
        preview_label_comp = ctk.CTkLabel(preview_pane_comp, text="", fg_color="transparent")
        preview_label_comp.pack(expand=True)

        cp = _card(cpt)

        entry_input_comp = ctk.CTkEntry(cp, **ENTRY)
        _row(cp, 0, "Source", entry_input_comp, has_browse=True,
             browse_cmd=lambda: browse_file_comp(entry_input_comp))

        _sep(cp, 1)

        # Compression slider row — built inline as it has two sub-widgets
        ctk.CTkLabel(cp, text="Compression", **LBL).grid(
            row=2, column=0, padx=(18, 0), pady=16, sticky="w")
        slider_row = ctk.CTkFrame(cp, fg_color="transparent")
        slider_row.grid(row=2, column=1, columnspan=2, sticky="ew",
                        padx=(0, 16), pady=16)
        slider_row.columnconfigure(0, weight=1)

        slider_comp = ctk.CTkSlider(
            slider_row, from_=0, to=100, number_of_steps=100,
            command=lambda val: schedule_prediction_update(),
            height=14, button_color=ACCENT_PRIMARY,
            button_hover_color=ACCENT_HOVER,
            progress_color=ACCENT_PRIMARY, fg_color=SURFACE_ELEVATED,
        )
        slider_comp.set(50)
        slider_comp.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        slider_comp.bind("<ButtonRelease-1>", lambda e: schedule_prediction_update())

        slider_level_label = ctk.CTkLabel(
            slider_row, text="50%",
            font=("Helvetica Neue", 14, "bold"),
            text_color=TEXT_PRIMARY, width=42, anchor="e",
        )
        slider_level_label.grid(row=0, column=1)

        # FPS row — hidden until a GIF is loaded
        fps_row_sep = ctk.CTkFrame(cp, **SEP)
        fps_row_sep.grid(row=3, column=0, columnspan=3, sticky="ew")
        fps_row_sep.grid_remove()

        fps_row_label = ctk.CTkLabel(cp, text="GIF FPS", **LBL)
        fps_row_label.grid(row=4, column=0, padx=(18, 0), pady=16, sticky="w")
        fps_row_label.grid_remove()

        fps_row_frame = ctk.CTkFrame(cp, fg_color="transparent")
        fps_row_frame.grid(row=4, column=1, columnspan=2, sticky="ew",
                           padx=(0, 16), pady=16)
        fps_row_frame.columnconfigure(0, weight=1)
        fps_row_frame.grid_remove()

        fps_slider = ctk.CTkSlider(
            fps_row_frame, from_=1, to=60, number_of_steps=59,
            command=lambda val: [fps_level_label.configure(text=f"{int(val)} fps"),
                                 schedule_prediction_update()],
            height=14, state="disabled",
            button_color=ACCENT_PRIMARY, button_hover_color=ACCENT_HOVER,
            progress_color=ACCENT_PRIMARY, fg_color=SURFACE_ELEVATED,
        )
        fps_slider.set(15)
        fps_slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        fps_level_label = ctk.CTkLabel(
            fps_row_frame, text="15 fps",
            font=("Helvetica Neue", 14, "bold"),
            text_color=TEXT_PRIMARY, width=52, anchor="e",
        )
        fps_level_label.grid(row=0, column=1)

        _sep(cp, 5)

        ctk.CTkLabel(cp, text="Predicted", **LBL).grid(
            row=6, column=0, padx=(18, 0), pady=16, sticky="w")
        label_predicted = ctk.CTkLabel(
            cp, text="—", font=("Helvetica Neue", 15),
            text_color=ACCENT_WARNING, anchor="w",
        )
        label_predicted.grid(row=6, column=1, columnspan=2, sticky="ew",
                             padx=(0, 16), pady=16)

        _sep(cp, 7)

        entry_output_comp = ctk.CTkEntry(cp, **ENTRY)
        _row(cp, 8, "Save As", entry_output_comp, has_browse=True,
             browse_cmd=lambda: browse_output_comp(entry_output_comp))

        compress_button = ctk.CTkButton(cpt, text="Compress",
                                        command=process_compression, **ACTION)
        compress_button.pack(fill="x", pady=(16, 0))

        progress_compress = ctk.CTkProgressBar(
            cpt, height=3, corner_radius=3,
            fg_color=BG_PRIMARY, progress_color=ACCENT_PRIMARY)
        progress_compress.set(0)
        progress_compress.pack(fill="x", pady=(5, 0))

        # Fit window height to content — no dead space
        root.update_idletasks()
        root.geometry(f"450x{root.winfo_reqheight()}")

    @staticmethod
    def _assets_path(*parts) -> str:
        """Resolve a path inside the assets/ folder, works both dev and PyInstaller."""
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS  # type: ignore[attr-defined]
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "assets", *parts)

    def _load_logo(self, max_height: int = 22):
        """Return a proportionally-scaled CTkImage from assets/logo.png if it exists."""
        candidates = ["logo.png", "icon.png"]
        for name in candidates:
            path = self._assets_path(name)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    w, h = img.size
                    scale = max_height / h
                    display_size = (max(1, int(w * scale)), max_height)
                    return ctk.CTkImage(light_image=img, dark_image=img, size=display_size)
                except Exception:
                    pass
        return None

    def _set_window_icon(self):
        """Apply a window icon (dock/taskbar) from assets/ if available."""
        import platform
        system = platform.system()
        if system == "Darwin":
            candidates = ["icon.icns", "icon.png", "logo.png"]
        elif system == "Windows":
            candidates = ["icon.ico", "icon.png", "logo.png"]
        else:
            candidates = ["icon.png", "logo.png"]
        for name in candidates:
            path = self._assets_path(name)
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    icon = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                    # Use tkinter's wm_iconphoto for cross-platform icon
                    from PIL import ImageTk
                    tk_img = ImageTk.PhotoImage(img.resize((32, 32)))
                    self.root.wm_iconphoto(True, tk_img)
                    self._icon_ref = tk_img  # prevent GC
                except Exception:
                    pass
                return

    def run(self):
        self.root.mainloop()
