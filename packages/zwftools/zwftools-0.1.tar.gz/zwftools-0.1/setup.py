from setuptools import setup, find_packages
 
setup(
    name='zwftools',
    version='0.1',
    packages=find_packages(),
    install_requires=['pandas','hana_ml','sqlalchemy'],  # 依赖列表
)