from setuptools import setup, find_packages

setup(
    name='multinut',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Chipperfluff',
    author_email='i96774080@gmail.com',
    description='A completely unnecessary multitool module.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ChipperFluff/multinut',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
