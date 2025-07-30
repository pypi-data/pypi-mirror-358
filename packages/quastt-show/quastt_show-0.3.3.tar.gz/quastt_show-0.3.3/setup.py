from setuptools import setup, find_packages

setup(
    name="quastt_show",
    version="0.3.3",
    description="Useful tools for monitoring,tracking,learning from mistakes.Just check our docs: https://quastt.com/",
    author="RVA",
    packages=find_packages(),
    install_requires=["requests","traceback","time","threading","concurrent"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "quastt-show=quastt_show.game:main",
        ],
    },
    include_package_data=True,
)
