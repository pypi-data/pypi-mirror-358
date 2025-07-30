from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'readme.md').read_text(encoding='utf-8')

setup(
    name='windll-python',                    # Paket adı (PyPI’de benzersiz olmalı)
    version='0.1.0.post1',
    author='CSDC-K VV',
    author_email='mark.mark34234@gmail.com',  # Dilersen gerçek e-posta koy
    description='Easy way to use windows dlls with python.',
    long_description=long_description,                # README içeriği buraya
    long_description_content_type='text/markdown',   # README formatı
    url='https://github.com/CSDC-K/WinDll',  # GitHub veya projenin URL’si
    packages=find_packages(),       # LMS klasörünü otomatik bulur
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
