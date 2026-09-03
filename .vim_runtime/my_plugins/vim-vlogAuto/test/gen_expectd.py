#!/usr/bin/env python3
"""Generate .expected files by running each test once and saving the buffer."""

import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_tests import run_test


def main():
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = sorted(glob.glob(os.path.join(tests_dir, '*.v')))

    for tf in test_files:
        buffer, stderr = run_test(tf)
        expected_file = tf + '.expected'
        with open(expected_file, 'w') as f:
            for line in buffer:
                f.write(line + '\n')
        print(f"  wrote {os.path.basename(expected_file)}")


if __name__ == '__main__':
    main()
