from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='turkle-review',
    version='0.2',
    description='Adds batch review capability to Turkle',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hltcoe/turkle-review',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=4.2',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
