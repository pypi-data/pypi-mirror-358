from setuptools import setup, find_packages
# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="openmailer",
    version="0.1.1",
    description="Open-source email automation and delivery engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mohamed Sesay",
    author_email="msesay@dee-empire.com",
    url="https://github.com/Devops-Bot-Official/OpenMailer.git",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "jinja2",
        "rich",
        "pyyaml",
        "requests",
        # any others
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
)

