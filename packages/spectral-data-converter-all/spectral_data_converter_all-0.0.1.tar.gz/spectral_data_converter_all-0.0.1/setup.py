from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="spectral_data_converter_all",
    description="Meta-library that combines all spectral_data_converter libraries.",
    long_description=(
            _read('DESCRIPTION.rst') + b'\n' +
            _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/waikato-datamining/spectral-data-converter-all",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    license='MIT License',
    packages=[],
    install_requires=[
        "spectral_data_converter>=0.0.1",
        "spectral_data_converter_sklearn>=0.0.1",
        "spectral_data_converter_vis>=0.0.1",
    ],
    version="0.0.1",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
)
