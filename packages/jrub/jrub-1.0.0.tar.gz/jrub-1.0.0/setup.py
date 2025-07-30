from setuptools import setup, find_packages

def read_file(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

setup(
    name='jrub',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'urllib3',
    ],
    include_package_data=True,
    description='rubika bot',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/mahdy-ahmadi/',
    author='Mahdi Ahmadi',
    author_email='mahdiahmadi.1208@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
