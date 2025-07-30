from setuptools import setup, find_packages

setup(
    name='chronolap',
    version='1.0.0',
    description='Advanced stopwatch with lap tracking for Python developers',
    author='Ertugrul Kara',
    author_email='ertugrulkra@gmail.com',
    url='https://github.com/ertugrulkara/ChronolapPy',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
