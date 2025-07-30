import os
from setuptools import setup, find_packages

# Caminho absoluto do diretório atual
this_directory = os.path.abspath(os.path.dirname(__file__))

# Caminho para o README.md
readme_path = os.path.join(this_directory, "README.md")

# Lê o conteúdo do README.md
with open(readme_path, "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='pygame_starter',
    version='0.3.3',  # ou a versão que estiver usando
    author='Seu Nome',
    description='Gerador automático de projetos base em Pygame com menu, resolução, cor e recorde',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pygame-starter = pygame_starter.gerador:main',
        ],
    },
)
