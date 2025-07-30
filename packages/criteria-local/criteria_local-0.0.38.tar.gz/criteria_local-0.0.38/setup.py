import setuptools

PACKAGE_NAME = "criteria-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/criteria-local
    version='0.0.38',
    author="Circles",
    author_email="info@circlez.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description="criteria-local",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "database-mysql-local>=0.1.10",
        # We changed hagging.logs to support Python 3.13.3 so we can use dateime.UTC in criteria-local-python-package
        "logger-local>=0.0.175",
        "opensearch-local>=0.0.8"
    ]
)
