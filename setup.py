from setuptools import setup, find_packages

setup(
    name='tuktuk_maintenance',
    version='0.1.0',
    description='Maintenance Management Addon for Sunny TukTuk Fleet',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Yuda Media',
    author_email='yuda@graphicshop.co.ke',
    url='https://github.com/yudamedia/tuktuk-maintenance',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'tuktuk_management>=0.1.4'  # Depends on base system
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Fleet Management',
        'Topic :: Office/Business :: Maintenance',
    ],
    keywords=['erpnext', 'maintenance', 'fleet-management', 'tuktuk', 'addon'],
    python_requires='>=3.10',
)
