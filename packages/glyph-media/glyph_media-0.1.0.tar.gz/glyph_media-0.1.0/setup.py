from setuptools import setup, find_packages

setup(
    name='glyph-media',
    version='0.1.0',
    author='pizzalover125',
    packages=find_packages(),
    install_requires=[
        'rich',
        'questionary',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'glyph=glyph.main:main',
        ],
    },
)
