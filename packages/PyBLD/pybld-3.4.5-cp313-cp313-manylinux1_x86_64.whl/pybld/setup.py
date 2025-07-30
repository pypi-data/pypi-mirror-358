from setuptools import setup,find_packages
from distutils.core import Extension
from distutils.misc_util import get_numpy_include_dirs
import os
incdir = get_numpy_include_dirs()
setup(
    name = "PyBLD",
    version = "3.3",
    description = "BLD for Python",
    author = "Hiroshi Watabe",
    author_email = "watabe@cyric.tohoku.ac.jp",
    url = "http://www.rim.cyric.tohoku.ac.jp/pybld/pybld.html",
    license = "GNU Library General Public License (GPL) Version 2",
    platform = "OS Independent",
    packages = find_packages(),
    include_package_data=True,
    package_data = {
        '': ['HISTORY'],
    },
    ext_package = "pybld",
    ext_modules = [Extension("_bldanaimgc",['bldanaimgc_wrap.c','img_transform.c','bld_util.c'],include_dirs=incdir),Extension("_pybldc",['bld_interpolate.c','bld_integrate.c','bld_conv_exp.c','bld_pconv_exp.c','bld_util.c','bld_random.c','random.c','bld_mullin.c','bld_polfit.c','bld_fitsub.c','bld_fit.c','bld_iter.c','bld_convg.c','bld_testcg.c','bld_subit.c','bld_filter.c','conv_exp.c','pconv_exp.c','interpolate.c','integrate.c','dminv.c','filter.c','matrixbld.c','dconex.c','mullin.c','pybldc_wrap.c','bld_splfit.c'],include_dirs=incdir)],
),
#copy startup file
if os.name == 'posix':
    home = os.environ['HOME']
    os.system('cp pybld_start.py %s/.pybld_start' % (home))
    print("Please copy bin/pybld and bin/gen_pybld_pass.py into your binary PATH")
