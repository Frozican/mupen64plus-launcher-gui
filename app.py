#!/usr/bin/env python3
"""Tkinter launcher and plugin manager for Mupen64Plus."""
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_DIR = Path.home() / '.config' / 'mupen64plus-gui'
CONFIG = APP_DIR / 'settings.json'
DEFAULTS = {
    'rom_dir': str(Path.home() / 'ROMs'),
    'fullscreen': False,
    'plugins': {'gfx': '', 'audio': '', 'input': '', 'rsp': ''},
    'extra_args': '',
}
PLUGIN_LABELS = [
    ('gfx', 'Video / GFX'),
    ('audio', 'Audio'),
    ('input', 'Input'),
    ('rsp', 'RSP'),
]
PLUGIN_PATTERNS = {
    'gfx': ('*video*.so', '*glide*.so', '*rice*.so', '*angrylion*.so'),
    'audio': ('*audio*.so',),
    'input': ('*input*.so',),
    'rsp': ('*rsp*.so',),
}
PLUGIN_DIRS = (
    Path('/usr/local/lib/mupen64plus'),
    Path('/usr/lib/mupen64plus'),
    Path('/usr/lib/aarch64-linux-gnu/mupen64plus'),
    Path('/usr/lib/x86_64-linux-gnu/mupen64plus'),
    Path.home() / '.local/lib/mupen64plus',
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mupen64Plus Launcher')
        self.geometry('840x570')
        self.minsize(700, 460)
        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.cfg = self.load_config()
        self.plugin_vars = {}
        self.build_ui()
        self.refresh_roms()

    def load_config(self):
        try:
            data = json.loads(CONFIG.read_text())
            merged = {**DEFAULTS, **data}
            merged['plugins'] = {**DEFAULTS['plugins'], **data.get('plugins', {})}
            return merged
        except (OSError, ValueError, TypeError):
            return json.loads(json.dumps(DEFAULTS))

    def save_config(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(self.cfg, indent=2))

    def build_ui(self):
        root = ttk.Frame(self, padding=14)
        root.pack(fill='both', expand=True)
        head = ttk.Frame(root)
        head.pack(fill='x')
        ttk.Label(head, text='Mupen64Plus', font=('TkDefaultFont', 19, 'bold')).pack(side='left')
        ttk.Button(head, text='Settings / Plugins', command=self.open_settings).pack(side='right')

        row = ttk.Frame(root)
        row.pack(fill='x', pady=(14, 8))
        self.folder_var = tk.StringVar(value=self.cfg['rom_dir'])
        ttk.Label(row, text='ROM folder:').pack(side='left')
        ttk.Entry(row, textvariable=self.folder_var).pack(side='left', fill='x', expand=True, padx=8)
        ttk.Button(row, text='Browse…', command=self.choose_rom_folder).pack(side='right')

        self.tree = ttk.Treeview(root, columns=('name', 'size'), show='headings', selectmode='browse')
        self.tree.heading('name', text='ROM')
        self.tree.heading('size', text='Size')
        self.tree.column('name', width=590)
        self.tree.column('size', width=110, anchor='e')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', lambda _event: self.launch())

        bottom = ttk.Frame(root)
        bottom.pack(fill='x', pady=(10, 0))
        self.status = tk.StringVar(value=self.emulator_status())
        ttk.Label(bottom, textvariable=self.status).pack(side='left')
        ttk.Button(bottom, text='Refresh', command=self.refresh_roms).pack(side='right', padx=(6, 0))
        ttk.Button(bottom, text='Launch ROM', command=self.launch).pack(side='right')

    def emulator_path(self):
        return shutil.which('mupen64plus')

    def emulator_status(self):
        exe = self.emulator_path()
        return f'Emulator: {exe}' if exe else 'Emulator not installed — run setup_linux.sh first.'

    def choose_rom_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_var.get() or str(Path.home()))
        if path:
            self.folder_var.set(path)
            self.cfg['rom_dir'] = path
            self.save_config()
            self.refresh_roms()

    def refresh_roms(self):
        self.cfg['rom_dir'] = self.folder_var.get()
        self.save_config()
        self.tree.delete(*self.tree.get_children())
        folder = Path(self.folder_var.get()).expanduser()
        if folder.is_dir():
            for path in sorted(folder.iterdir(), key=lambda item: item.name.lower()):
                if path.is_file() and path.suffix.lower() in ('.z64', '.n64', '.v64', '.zip'):
                    self.tree.insert('', 'end', iid=str(path), values=(path.name, f'{path.stat().st_size / 1048576:.1f} MiB'))
        self.status.set(self.emulator_status())

    def find_plugins(self, kind):
        found = set()
        for directory in PLUGIN_DIRS:
            if directory.is_dir():
                for pattern in PLUGIN_PATTERNS[kind]:
                    found.update(str(path.resolve()) for path in directory.glob(pattern) if path.is_file())
        return sorted(found, key=lambda value: Path(value).name.lower())

    def open_settings(self):
        win = tk.Toplevel(self)
        win.title('Launcher & Plugin Settings')
        win.geometry('760x470')
        win.minsize(650, 420)
        win.transient(self)
        self.plugin_vars = {}
        self._build_settings_content(win)

    def _build_settings_content(self, win):
        frame = ttk.Frame(win, padding=16)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Plugin selection', font=('TkDefaultFont', 13, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Label(frame, text='Select the plugin library used for each subsystem. The installer builds the standard plugins from the official source repositories.').pack(anchor='w', pady=(0, 12))

        for key, label in PLUGIN_LABELS:
            line = ttk.Frame(frame)
            line.pack(fill='x', pady=6)
            ttk.Label(line, text=label, width=14).pack(side='left')
            options = ['(Use emulator default)'] + self.find_plugins(key)
            current = self.cfg.get('plugins', {}).get(key, '')
            current = current if current in options else (current or options[0])
            var = tk.StringVar(value=current)
            self.plugin_vars[key] = var
            combo = ttk.Combobox(line, textvariable=var, values=options, state='readonly')
            combo.pack(side='left', fill='x', expand=True, padx=7)
            ttk.Button(line, text='Browse…', command=lambda target=var: self.browse_plugin(target)).pack(side='right')

        self.fullscreen_var = tk.BooleanVar(value=bool(self.cfg.get('fullscreen')))
        ttk.Checkbutton(frame, text='Start games in fullscreen', variable=self.fullscreen_var).pack(anchor='w', pady=(15, 7))
        ttk.Label(frame, text='Additional command-line arguments:').pack(anchor='w')
        self.extra_var = tk.StringVar(value=self.cfg.get('extra_args', ''))
        ttk.Entry(frame, textvariable=self.extra_var).pack(fill='x', pady=(4, 12))

        buttons = ttk.Frame(frame)
        buttons.pack(fill='x', side='bottom')
        ttk.Button(buttons, text='Rescan plugins', command=lambda: self.rescan_settings(win)).pack(side='left')
        ttk.Button(buttons, text='Save settings', command=lambda: self.save_settings(win)).pack(side='right')

    def browse_plugin(self, variable):
        path = filedialog.askopenfilename(
            title='Select plugin library',
            filetypes=[('Shared libraries', '*.so *.so.*'), ('All files', '*')],
        )
        if path:
            variable.set(str(Path(path).resolve()))

    def rescan_settings(self, win):
        pending = {key: variable.get() for key, variable in self.plugin_vars.items()}
        for key, value in pending.items():
            self.cfg['plugins'][key] = '' if value == '(Use emulator default)' else value
        self.cfg['fullscreen'] = self.fullscreen_var.get()
        self.cfg['extra_args'] = self.extra_var.get()
        self.plugin_vars = {}
        for child in win.winfo_children():
            child.destroy()
        self._build_settings_content(win)
        for key, value in pending.items():
            if key in self.plugin_vars and value:
                self.plugin_vars[key].set(value)

    def save_settings(self, win):
        self.cfg['plugins'] = {
            key: ('' if variable.get() == '(Use emulator default)' else variable.get())
            for key, variable in self.plugin_vars.items()
        }
        self.cfg['fullscreen'] = self.fullscreen_var.get()
        self.cfg['extra_args'] = self.extra_var.get()
        self.save_config()
        win.destroy()
        messagebox.showinfo('Settings saved', 'Video, Audio, Input, RSP and launcher settings have been saved.')

    def launch(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('No ROM selected', 'Select a ROM from the list first.')
            return
        exe = self.emulator_path()
        if not exe:
            messagebox.showerror('Emulator missing', 'Mupen64Plus was not found. Run setup_linux.sh first.')
            return
        rom = selected[0]
        args = [exe]
        if self.cfg.get('fullscreen'):
            args.append('--fullscreen')
        option_names = {'gfx': '--gfx', 'audio': '--audio', 'input': '--input', 'rsp': '--rsp'}
        for key, _label in PLUGIN_LABELS:
            value = self.cfg.get('plugins', {}).get(key, '')
            if value:
                if not Path(value).is_file():
                    messagebox.showerror('Plugin not found', f'The selected {key.upper()} plugin does not exist:\n{value}\n\nOpen Settings and select an installed plugin.')
                    return
                args.extend([option_names[key], value])
        extra = self.cfg.get('extra_args', '').strip()
        if extra:
            args.extend(shlex.split(extra))
        args.append(rom)
        try:
            subprocess.Popen(args, cwd=str(Path(rom).parent))
        except Exception as exc:
            messagebox.showerror('Launch failed', str(exc))


if __name__ == '__main__':
    App().mainloop()
