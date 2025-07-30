from setuptools import setup, find_packages

with open('readme.md', 'r', encoding='utf-8') as f:
    description = f.read()

setup(
    name="pewhits-client-sdk",
    version='0.9',
    packages=find_packages(),
    install_requires=[
        'typing_extensions>=4.12.2',
        'cattrs>=22.2.0',
        'quattro>=22.2.0',
        'attrs>=24.2.0',
        'aiohttp>=3.10.5',        
    ],
    long_description=description,
    long_description_content_type="text/markdown"
)
