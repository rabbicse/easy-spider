import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy_spider",
    version="0.0.1",
    author="MD. MEHEDI HASAN RABBI",
    author_email="rabbi.cse.sust.bd@gmail.com",
    description="A micro framework to create spider/crawler.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rabbicse/easy-spider.git",
    packages=setuptools.find_packages(exclude=("examples",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPL-3.0",
        "Operating System :: OS Independent",
    ],
)
