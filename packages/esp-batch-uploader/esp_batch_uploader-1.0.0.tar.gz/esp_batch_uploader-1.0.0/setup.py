from setuptools import setup, find_packages

setup(
    name='esp-batch-uploader',
    version='1.0.0',
    description='Batch file uploader to ESP32 devices over HTTP with UDP discovery',
    author='Abdullah Bajwa',  # Optional but good practice
    packages=find_packages(exclude=["tests*", "examples*"]),  # Avoid packaging examples/tests
    install_requires=[
        'aiohttp'
    ],
    entry_points={
        'console_scripts': [
            'esp-upload = esp_batch_uploader.__main__:main_entry'
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
