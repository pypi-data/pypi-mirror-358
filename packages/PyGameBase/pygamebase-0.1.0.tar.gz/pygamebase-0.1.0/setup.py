from setuptools import setup

with open("README.md", "r", encoding="utf-8") as arq:
    readme = arq.read()

setup(
    name='PyGameBase',
    version='0.1.0',
    license='MIT',
    author='Thiago Silva Mendes',
    author_email='devscriptpy@gmail.com',
    description='Biblioteca para facilitar o uso do Pygame com sintaxe mais simples e componentes prontos.',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=['PyGameBase'],
    install_requires=[
        'pygame>=2.0.0',
        'Pillow>=8.0.0',
    ],
    keywords=['pygame', 'jogos', '2d', 'python', 'interface', 'PyGameBase'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Games/Entertainment',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    entry_points={
    'console_scripts': [
        'pygamebase = PyGameBase.cli:main',
    ],
},
)
