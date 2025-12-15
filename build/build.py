import PyInstaller.__main__

PyInstaller.__main__.run([
    '..\MSS.py',
    '--log-level=DEBUG',
    '--name=MSS',
    '--clean',
    '-w',
    '--onefile',
    '--uac-admin',
    '--version-file=./version.rc'
])