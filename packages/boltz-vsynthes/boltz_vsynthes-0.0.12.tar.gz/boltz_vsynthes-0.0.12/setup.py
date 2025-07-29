from setuptools import setup, find_packages

setup(
    # ... existing setup args ...
    entry_points={
        'console_scripts': [
            'boltz-sdf-to-pre-affinity=boltz.utils.sdf_to_pre_affinity_npz:main',
        ],
    },
) 