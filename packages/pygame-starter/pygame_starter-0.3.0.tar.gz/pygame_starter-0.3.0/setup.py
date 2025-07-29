from setuptools import setup, find_packages

setup(
    name='pygame_starter',
    version='0.3.0',
    author='Seu Nome',
    description='Gerador automático de projetos base em Pygame com menu, resolução, cor e recorde',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'pygame-starter = pygame_starter.gerador:main',
        ],
    },
    include_package_data=True,
)
