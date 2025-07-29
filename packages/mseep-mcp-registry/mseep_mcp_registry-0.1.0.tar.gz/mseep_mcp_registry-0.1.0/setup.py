from setuptools import setup, find_packages

setup(
    name='mseep-mcp-registry',
    version='0.1.0',
    description='A registry for MCP servers',
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
    install_requires=['fastapi>=0.115.12', 'itsdangerous>=2.2.0', 'jinja2>=3.1.6', 'mcp>=1.8.0', 'pydantic>=2.11.3', 'httpx>=0.27.0', 'python-dotenv>=1.1.0', 'python-multipart>=0.0.20', 'uvicorn[standard]>=0.34.2', 'faiss-cpu>=1.7.4', 'sentence-transformers>=2.2.2', 'websockets>=15.0.1', 'scikit-learn>=1.3.0', 'torch>=1.6.0', 'huggingface-hub[cli]>=0.31.1', 'bandit>=1.8.3', 'langchain-mcp-adapters>=0.0.11', 'langgraph>=0.4.3', 'langchain-aws>=0.2.23', 'pytz>=2025.2'],
    keywords=['mseep'],
)
