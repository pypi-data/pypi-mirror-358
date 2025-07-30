import setuptools 

PACKAGE_NAME = "smartlink-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.67',  # https://pypi.org/project/smartlink-local/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles smart link Python",
    long_description="PyPI Package for Circles smart link Python",
    long_description_content_type='text/markdown',
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "logger-local>=0.0.136",
        "message-local>=0.0.142",
        "queue-worker-local>=0.0.37",
        "database-mysql-local>=0.0.290",
        "python-sdk-remote"
        # 'entity-type-local'
    ],
)
