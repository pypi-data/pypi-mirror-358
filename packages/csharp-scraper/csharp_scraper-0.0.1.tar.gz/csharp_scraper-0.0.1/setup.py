from setuptools import setup, find_packages

setup(
    name='csharp-scraper',
    version='0.0.1',
    packages=find_packages(),  # finds logic, cli, profiles automatically
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'csharp-scraper = scraper:main'
        ]
    },
    description='Extract and process C# logic blocks into raw.txt for LLM training',
    author='jdolabs',
    license='MIT',
)
