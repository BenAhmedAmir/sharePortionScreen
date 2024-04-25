from setuptools import setup

APP = ['main.py']  # replace with your script name
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
