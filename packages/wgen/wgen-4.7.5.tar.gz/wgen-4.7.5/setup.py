from setuptools import setup, find_packages

setup(
    name='wgen',
    version='4.7.5',
    author='lucasliu71',
    author_email='Lucasliu71@126.com',
    description='Wordlist generator for password brute force cracking using CPUs',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://gitee.com/lucasliu71/wgen',
    packages=find_packages(),
    install_requires=['psutil>=7.0.0', 'rich>=14.0.0'],
    entry_points={
        'console_scripts': [
            'wgen=wgen.wgen:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7'
)
