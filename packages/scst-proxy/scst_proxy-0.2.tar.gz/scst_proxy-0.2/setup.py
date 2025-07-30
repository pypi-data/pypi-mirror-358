from setuptools import setup, find_packages

setup(
    name='scst_proxy',
    version='0.2',
    package_dir={'': '.'},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'allianceauth>=2.0.0',
        'requests',
        'django-ipware',
    ],
    description='Register user on SCST proxy server',
    long_description='Provides registration for Alliance Auth users to register their credentials on proxy server.',
    author='Aleksey Misyagin',
    author_email='me@misyagin.ru',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    package_data={
        'html_templates': [
                'templates/*.*',
                'templates/**/*',
        ],
        'scst_proxy':[ 'static/*' ]
    }
)