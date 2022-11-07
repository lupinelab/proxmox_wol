import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--collect-all',
    'proxmoxer',
    '--onefile',
    '--distpath',
    './bin',
    '--name',
    'proxmox_wol'
])