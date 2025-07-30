# setup.py
import os
from setuptools import setup, find_packages

# README.md dosyasını oku
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='alfaslogger',
    version='0.1.1', # Paketinizin versiyon numarası
    author='OfficialAlfa', # Adınız veya şirketinizin adı
    author_email='sosyalfaone@gmail.com', # E-posta adresiniz
    description='A comprehensive Python logging module with console, file, database, and web GUI support.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TcAlfa31', # Projenizin GitHub veya benzeri deposunun URL'si
    packages=find_packages(),
    include_package_data=True, # MANIFEST.in dosyasını kullanmak için gerekli
    install_requires=[
        'websockets>=10.0', # websockets kütüphanesi gerekli olduğu için eklendi
        # Diğer bağımlılıklar buraya eklenebilir
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Kullandığınız lisansa göre değiştirin
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
    ],
    python_requires='>=3.7', # Desteklenen minimum Python sürümü
    keywords='logging, log, gui, websocket, sqlite, file, console',
)
