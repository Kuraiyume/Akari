from setuptools import setup, find_packages

setup(
    name="akari",
    version="0.12",
    packages=['akari'],
    install_requires=[
        'dnspython',
        'termcolor',
        'retrying',
    ],
    entry_points={
        'console_scripts': [
            'akari=akari.akari:main',
        ],
    },
    author="Veilwr4ith",
    author_email="hacktheveil@gmail.com",
    description="Advanced DNS Enumerator",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/veilwr4ith/Akari",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
