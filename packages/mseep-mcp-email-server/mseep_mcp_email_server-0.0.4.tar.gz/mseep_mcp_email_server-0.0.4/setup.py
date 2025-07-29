from setuptools import setup, find_packages

setup(
    name='mseep-mcp-email-server',
    version='0.0.4',
    description='IMAP and SMTP via MCP Server',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/mseep',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['aioimaplib>=2.0.1', 'aiosmtplib>=4.0.0', 'gradio>=5.18.0', 'jinja2>=3.1.5', 'loguru>=0.7.3', 'mcp[cli]>=1.3.0', 'pydantic>=2.10.6', 'pydantic-settings[toml]>=2.8.0', 'tomli-w>=1.2.0', 'typer>=0.15.1'],
    keywords=['mseep', 'MCP', 'IMAP', 'SMTP', 'email'],
)
