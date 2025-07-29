from setuptools import setup, find_packages

setup(
    name='hf-ms-transfer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'huggingface_hub',
        'modelscope',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'hf-ms-transfer = hf_ms_transfer.__main__:main',
        ],
    },
    author='Your Name', # TODO: Replace with your name
    author_email='your.email@example.com', # TODO: Replace with your email
    description='A tool to transfer models from Hugging Face to ModelScope',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/hf-ms-transfer', # TODO: Replace with your repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)