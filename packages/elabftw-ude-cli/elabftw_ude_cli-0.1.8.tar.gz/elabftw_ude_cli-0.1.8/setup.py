from setuptools import setup, find_packages

setup(
    name='elabftw_ude_cli',
    version='0.1.8',
    packages=find_packages(),
    install_requires=[
        'requests',
        'argcomplete',
    ],
    entry_points={
        'console_scripts': [
            'elabftw-cli=elabftw_ude_cli.cli:main',
            'elab_auto_update=elabftw_ude_cli.auto_update:main',
        ],
    },
    author='Manan B Shah',
    author_email='manan.shah@uni-due.de',
    description='CLI wrapper for interacting with eLabFTW API at University of Duisburg-Essen',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://github.com/yourusername/elabftw_ude_cli',  # Optional: Update if hosted
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
