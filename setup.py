try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='social_auth_py',
    version='0.0.1',
    description=('Authentication middleware for various identity providers'),
    author='Pierre Ruyssen (AF83)',
    author_email='pierre@ruyssen.fr',
    url='https://github.com/AF83/social_auth_py',
    install_requires=[
        "oauth2>=1.1.3",
        "python_openid>=2.2.4",
        "simplejson>=2.1.1",
        "WebOb>=0.9.8",
    ],
    setup_requires=[""],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={},
    zip_safe=False,
)
