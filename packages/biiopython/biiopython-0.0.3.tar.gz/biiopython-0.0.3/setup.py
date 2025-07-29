from setuptools import setup, find_packages

setup(
    name="biiopython",
    version="0.0.3", # Incrementing version since 0.0.1 and 0.0.2 were already uploaded
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'biiopython': ['data/*', '*.ent']
    },
    install_requires=[],
    description="A Python package for bioinformatics tasks (static reference files).",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="JAI GUPTA",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/biiopython",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
