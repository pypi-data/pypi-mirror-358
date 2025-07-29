from subprocess import call

from setuptools import setup
from setuptools.command.install import install


# simple wrapper around setuptools "install" that just adds the execution of
# python -c 'import imageio; imageio.plugins.freeimage.download()'
# after the standard install
class InstallWithFreeImage(install):
    def run(self):
        install.run(self)
        # https://github.com/imageio/imageio-freeimage?tab=readme-ov-file#installation
        call("python -c 'import imageio; imageio.plugins.freeimage.download()'")
        # Enable pre-commit hooks to check the code before committing
        call("pre-commit install")


setup(
    name="wai-core",
    version="1.0.3",
    description="WAI: World AI format unifying various 3D/4D datasets",
    long_description=open("readme.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Norman Mueller",
    author_email="normanm@meta.com",
    python_requires=">=3.10.0",
    package_dir={"": "."},
    packages=["wai"],
    package_data={"wai": ["colormaps/*.npz"]},
    install_requires=[
        "einops",
        "imageio",
        "matplotlib",
        "numpy",
        "opencv-python==4.10.0.84",  # Comment this out if using OpenCV from Conda
        "portalocker",
        "pillow",
        "pip",
        "plyfile",
        "python-box",
        "scipy",
        "torch",
        "torchvision",
        "tqdm",
        "iopath",
        "ruff",
        "pre-commit",
        "orjson",
        "pycolmap",
        "color-science",
    ],
)
