import setuptools


def readme():
    with open("readme.md", "r") as f:
        return f.read()


setuptools.setup(
    name="multisafepay_payment",
    version="1.0.1",
    author="Akinon",
    author_email="dev@akinon.com",
    description="A library to provide payment gateway for MultisafePay Payment",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/akinonteam/multisafe-payment/",
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "dummy.*"]),
    zip_safe=False,
    install_requires=[
        "Django>=2.2.9,<4.0",
        "requests",
        "djangorestframework>=3.11.0,<3.15",
        "mock==4.0.3",
    ],
    include_package_data=True,
    package_data={"multisafepay_payment": ["templates/*"]},
)
