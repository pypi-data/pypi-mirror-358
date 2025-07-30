"""
Remote IKernel entry point.

From here you can get to 'manage', otherwise it is assumed
that a kernel is required instead and instance one instead.
"""
import sys

def main():
    """Enter into aap_ipykernel."""
    if "manage" in sys.argv:
        from aap_ipykernel.manage import manage
        manage()
    else:
        from aap_ipykernel.kernel import start_remote_kernel
        start_remote_kernel()

if __name__ == "__main__":
    main()
