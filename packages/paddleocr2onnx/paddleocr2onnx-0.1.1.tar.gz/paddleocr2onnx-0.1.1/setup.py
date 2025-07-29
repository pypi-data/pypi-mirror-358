from setuptools import setup, find_packages

setup(
    name="paddleocr2onnx",
    version="0.1.1",
    description="Fast & Lightweight OCR for vehicle license plates.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="francis",
    author_email="lidilek624@ofacer.com",
    url="https://github.com/lidilek/paddleocr2onnx",
    project_urls={
        "Documentation": "https://ankandrew.github.io/fast-plate-ocr"
    },
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Typing :: Typed",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.20",
        "opencv-python",
        "pyyaml>=5.1",
        "tqdm",
        "rich",
        "onnxruntime>=1.19.2",  # Simplified fallback handling
    ],
    entry_points={
        "console_scripts": [
            "fast_plate_ocr=fast_plate_ocr.cli.cli:main_cli"
        ]
    },
)

