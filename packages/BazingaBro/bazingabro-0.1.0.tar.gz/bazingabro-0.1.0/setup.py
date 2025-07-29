# C:\Users\Lenovo\BooYaa\fahad-mcp-server\setup.py
from setuptools import setup, find_packages

setup(
    name='BazingaBro', # Changed package name as per your new file
    version='0.1.0', # Changed version as per your new file
    # FIX: Use find_packages() without 'where' if 'BazingaBroServ' is directly under setup.py's dir
    packages=find_packages(), # This will now find 'BazingaBroServ' if it's a direct subdirectory
    install_requires=["mcp"], # Updated install_requires as per your new file
    entry_points={
        'console_scripts': [
            # Changed console script name to 'BazingaBro'
            # Changed module path to 'BazingaBroServ.service:main'
            'BazingaBro=BazingaBroServ.service:main',
        ],
    },
    author='Fahad Khan',
    author_email='khan.fahad855@gmail.com',
    description='An MCP server for integrating with X system.',
    # Keep license as a simple string for modern builds, consistent with removing classifier
    license='MIT', # Assuming MIT license as before, or specify if different
    long_description=open('README.md').read(), # Ensure README.md exists in the same directory
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/BazingaBro', # Recommended: Link to your GitHub repo, updated for new name
    classifiers=[
        # Changed Python version classifier as per your new file
        'Programming Language :: Python :: 3.11',
        # Removed deprecated license classifier as 'license=' handles it
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Framework :: FastAPI' # If applicable
    ],
    # Ensure python_requires matches the classifier
    python_requires='>=3.10',
)
