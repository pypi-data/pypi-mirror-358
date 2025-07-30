from setuptools import setup, find_packages

setup(
    name='meta-truemoney-api',
    version='0.1.0',
    description='โมดูล Python สำหรับเชื่อม API ซองอั่งเปา TrueMoney (ไม่มีค่าธรรมเนียม)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='DEVPARK',
    author_email='0924011344aa@email.com',
    url='https://github.com/yourname/meta-truemoney-api',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
