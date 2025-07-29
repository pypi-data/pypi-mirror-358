from setuptools import setup, find_packages

exec(open("runstardist/__version__.py", encoding="utf-8").read())

setup(
    name="run-stardist",
    version=__version__,
    author="Qin Yu",
    author_email="qin.yu@embl.de",
    license="MIT",
    description="Train and use StarDist models",
    url="https://github.com/kreshuklab/go-nuclear",
    project_urls={
        "Documentation": "https://kreshuklab.github.io/go-nuclear/",
        "Source": "https://github.com/kreshuklab/go-nuclear",
        "Bug Tracker": "https://github.com/kreshuklab/go-nuclear/issues",
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "train-stardist=runstardist.train:main",
            "predict-stardist=runstardist.predict:main",
        ],
    },
)
