from setuptools import setup, find_packages

setup(
    name='dataframeops', 
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas', 'openpyxl'
    ],
    author='Jorik Carlsen',
    author_email='jorikcarlsen@protonmail.com',
    description='A dataframe utility module with extended caching.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)