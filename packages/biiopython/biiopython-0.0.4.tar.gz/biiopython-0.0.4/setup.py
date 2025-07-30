from setuptools import setup, find_packages

setup(
    name="biiopython",
    version="0.0.4", 
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'biiopython': ['data/*', '*.ent']
    },
    install_requires=[],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
