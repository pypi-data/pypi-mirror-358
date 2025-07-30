from setuptools import setup, find_packages

setup(
    name="michael_agent",
    version="1.0.3",
    description="SmartRecruitAgent - A recruitment automation library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Michael Jone",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/agent",
    packages=find_packages(include=["michael_agent", "michael_agent.*"]),
    install_requires=[
        "python-dotenv",
        "langchain",
        "langgraph",
        "langchain-openai",
        "PyPDF2",
        "pymupdf",
        "flask",
        "requests",
        "watchdog",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)

"""
MIT License

Copyright (c) 2025 Michael Jone

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

...
"""