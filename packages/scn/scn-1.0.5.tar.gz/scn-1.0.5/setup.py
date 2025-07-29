"""
This code was architected, developed, and programmed by Ben-Hur Varriano for Sapiens Technology®️ (as well as all other AI algorithms of the company),
and any unauthorized alteration, adaptation, and/or distribution, as well as public comments and/or postings regarding the operation and/or mathematics involved in the algorithm, are strictly prohibited.
Failure to comply with these rules may result in legal action against the author by our team of attorneys.

This code is an extension of the SCNet algorithm with improvements in training and inference that allow it to run on custom devices.
It features an infinite context window that makes predictions through semantic comparisons between the user prompt and the inputs of the training or adjustment samples.
The SCN network operates on a layer of the HurNetTorch network that calculates weights in a single step without backpropagation in the fine-tuning training, which allows for huge speed gains during this phase.
The data reading and processing functions work with iterative streams, which allows the use of huge data sets without memory overflow or performance loss.

We named the network SCN, an abbreviation of "Semantic Comparison Network", referring to the underlying algorithm SCNet (also authored by Ben-Hur Varriano) that originated the current code.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'scn'
version = '1.0.5'
from platform import system, machine
extras = []
if system().lower().strip() != 'darwin' or machine().lower().strip() != 'arm64': extras.append('torch-xla')
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=['torch', 'tiktoken', 'numpy', 'ijson', 'psutil', 'scnetwork', 'hurnet-torch', 'requests', 'tqdm'] + extras,
    url='https://github.com/sapiens-technology/SCN',
    license='Proprietary Software'
)
"""
This code was architected, developed, and programmed by Ben-Hur Varriano for Sapiens Technology®️ (as well as all other AI algorithms of the company),
and any unauthorized alteration, adaptation, and/or distribution, as well as public comments and/or postings regarding the operation and/or mathematics involved in the algorithm, are strictly prohibited.
Failure to comply with these rules may result in legal action against the author by our team of attorneys.

This code is an extension of the SCNet algorithm with improvements in training and inference that allow it to run on custom devices.
It features an infinite context window that makes predictions through semantic comparisons between the user prompt and the inputs of the training or adjustment samples.
The SCN network operates on a layer of the HurNetTorch network that calculates weights in a single step without backpropagation in the fine-tuning training, which allows for huge speed gains during this phase.
The data reading and processing functions work with iterative streams, which allows the use of huge data sets without memory overflow or performance loss.

We named the network SCN, an abbreviation of "Semantic Comparison Network", referring to the underlying algorithm SCNet (also authored by Ben-Hur Varriano) that originated the current code.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
