from setuptools import setup, find_packages

setup(
    name="endmad",
    version="0.1.2",
    packages=find_packages(),
    package_data={
        'my_package': ['*'],  # Files directly in my_package
        'my_package.cie1': ['*'],  # All files in cie1 subdirectory
        'my_package.cie2': ['*'],  # All files in cie2 subdirectory
        'my_package.cie2.animation': ['*'],
        'my_package.cie2.canvas': ['*'],
        'my_package.cie2.contextMenu': ['*'],
        'my_package.cie2.database': ['*'],
        'my_package.cie2.explicit': ['*'],
        'my_package.cie2.fragment': ['*'],
        'my_package.cie2.IMPLICIT and EXPLICIT': ['*'],
        'my_package.cie2.optionsMenu': ['*'],
        'my_package.cie2.popMenu': ['*'],
        'my_package.cie2.sharedpref': ['*'],
        'my_package.master': ['*'],  # All files in master subdirectory
    },
    include_package_data=True,
    zip_safe=False,  # Important for accessing package data
)