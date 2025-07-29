from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytest_zephyr_scale_integration",
    version="0.1.31",
    author="Sergey Popov",
    maintainer="Sergey Popov",
    author_email="sergey1404sergey@mail.ru",
    maintainer_email="sergey1404sergey@mail.ru",
    description="A library for integrating Jira Zephyr Scale (Adaptavist\TM4J) with pytest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PROaction/pytest-zephyr-scale-integration",
    license="MIT",
    packages=find_packages(),
    keywords="zephyr, zephyr-scale, adaptavist, TM4J, pytest, autocreate test cycle, pytest zephyr integration",
    install_requires=[
        "pytest",
        "python-dotenv",
        "requests",
        "requests-toolbelt",
    ],
    entry_points={
        'pytest11': [
            'pytest_zephyr_scale_integration = pytest_zephyr_scale_integration.conftest',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)