from setuptools import setup


setup(
    name="nex_protocols_common_py",
    version="0.2.1",
    description="NEX protocols common for use to easily create NEX Servers.",
    packages=["nex_protocols_common_py"],
    package_dir={"nex_protocols_common_py": "."},
    install_requires=[
        "pymongo",
        "nintendoclients"
    ],
    python_requires=">=3.7",
)