import setuptools

setuptools.setup(
    name='glhmm',
    version='1.1.1',
    description='Gaussian Linear Hidden Markov Model',
    url='https://github.com/vidaurre/glhmm',
    author='Diego Vidaurre',
    author_email = "dvidaurre@cfin.au.dk",
    readme = "README.md",
    install_requires=['scipy','numpy','scikit-learn','matplotlib','numba','seaborn', 'pandas','igraph', 'tqdm', 'scikit-image','statsmodels', 'h5py','nibabel','requests','nilearn'],
    packages=["glhmm"],
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3"]
    )
