from setuptools import setup, find_packages

setup(
    name='devghost',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
        'PyGithub',
    ],
    entry_points={
        'console_scripts': [
            'devghost=devghost.cli:cli',
        ],
    },
    author='Your Name',
    description='DevGhost: Smart CLI for AI-powered commit messages',
    long_description='Generate smart GitHub commit messages from code diffs using Gemini AI.',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/devghost',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
) 