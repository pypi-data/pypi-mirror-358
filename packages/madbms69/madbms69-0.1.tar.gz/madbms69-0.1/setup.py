from setuptools import setup, find_packages

setup(
    name='madbms69',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    description='CLI tool to display Android code examples',
    author='Your Name',
    author_email='you@example.com',
    entry_points={
        'console_scripts': [
            'madbms69 = madbms69.cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

