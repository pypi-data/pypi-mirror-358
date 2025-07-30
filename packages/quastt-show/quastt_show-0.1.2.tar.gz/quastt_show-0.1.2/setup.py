from setuptools import setup, find_packages

setup(
    name="quastt_show",
    version="0.1.2",
    description="A trivia game with AI stats.",
    author="RVA",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "quastt-show=quastt_show.game:main",
        ],
    },
    include_package_data=True,
)
