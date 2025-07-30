
"""
Setup script for HiDT.

"""
import os, sys, glob
import setuptools

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if (sys.version_info.major < 3) or (sys.version_info.major == 3 and sys.version_info.minor < 7):
    print(
        f"Python >=3.7 is required. You are currently using Python {sys.version.split()[0]}"
    )
    sys.exit(2)

# Guarantee Unix Format
for src in glob.glob('scripts/*'):
    text = open(src, 'r').read().replace('\r\n', '\n')
    open(src, 'w').write(text)

setuptools.setup(
    name = 'hidt',
    version = "0.1.2",
    author = "Li Junping",
    author_email = 'lijunping02@qq.com',
    url = 'https://github.com/GaoLabXDU/HiDT',
    description = 'A computational pipeline for identifying differential TADs from 3D genome contact maps',
    keywords = ("3D genome", "Comparative analysis", "Topologically associating domains"),
    scripts = glob.glob('scripts/*'),
    packages = setuptools.find_packages(),
    include_package_data = True,
    package_data={
        "hidt": ["pretrained_model.pth"],
    },
    platforms = "any",
    license="MIT Licence",
    install_requires = [
        "numpy",
        "pandas",
        "scikit-learn",
        "hic-straw==1.3.1"
        ]
    )
