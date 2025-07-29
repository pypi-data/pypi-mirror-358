from setuptools import setup, find_packages

setup(
    name='fahad_mcp_server',
    version='0.1.0',
    packages=find_packages(),
    install_requires=open(r'C:\Users\Lenovo\BooYaa\my-first-mcp-package\requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'fahad_mcp_server=fahad_server.server:main', # This defines your command
        ],
    },
    author='Fahad Khan',
    author_email='khan.fahad855@gmail.com',
    description='An MCP server for integrating with X system.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)