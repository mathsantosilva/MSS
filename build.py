import PyInstaller.__main__

PyInstaller.__main__.run([
    '.\BuscaMuro.py',
    '--clean',
    '--onefile',
    '-w'
])