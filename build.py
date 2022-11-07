import PyInstaller.__main__

PyInstaller.__main__.run([
    'proxmox_wol.py',
    '--collect-all',
    'proxmoxer',
    '--onefile',
    '--distpath',
    './bin',
])