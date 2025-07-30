from setuptools import setup, find_packages

setup(
    name="mybashbuddy",
    version="0.1.1",
    description="AI-powered shell assistant and coding companion",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Atharva Dethe",
    author_email="atharvadethe2004@gmail.com",
    url="https://github.com/Atharvadethe/BashBuddy",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "google-generativeai",
        "pyperclip"
    ],
    entry_points={
        "console_scripts": [
            "bashbuddy=bashbuddy.main:app"
        ]
    },
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 