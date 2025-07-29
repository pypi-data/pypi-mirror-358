import setuptools


def get_readme():
    with open("README.rst") as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pygpeople",
    version="0.0.2",
    packages=[
        "pygpeople",
    ],
    package_data={
		"pygpeople": ["*.json"],
    },
    # from here all is optional
    description="Manage your contacts in google",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        "google",
        "contacts",
        "people",
        "python",
    ],
    url="https://veltzer.github.io/pygpeople",
    download_url="https://github.com/veltzer/pygpeople",
    license="MIT",
    platforms=[
        "python3",
    ],
    install_requires=[
        "pygooglehelper",
        "google-api-python-client",
        "pytconf",
        "pylogconf",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    entry_points={"console_scripts": [
        "pygpeople=pygpeople.main:main",
    ]},
)
