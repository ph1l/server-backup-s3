# vim:et:ts=4:sts=4:ai
from setuptools import setup, find_packages
setup(
    name = "ServerBackupS3",
    version = "1.0.0",
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'server-backup-s3 = ServerBackupS3.__main__:main',
        ],
    }
)
