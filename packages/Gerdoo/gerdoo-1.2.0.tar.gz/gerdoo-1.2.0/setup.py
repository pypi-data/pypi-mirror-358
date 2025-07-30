from setuptools import setup, find_packages

setup(
    name='Gerdoo',
    version='1.2.0',
    author='MohammadReza',
    author_email='narnama.room@gmail.com',
    description='This unofficial library is built for using the Gerdoo search engine. You can use this tool to search the web, images, videos, news, and more. 🐍✨',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=[
        'requests',
        'beautifulsoup4'
    ],
    project_urls={
        'موتور جستجوی گردو 🌐' : 'https://gerdoo.me/',
        'صفحه من ❤️' : 'https://apicode.pythonanywhere.com/',
    },
)
