from setuptools import setup, find_packages

with open("readme.md","r") as f:
    description= f.read()

setup(
    name="dq_summary_llm",
    version="0.1",
    packages=find_packages(),
    install_requires=['pandas','openai'],
    author="Sivananda Panda",
    author_email="pandasivananda@gmail.com",
    long_description=description,
    long_description_content_type="text/markdown"
)