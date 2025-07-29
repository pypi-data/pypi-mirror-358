from setuptools import setup

setup(
    name='office_editor_mcp',
    version='0.2.0.post1',
    py_modules=['powerpoint_server'],
    install_requires=[
        "annotated-types>=0.7.0",
        "anyio>=4.9.0",
        "click>=8.2.1",
        "Flask>=3.1.1",
        "httpcore>=1.0.9",
        "httpx>=0.28.1",
        "httpx-sse>=0.4.0",
        "itsdangerous>=2.2.0",
        "Jinja2>=3.1.6",
        "lxml>=5.4.0",
        "mcp>=1.9.3",
        "pillow>=11.2.1",
        "pydantic>=2.11.5",
        "pydantic-settings>=2.9.1",
        "pydantic_core>=2.33.2",
        "python-docx>=1.1.2",
        "python-dotenv>=1.1.0",
        "python-multipart>=0.0.20",
        "python-pptx>=1.0.2",
        "sniffio>=1.3.1",
        "sse-starlette>=2.3.6",
        "starlette>=0.47.0",
        "typing-inspection>=0.4.1",
        "typing_extensions>=4.14.0",
        "uvicorn>=0.34.3",
        "Werkzeug>=3.1.3",
        "XlsxWriter>=3.2.4",
        "oss2>=2.19.1",
        "loguru>=0.7.3"
    ],
    entry_points={
        'console_scripts': [
            'pptserver = powerpoint_server:main'
        ]
    },
)
