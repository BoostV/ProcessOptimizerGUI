import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'plaster_pastedeploy',
    'pyramid==1.10.4',
    'pyramid_debugtoolbar',
    'substanced',
    'pyramid_tm==2.3',
    'pyramid_retry',
    'waitress',
    'scikit-optimize',
    'matplotlib',
    'mock',
    'RelStorage[postgresql]',
    'ProcessOptimizer>=0.6.1'
    ]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    ]

setup(name='AIFrontend',
      version='0.0',
      description='AIFrontend',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Bjarne Enrico Nielsen',
      author_email='bj000555@hotmail.com',
      url='',
      keywords='ProcessOptimizer',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = AIFrontend:main
      """,
      )
