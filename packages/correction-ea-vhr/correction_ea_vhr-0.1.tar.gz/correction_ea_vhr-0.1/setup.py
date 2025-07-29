from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="correction_ea_vhr",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={"correction_ea_vhr": ["model/VHR.h5"]},
    install_requires=["tensorflow", "numpy", "pandas", "openpyxl"],
    description="Neural network correction tool for activation energy in VHR thermoluminescence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JF Benavente & JE Tenopala",
    url="https://github.com/Eduardo-TePe/correction_ea_vhr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)