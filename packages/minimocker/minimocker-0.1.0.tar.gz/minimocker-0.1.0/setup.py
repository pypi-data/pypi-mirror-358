from setuptools import setup, find_packages

setup(
    name="minimocker",
    version="0.1.0",
    description="A simple, reloadable API mock server with JWT support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ram Awasthi",
    author_email="ram@skillsetpro.ai",
    url="https://github.com/ramsawasthi/minimocker",
    project_urls={
        "Documentation": "https://github.com/ramsawasthi/minimocker",
        "Source": "https://github.com/ramsawasthi/minimocker",
        "Tracker": "https://github.com/ramsawasthi/minimocker/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-jose",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "minimocker=minimocker.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
