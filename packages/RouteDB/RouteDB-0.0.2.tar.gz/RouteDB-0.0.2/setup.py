import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="RouteDB",
    version="0.0.2",
    author="itsoutchy",
    author_email="itsoutchy@itsoutchy.xyz",
    packages=["RouteDB"],
    description="A package which helps you manage local databases",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/itsoutchy-projects/RouteDB",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)