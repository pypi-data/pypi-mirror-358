from setuptools import setup, find_packages

setup(
    name='PreCliPy',
    version='0.1.2',
    description='A biomedical lookup tool for diseases, drugs, PMC articles, and NCT trials',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'duckdb',
    ],
    include_package_data=True,
    package_data={
        'PCPy': ['data/*.duckdb']
    },
)
