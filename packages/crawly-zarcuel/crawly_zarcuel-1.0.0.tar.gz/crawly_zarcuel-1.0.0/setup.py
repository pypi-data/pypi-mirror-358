from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='crawly-zarcuel',
    version='1.0.0',
    description='A privacy-focused web scanner that detects cookies and trackers.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Zarcuel',
    author_email='zarcuelkali@gmail.com',
    url='https://github.com/Zarcuel/Crawly',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'playwright',
    ],
    entry_points={
        'console_scripts': [
            'crawly-zarcuel=crawly.crawly:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
