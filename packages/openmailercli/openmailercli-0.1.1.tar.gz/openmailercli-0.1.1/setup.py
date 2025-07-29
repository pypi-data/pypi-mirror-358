from setuptools import setup, find_packages
# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="openmailercli",
    version="0.1.1",
    description="A pure Python open-source email delivery tool",
    author="Mohamed Sesay",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "opmctl=cli.main:main"  # ✅ Command: opmcli -> cli/main.py:main()
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7'
)
