"""
This code was architected, developed, and programmed by Ben-Hur Varriano for Sapiens Technology®️ (as well as all other AI algorithms of the company),
and any unauthorized alteration, adaptation, and/or distribution, as well as public comments and/or postings regarding the operation and/or mathematics involved in the algorithm, are strictly prohibited.
Failure to comply with these rules may result in legal action against the author by our team of attorneys.

The module in question comprises a sophisticated mathematical algorithm operated by a set of advanced applied mathematics functions, equations,
and calculations that collaboratively develop large language models (LLMs) with a novel approach and a revolutionary concept.
It differentiates itself from other architectures due to its ease of construction and efficiency in model training and inference.
The parameterization, training, and inference processes are significantly faster and require computational resources several orders of magnitude lower than those used by conventional model architectures.
Furthermore, the architecture can be used to train instruction-based models, chat-based models, or a combination of both.
Its tensor processing via streaming enables an infinite context window, and its adaptive response calculations allow the model to generalize to inputs it was not explicitly trained on.

We named the network SCNet, an abbreviation of "Semantic Comparison Network", referring to the underlying algorithm (also authored by Ben-Hur Varriano) that originated the current code.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'scnetwork'
version = '1.1.2'
from platform import system, machine
extras = []
if system().lower().strip() != 'darwin' or machine().lower().strip() != 'arm64': extras.append('torch-xla==2.7.0')
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=['torch==2.4.1', 'tiktoken==0.4.0', 'numpy==1.25.2', 'ijson==3.3.0', 'psutil==7.0.0', 'semantic-comparison-network==1.0.8', 'hurnet==1.0.8', 'requests==2.31.0', 'tqdm==4.67.1'] + extras,
    url='https://github.com/sapiens-technology/SCNet',
    license='Proprietary Software'
)
"""
This code was architected, developed, and programmed by Ben-Hur Varriano for Sapiens Technology®️ (as well as all other AI algorithms of the company),
and any unauthorized alteration, adaptation, and/or distribution, as well as public comments and/or postings regarding the operation and/or mathematics involved in the algorithm, are strictly prohibited.
Failure to comply with these rules may result in legal action against the author by our team of attorneys.

The module in question comprises a sophisticated mathematical algorithm operated by a set of advanced applied mathematics functions, equations,
and calculations that collaboratively develop large language models (LLMs) with a novel approach and a revolutionary concept.
It differentiates itself from other architectures due to its ease of construction and efficiency in model training and inference.
The parameterization, training, and inference processes are significantly faster and require computational resources several orders of magnitude lower than those used by conventional model architectures.
Furthermore, the architecture can be used to train instruction-based models, chat-based models, or a combination of both.
Its tensor processing via streaming enables an infinite context window, and its adaptive response calculations allow the model to generalize to inputs it was not explicitly trained on.

We named the network SCNet, an abbreviation of "Semantic Comparison Network", referring to the underlying algorithm (also authored by Ben-Hur Varriano) that originated the current code.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
