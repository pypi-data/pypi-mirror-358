# default to setuptools so that 'setup.py develop' is available,
# but fall back to standard modules that do the same
import setuptools

if __name__ == "__main__":
    setuptools.setup()