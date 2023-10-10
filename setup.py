from setuptools import setup, find_packages

def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content

setup(
    name='rsspush',
    version='0.0.5',
    description='rss推送',
    packages=find_packages(),
    author = 'buyfakett',
    author_email = 'buyfakett@vip.qq.com',
    long_description=readme(),                  # 长文字描述
    long_description_content_type='text/markdown',
    include_package_data=True,
    url='https://github.com/buyfakett/rsspush',
    package_data={
        'lqz_books': ['static/*', 'templates/*']
    },
    install_requires=[
        'Django==4.1.7',
    ]
)