from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dash_stylish_header_footer_hook",
    version="0.0.1",
    install_requires=[
        "dash>=3.0.3",
        "flask_login",
    ],
    entry_points={
        "dash_hooks": [
            "dash_stylish_header_footer_hook = dash_stylish_header_footer_hook"
        ]
    },
    packages=find_packages(),
    author="koveszter",
    description="Dash hook for stylish header and footer",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Ez fontos, ha markdown a README
    url="https://github.com/banana0000/dash_stylish_header",
)