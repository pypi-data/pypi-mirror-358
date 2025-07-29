from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='mplviz',
    version='0.3',
    description='A fluent wrapper around matplotlib for easy, expressive visualizations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='BBEK-Anand',
    url='https://github.com/BBEK-Anand/mplviz',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        'matplotlib>=3.6.0',
        'numpy>=1.18.0',
        'ipython>=7.0.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Visualization',
        'Framework :: Matplotlib',
    ],
    python_requires='>=3.7',

)
