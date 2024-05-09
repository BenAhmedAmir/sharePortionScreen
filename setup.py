from setuptools import setup

APP = ['portionShare.py']  # replace with your script name
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5'],
    'iconfile': '/Users/takiacademy/PycharmProjects/sharescreen/camera.icns'
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
