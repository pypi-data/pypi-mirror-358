from setuptools import setup, find_packages

setup(
    name='matplotsklib',
    version='0.1',
    packages=find_packages(),
    install_requires=['pyperclip'],
    entry_points={
        'console_scripts': [
            'matplotsklib=matplotsklib.__main__:main'
        ],
    },
    author='SKLIB',
    description='Installer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
