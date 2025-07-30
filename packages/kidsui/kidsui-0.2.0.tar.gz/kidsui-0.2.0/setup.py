from setuptools import setup, find_packages

setup(
    name='kidsui',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'kivy'
    ],
    author='Ahmed Mohammed',
    author_email='programmer2020dev@gmail.com',
    description='A colorful GUI library for kids built on Kivy',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/kidsui',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
