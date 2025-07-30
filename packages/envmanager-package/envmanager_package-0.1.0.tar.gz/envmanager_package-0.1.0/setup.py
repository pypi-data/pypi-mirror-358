from setuptools import setup, find_packages

setup(
    name='envmanager-package',
    version='0.1.0',
    description='A simple CLI tool to create, edit, validate, and manage .env files for Python projects.',
    long_description='EnvManager is a Python CLI utility that helps you manage .env files: add/remove keys, validate required variables, and generate from templates. Ideal for Python developers who use environment variables.',
    long_description_content_type='text/markdown',
    author='Sunil Kumawat',
    author_email='kumawatsunilkumar889@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'envmanager=envmanager.cli:cli',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    project_urls={
        'Source': 'https://github.com/yourusername/envmanager',
    },
) 