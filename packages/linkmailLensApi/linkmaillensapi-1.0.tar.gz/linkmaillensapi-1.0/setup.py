from setuptools import setup, find_packages

with open("./README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name='linkmailLensApi',
    packages=['linkmailLensApi'],
    version='1.0',
    description='Api no oficial de Google lens creada por mi.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Linkmail',
    author_email='',  
    url='https://github.com/Linkmail16/linkmailLensApi',
    download_url='https://github.com/Linkmail16/linkmailLensApi/archive/refs/tags/v0.3.tar.gz',
    keywords=['api', 'google', 'google lens'],
     classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pillow",
    ],
)