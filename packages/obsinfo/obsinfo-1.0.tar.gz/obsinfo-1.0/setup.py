import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()
    print(long_description)
    
version={}
with open("src/obsinfo/version.py") as fp:
    exec(fp.read(),version)

setuptools.setup(
    name="obsinfo",
    version=version['__version__'],
    author="Wayne Crawford",
    author_email="crawford@ipgp.fr",
    description="Tools for documenting ocean bottom seismometer experiments and creating metadata",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/resif/smm/obsinfo",
    include_package_data=True,
    install_requires=[
          'numpy>=1.26',
          'obspy>=1.4',
          'pyyaml>=6.0',
          'jsonschema>=3.2,<4',
          'python-gitlab>=5.0',
          'jsonref>=1.1',
          'cartopy>=0.23.0',
          'requests>=2.28'
      ],
    entry_points={
        'console_scripts': [
            'obsinfo=obsinfo.console_scripts.argparser:main',
            'obsinfo-test=obsinfo.tests.run_test_script:run_suite_info_files',
            'obsinfo-makescript_LC2MSpy=obsinfo.addons.LC2MS:console_lc2mspy',
            'obsinfo-makescript_LC2SDSpy=obsinfo.addons.LC2SDS:console_script'
        ]
    },
    python_requires='>=3.9',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    keywords='seismology OBS'
)
