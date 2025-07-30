from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='FloriaTelegramBotAPI',
    version='0.2.0',
    author='FloriaProduction',
    author_email='FloriaProduction@yandex.ru',
    description='Python Telegram Bot API',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='Apache-2.0',
    project_urls={
        "Source": 'https://github.com/FloriaProduction/FloriaTelegramBotAPI',
    },
    packages=find_packages(),
    install_requires=['httpx', 'pydantic'],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Console',
        "Intended Audience :: Developers",
        "Typing :: Typed"
    ],
    keywords='python api telegram bot tools',
    zip_safe=True,
    python_requires='>=3.12'
)