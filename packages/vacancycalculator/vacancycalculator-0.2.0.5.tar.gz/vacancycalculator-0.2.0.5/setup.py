from setuptools import setup, find_packages

setup(
    name='vacancycalculator',
    version='0.2.0.5',
    author='TiagodBe',
    author_email='santiagobergamin@gmail.com',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    url='https://github.com/TiagoBe0/VFScript-CDScanner',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['scikit-learn', 'pandas', 'xgboost'],
    include_package_data=True,
)
