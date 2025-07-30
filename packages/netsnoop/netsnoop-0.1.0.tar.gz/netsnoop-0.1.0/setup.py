from setuptools import setup, find_packages

setup(
    name='netsnoop',
    version='0.1.0',
    description='NetSnoop: Real-Time Linux System Anomaly Monitor and Dashboard',
    author='Chitvi Joshi',
    author_email='chitvijoshi2646@gmail.com',
    license='MIT',  # ✅ Add this line!
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'pandas',
        'plotly'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
    ],
    entry_points={
        'console_scripts': [
            'netsnoop-init = netsnoop.setup_runner:main',
        ],
    },
    python_requires='>=3.7',
)
