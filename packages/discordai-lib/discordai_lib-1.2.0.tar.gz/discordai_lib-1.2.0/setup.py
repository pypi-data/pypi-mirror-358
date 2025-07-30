
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="discordai-lib",
    version="1.2.0",
    author="VyeronServices",
    author_email="vyeronservices.official@gmail.com",
    description="Easy AI integration for Discord bots using Pollination.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VyeronServices/discordai-lib",
    packages=find_packages(),
    package_data={
        'discordailib': ['*.py'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "discord": ["discord.py>=2.3.0"],
    },
    keywords="discord, bot, ai, pollination, deepseek, grok, openai, chatbot, image generation",
    project_urls={
        "Bug Reports": "https://github.com/VyeronServices/discordai-lib/issues",
        "Source": "https://github.com/VyeronServices/discordai-lib",
        "Documentation": "https://github.com/VyeronServices/discordai-lib#readme",
        "Discord Support": "https://discord.gg/zsBNWvDu96",
    },
)
