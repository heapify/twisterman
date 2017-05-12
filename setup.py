from setuptools import setup, find_packages

setup(
    name = 'twisterman',
    packages = find_packages(),
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    entry_points={
        "console_scripts": [
            "twisterman = twisterman:main"
        ]
    },
    install_requires = ['Twisted', 'PyYAML'],
)
