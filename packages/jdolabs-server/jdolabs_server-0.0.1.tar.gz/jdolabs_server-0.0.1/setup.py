from setuptools import setup, find_packages

setup(
    name='jdolabs-server',
    version='0.0.1',
    packages=['logic'],
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'ai-server = main:main'
        ]
    },
    install_requires=[
        'fastapi',
        'uvicorn',
        'transformers',
        'safetensors',
        'torch'
    ],
    include_package_data=True,
    description='Local AI server with model loading, REST API, and multi-format LLM support',
    author='jdolabs',
    license='MIT'
)
