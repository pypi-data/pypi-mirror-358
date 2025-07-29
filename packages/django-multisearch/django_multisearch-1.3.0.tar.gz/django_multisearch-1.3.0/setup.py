from setuptools import setup, find_packages

setup(
    name = 'django-multisearch',
    version = '1.3.0',
    packages = find_packages(),
    author = 'Augusto Destrero',
    author_email = 'a.destrero@gmail.com',
    license='MIT',
    description = 'Multifield search for Django, using Bootstrap 3 and jQuery DataTables',
    url = 'https://github.com/baxeico/django-multisearch',
    keywords = ['django', 'search'],
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'six>=1.11',
    ]
)
