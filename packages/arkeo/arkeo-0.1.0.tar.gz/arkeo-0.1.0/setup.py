from setuptools import setup, find_packages

setup(
  name="arkeo",
  version="0.1.0",
  author="arkeosaurus",
  author_email="sun.kwon09@myhunter.cuny.edu",
  description="markdown archiver betasaurus",
  long_description="Ideally, this inhales a lot of media and regurgitates markdown for a curated, research repository.",
  long_description_content_type="text/plain",
  url="https://github.com/arkeosaurus/arkeo",
  packages=find_packages(),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Text Processing",
    "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
  ],
  python_requires=">=3.8",
  install_requires=[
    "newspaper3k",
    "html2text",
    "requests",
    "beautifulsoup4",
    "tqdm",
  ],
  keywords="document processing, archiving, indexing, markdown, corpus",
)