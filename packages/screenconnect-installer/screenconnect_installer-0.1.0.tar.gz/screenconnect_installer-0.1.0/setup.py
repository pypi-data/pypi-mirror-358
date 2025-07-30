from setuptools import setup, find_packages

setup(
    name='screenconnect-installer',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={'screenconnect_installer': ['connectwise.msi']},
    entry_points={
        'console_scripts': [
            'screenconnect-installer=screenconnect_installer.instalar:instalar',
        ],
    },
    author='Seu Nome',
    description='Instalador automático do ScreenConnect via pip',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
)
