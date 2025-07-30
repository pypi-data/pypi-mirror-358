from setuptools import setup, find_packages

setup(
    name="hancsv",
    version="1.02",
    description="A utility for handling CSV files, supports Hancom Cell CSV file (for cybersecurity demo purposes only).",
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type="text/markdown",
    author="Jaehoon Lee",
    author_email='68533989+jaehoon0905@users.noreply.github.com',
    install_requires=[],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
    ],
    python_requires='>=3.6',
)
