#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

# import io
import os
import sys
import shutil
from setuptools import find_packages, setup

version = "v5.0.1"


def read(f):
    return open(f, 'r', encoding='utf-8').read()


if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if os.system("twine check dist/*"):
        print("twine check failed. Packages might be outdated.")
        print("Try using `pip install -U twine wheel`.\nExiting.")
        sys.exit()
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('sparrowcloud.egg-info')
    sys.exit()


setup(
    name='sparrowcloud',
    version=version,
    license='MIT',
    description='基础Django和drf的微服务框架扩展',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='sparrow',
    author_email='',  # SEE NOTE BELOW (*)
    url='https://gitee.com/sparrow614/sparrow_cloud',
    packages=find_packages(include=[
                           'sparrow_cloud', 'sparrow_cloud.*', '*.sparrow_cloud.*', '*.sparrow_cloud']),
    include_package_data=True,
    install_requires=[
        'requests>=2.32.3',
        'coreapi>=2.3.3',
        'PyJWT>=2.9.0',
        'openapi_codec>=1.3.2',
        'dulwich>=0.22.1',
        'pika>=1.3.2',
        'cryptography>=43.0.0',
        'opentracing>=2.4.0',
        'jaeger-client>=4.8.0',
        'six>=1.16.0',
    ],
    python_requires=">=3.11",
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        # 'Framework :: Django',
        # 'Framework :: Django :: 1.9',
        # 'Framework :: Django :: 3.2',
         'Framework :: Django :: 4.2',
        # 'Intended Audience :: Developers',
        # 'Operating System :: OS Independent',
        # 'Programming Language :: Python',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
    ],

)
