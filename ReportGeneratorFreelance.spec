# -*- mode: python ; coding: utf-8 -*-

import os
import sys


python_root = sys.base_prefix
tcl_root = os.path.join(python_root, 'tcl')
dll_root = os.path.join(python_root, 'DLLs')


a = Analysis(
    ['report_generator.py'],
    pathex=[],
    binaries=[
        (os.path.join(dll_root, 'tcl86t.dll'), '.'),
        (os.path.join(dll_root, 'tk86t.dll'), '.'),
        (os.path.join(dll_root, '_tkinter.pyd'), '.'),
    ],
    datas=[
        ('marble_logo.png', '.'),
        (os.path.join(tcl_root, 'tcl8.6'), '_tcl_data'),
        (os.path.join(tcl_root, 'tk8.6'), '_tk_data'),
        (os.path.join(tcl_root, 'tcl8'), 'tcl8'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=['pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ReportGeneratorFreelance',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
