from setuptools import find_packages, setup

long_description = """
Custom fork of instagrapi (Instagram Private API wrapper) with personalized features, rate-limit patches, and device configuration.

Changes:
- Custom UUID/session/user-agent handling
- Rate-limit delay options
- Local development flexibility
"""

requirements = [
    "requests<3.0,>=2.25.1",
    "PySocks==1.7.1",
    "pydantic==2.11.5",
    "pycryptodomex==3.23.0",
]

setup(
    name="voidgrapibro",  # ⬅️ NEW NAME TO AVOID CONFLICT
    version="2.1.5.post1",  # ⬅️ CUSTOM VERSION
    author="void",
    author_email="void@users.noreply.github.com",
    license="MIT",
    url="https://github.com/voiddev/voidgrapibro",  # ⬅️ optional GitHub link
    install_requires=requirements,
    keywords=[
        "instagram", "api", "private api", "reels", "stories", "uploader", "custom",
        "instagrapi", "void", "ratelimit bypass"
    ],
    description="Custom Instagram Private API with patched behavior",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
