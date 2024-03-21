from setuptools import setup, find_packages

setup(
    name='wiki_graph_kb',
    version='0.0.0', 
    author='Panuthep Tasawong',
    author_email='panuthep.t_s20@vistec.ac.th',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)