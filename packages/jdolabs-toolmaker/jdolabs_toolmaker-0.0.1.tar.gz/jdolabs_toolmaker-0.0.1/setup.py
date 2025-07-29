from setuptools import setup

setup(
    name="jdolabs-toolmaker",
    version="0.0.1",
    description="JdoLabs tool scaffolding system for rapid modular CLI + logic tool creation.",
    author="JdoLabs",
    packages=[],  # Nothing is imported as a package
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "jdolabs-toolmaker = main:main"
        ]
    },
    install_requires=[
        "typer>=0.9.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
