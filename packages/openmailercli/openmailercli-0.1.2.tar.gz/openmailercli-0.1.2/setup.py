from setuptools import setup, find_packages

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openmailercli",
    version="0.1.2",  # ✅ Bump version to upload again
    description="A pure Python open-source email delivery tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mohamed Sesay",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openmailer>=0.1.1",     # ✅ Core engine
        "python-dotenv>=1.0.0",  # ✅ For loading .env SMTP config
        "click>=8.0.0",          # ✅ If you're using click-based CLI
        "jinja2>=3.0.0",         # ✅ Inherited from openmailer
        "rich>=13.0.0",          # ✅ For terminal UI
        "pyyaml>=6.0.0",         # ✅ Template config parsing
        "requests>=2.0.0",
        "openmailer"
    ],
    entry_points={
        "console_scripts": [
            "opmctl=cli.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7'
)

