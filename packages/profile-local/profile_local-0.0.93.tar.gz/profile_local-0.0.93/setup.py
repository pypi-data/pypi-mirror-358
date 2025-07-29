import setuptools

PACKAGE_NAME = "profile-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.93',  # https://pypi.org/project/profile-local/
    author="Circles",
    author_email="info@circlez.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    description="This is a package for sharing common crud operation to profile schema in the db",
    long_description="This is a package for sharing common profile functions used in different repositories",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "database-mysql-local>=0.0.290",
        "email-address-local>=0.0.40",
        "gender-local>=0.0.10",
        "group-remote>=0.0.111",
        "group-profile-remote>=0.0.29",
        "language-remote>=0.0.20",
        "location-local>=0.0.103",
        "logger-local>=0.0.135",
        "operational-hours-local>=0.0.23",
        "profile-profile-local>=0.0.18",
        "profile-reaction-local>=0.0.17",
        "reaction-local>=0.0.17",
        "location-profile-local>=0.0.51",
        "person-local>=0.0.51",
        "user-context-remote>=0.0.75",
        "storage-local>=0.1.38",
        "python-sdk-remote>=0.0.93",
        "visibility-local>=0.0.3",
    ]
)
