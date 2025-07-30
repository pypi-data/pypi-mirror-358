"""Setup configuration for pdf-section-binding package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from version.py
version_file = Path(__file__).parent / "src" / "pdf_section_binding" / "version.py"
version_dict = {}
exec(version_file.read_text(), version_dict)

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

setup(
    name="pdf-section-binding",
    version=version_dict["__version__"],
    author=version_dict["__author__"],
    author_email=version_dict["__email__"],
    description=version_dict["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/sravankumarrekandar/pdf-section-binding",  # Update this
    project_urls={
        "Bug Reports": "https://github.com/sravankumarrekandar/pdf-section-binding/issues",  # Update this
        "Source": "https://github.com/sravankumarrekandar/pdf-section-binding",  # Update this
        "Documentation": "https://github.com/sravankumarrekandar/pdf-section-binding#readme",  # Update this
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Printing",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyPDF2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "pylint>=3.0.0",
            "mypy>=1.0.0",
            "build>=1.0.0",
            "twine>=4.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-section-binding=pdf_section_binding.cli:main",
            "section-binding=pdf_section_binding.cli:main",  # Shorter alias
        ],
    },
    keywords=[
        "pdf",
        "bookbinding",
        "section-binding",
        "printing",
        "cli",
        "page-reordering",
        "signatures",
        "folding",
    ],
    zip_safe=False,
    include_package_data=True,
)
