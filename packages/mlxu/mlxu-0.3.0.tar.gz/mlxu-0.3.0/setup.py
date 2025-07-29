from setuptools import setup, find_packages

setup(
    name='mlxu',
    version='0.3.0',
    license='MIT',
    description='Machine learning experiment utils.',
    url='https://github.com/young-geng/mlxu',
    packages=find_packages(include=['mlxu']),
    python_requires=">=3.7",
    install_requires=[
        'absl-py',
        'ml-collections',
        'wandb',
        'gcsfs',
        'cloudpickle',
        'numpy',
    ],
    extras_require={
        'jax': [
            'jax',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
)