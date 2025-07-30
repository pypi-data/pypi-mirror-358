from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="5.0.0",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="hanifx: Advanced Python Security, Time-Lock & Utility Toolkit",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540/hanifx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Utilities",
        "Development Status :: 5 - Production/Stable",
    ],
    project_urls={
        "GitHub": "https://github.com/hanifx-540/hanifx",
        "Facebook": "https://facebook.com/hanifx540",
        "Documentation": "https://github.com/hanifx-540/hanifx/blob/main/README.md"
    },
    python_requires='>=3.6',
)
