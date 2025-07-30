# setup.py
from setuptools import setup, find_packages

setup(
    name='binaryduino',
    version='0.1.0',
    description='Binary and Arduino simulation toolkit with waveform visualization and signal processing',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Adam Alcander et Eden',
    author_email='aeden6877@gmail.com',
    url='https://github.com/EdenGithhub/binaryduino',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'colorama',
        'bitstring',
        'pyserial',
        'loguru',
        'rich',
        'pydantic',
        'typer',
        'tqdm',
        'python-dotenv',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'binaryduino-cli = binaryduino.core:cli_encoder'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True,
    license='MIT'
)