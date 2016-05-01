from os.path import join, dirname
from setuptools import setup


LONG_DESCRIPTION = """
KSP Login is an app for easy authentication management with support for
social as well as traditional authentication.
"""


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), 'README.rst')).read()
    except IOError:
        return LONG_DESCRIPTION


install_requires = [
    'Django>=1.8',
    'python-social-auth',
]


try:
    import importlib
except ImportError:
    install_requires.append('importlib')


setup(
    name='ksp-login',
    version='0.4.0',
    author='Michal Petrucha',
    author_email='michal.petrucha@koniiiik.org',
    url='https://github.com/koniiiik/ksp_login',
    packages=['ksp_login', 'ksp_login.templatetags'],
    package_data={
        'ksp_login': [
            'locale/*/*/*.[mp]o',
            'static/ksp_login/css/*.css',
            'static/ksp_login/img/*.svg',
            'static/ksp_login/img/*.png',
            'static/ksp_login/img/*.txt',
            'static/ksp_login/js/*.js',
            'templates/ksp_login/*.html',
            'templates/ksp_login/parts/*.html',
        ],
    },
    license='BSD',
    description='A Django app for both traditional and social authentication',
    long_description=long_description(),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
