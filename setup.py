# vim:et:ts=4:sts=4:ai
from setuptools import setup, find_packages
setup(
    name = "ServerBackupS3",
    version = "1.0.0",
    packages = find_packages(),
    install_requires = ["boto >= 2.3.0"],
    entry_points={
        'console_scripts': [
            'server-backup-s3 = ServerBackupS3.__main__:main',
        ],
    },
    author = "Philip J Freeman",
    author_email = "elektron@halo.nu",
    description = "streaming server backup to s3 using tar listed incremental and optional gnupg (PGP) encryption",
    license = "GPL3",
    keywords = "backup tar gpg s3",
    url = "https://github.com/ph1l/server-backup-s3",
)
