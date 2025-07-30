from setuptools import setup, find_packages

setup(
    name='zonefinder',
    version='0.0.5',
    description='Data-driven approach to highlight critical price zones',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Anthony Gocmen',
    author_email='anthony.gocmen@gmail.com',
    url='https://www.developexx.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.11',
    install_requires=[
        'pandas>=1.0',
    ],
    license='MIT'
)
