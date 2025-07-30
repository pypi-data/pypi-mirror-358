from setuptools import setup, find_packages

setup(
    name="endmad",
    version="0.1.1",
    packages=find_packages(),
    package_data={
        'my_package': ['**/*'],  # Include all files
        'my_package.cie1': ['*'],
        'my_package.cie2': ['*'], 
        'my_package.master': ['**/*'],
    },
    include_package_data=True,
)