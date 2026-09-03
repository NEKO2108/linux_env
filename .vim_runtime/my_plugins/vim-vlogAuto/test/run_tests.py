#!/usr/bin/env python3
"""
Test runner for vlogAuto autodef tests.

Usage:
    cd ~/.vim/plugin
    python3 /usrhome/zengjie/projects/vim/tests/run_tests.py

Each .v file in tests/ is fed to proc_auto_define via a mock vim buffer.
The result is compared against the corresponding .expected file (if exists).
If no .expected file exists, the test just runs without failure and dumps output.
"""

import sys
import os
import glob
import io
import contextlib

# Add vlogAuto plugin dir to path
PLUGIN_DIR = '../plugin'
sys.path.insert(0, PLUGIN_DIR)

# Mock vim module
class MockBuffer:
    def __init__(self, lines, name=None):
        self._lines = list(lines)
        self.name = name
    def __len__(self): return len(self._lines)
    def __getitem__(self, idx):
        if isinstance(idx, slice): return self._lines[idx]
        return self._lines[idx]
    def __setitem__(self, idx, val):
        if isinstance(idx, slice): self._lines[idx] = list(val)
        else: self._lines[idx] = val
    def __iter__(self): return iter(self._lines)
    def __delitem__(self, idx): del self._lines[idx]
    def append(self, line, idx=None):
        if idx is None: self._lines.append(line)
        else: self._lines.insert(idx, line)

class MockVim:
    def __init__(self):
        self.current = type('C', (), {'buffer': None, 'window': None, 'line': None, 'column': None})()
    def eval(self, x): return '0'


def run_test(test_file):
    """Run proc_auto_define on test_file, return resulting buffer lines."""
    with open(test_file, 'r') as f:
        lines = [l.rstrip('\n') for l in f]

    mock = MockVim()
    mock.current.buffer = MockBuffer(lines, name=test_file)
    sys.modules['vim'] = mock

    # Force reimport to pick up latest vlogProcLib/vimCmdProc
    for mod_name in list(sys.modules.keys()):
        if mod_name in ('vlogProcLib', 'vimCmdProc', 'pyCmdProc'):
            del sys.modules[mod_name]

    from vimCmdProc import proc_auto_define

    stderr_buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr_buf):
            proc_auto_define(mock.current.buffer, test_file)
    except Exception as e:
        return mock.current.buffer, f"Exception: {e}\n{stderr_buf.getvalue()}"

    return mock.current.buffer, stderr_buf.getvalue()


def main():
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = sorted(glob.glob(os.path.join(tests_dir, '*.v')))

    print(f"Found {len(test_files)} test files in {tests_dir}")
    print("="*70)

    passed = 0
    failed = 0
    no_expected = 0

    for tf in test_files:
        name = os.path.basename(tf)
        expected_file = tf + '.expected'

        print(f"\n--- {name} ---")
        buffer, stderr = run_test(tf)
        if stderr:
            print(f"  stderr: {stderr.strip()[:200]}")

        if os.path.isfile(expected_file):
            with open(expected_file, 'r') as f:
                expected_lines = [l.rstrip('\n') for l in f]
            actual_lines = list(buffer)
            if actual_lines == expected_lines:
                print(f"  PASS (matches .expected)")
                passed += 1
            else:
                print(f"  FAIL (does not match .expected)")
                print(f"  --- Expected ---")
                for i, l in enumerate(expected_lines):
                    print(f"  {i+1:3d}: {l}")
                print(f"  --- Actual ---")
                for i, l in enumerate(actual_lines):
                    print(f"  {i+1:3d}: {l}")
                failed += 1
        else:
            print(f"  (no .expected file, dumping output)")
            for i, l in enumerate(buffer):
                print(f"  {i+1:3d}: {l}")
            no_expected += 1

    print("\n" + "="*70)
    print(f"Total: {len(test_files)} | PASS: {passed} | FAIL: {failed} | NO_EXPECTED: {no_expected}")


if __name__ == '__main__':
    main()
