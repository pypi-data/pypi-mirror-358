from setuptools import setup, find_packages

setup(
    name='passwordrd',
    version='0.1.0',
    author='Seu Nome',
    author_email='seu.email@example.com',
    description='Executa eval() com senha e mensagens de erro detalhadas',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/seu_usuario/passwordrd',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
