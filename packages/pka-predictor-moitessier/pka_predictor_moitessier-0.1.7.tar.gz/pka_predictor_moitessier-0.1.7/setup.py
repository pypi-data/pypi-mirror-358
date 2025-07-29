from setuptools import setup, find_packages

setup(
    name="pka_predictor_moitessier",
    version="0.1.7",
    author="Moitessier Lab",
    author_email="nicolas.moitessier@mcgill.ca",
    description="Graph-based pKa prediction for small molecules",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MoitessierLab/pKa-predictor",
    license="GPL-3.0",
    keywords="pKa prediction GNN chemistry rdkit",
    packages=find_packages(include=['pka_predictor', 'pka_predictor.*'], exclude=["tests", "Datasets"]),
    install_requires=[
        #"torch>=2.0.0,<3.0",   # PyG users should install torch separately
        #"torch_geometric>=2.3.0",
        #"pandas>=1.5,<2.0",
        "numpy>=1.24",
        "seaborn>=0.12",
        "hyperopt>=0.2.7",
        # note: rdkit should be installed via conda-forge prior to pip install
        #"rdkit-pypi>=2025.3",
        "scikit-learn>=1.2.0",
    ],
    entry_points={
        "console_scripts": [
            "pka-predictor=pka_predictor.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)


### proteination states for each proteination site