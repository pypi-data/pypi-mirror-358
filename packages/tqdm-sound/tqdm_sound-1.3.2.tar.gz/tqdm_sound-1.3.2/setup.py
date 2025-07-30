from pathlib import Path
from setuptools import find_packages, setup
from typing import Optional

# Load version number
__version__: Optional[str] = None

src_dir = Path(__file__).parent.absolute()
version_file = src_dir / 'tqdm_sound' / '_version.py'
readme_file = src_dir / 'README.rst'

# Long README
with open(version_file) as fd:
    exec(fd.read())

long_description=open(readme_file, encoding="UTF-8").read()

setup(
    name='tqdm_sound',
    version=__version__,
    readme="README.rst",
    author='JH',
    author_email='dev_gatehouse@proton.me',
    description='Progress bars with sound enhancements',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/looking-glass-station/tqdm_sound',
    download_url=f'https://github.com/looking-glass-station/tqdm_sound/v_{__version__}.tar.gz',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        "build~=1.2.2.post1",
        "cffi~=1.17.1",
        "colorama~=0.4.6",
        "iniconfig>=1.1.1",
        "numpy>=1.26.0",
        "packaging~=25.0",
        "pluggy~=1.6.0",
        "pycparser~=2.22",
        "pynput~=1.8.1",
        "pyproject_hooks~=1.2.0",
        "pytest~=8.3.5",
        "simpleaudio~=1.0.4",
        "six~=1.17.0",
        "sounddevice~=0.5.2",
        "soundfile~=0.13.1",
        "tqdm~=4.67.1"
    ],

    package_data={
        "tqdm_sound": ["sounds/**/*.wav"],
    },
    tests_require=['pytest'],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords=[
        'tqdm',
        'progress bar',
        'progress alerts',
        'progress sounds'
        'Ryoji Ikeda'
    ],
    python_requires = ">=3.9"
)
