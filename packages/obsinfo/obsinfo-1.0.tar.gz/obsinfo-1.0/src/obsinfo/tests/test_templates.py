"""
Runs schema, then print, the plot commands on every template file
"""
import pytest
import subprocess
from pathlib import Path

template_files = list(Path("../_templates").glob("*.yaml"))

@pytest.mark.parametrize("f", template_files)
def test_templates(f):
    print(f)
    _test_subcommand('schema', f)
    _test_subcommand('print', f)
    if 'polynomial' not in str(f):  # As of obspy 1.4.0, PolynomialResponseStage was not yet implemented
        _test_subcommand('plot', f)
    
def _test_subcommand(subcommand, f):
    value = subprocess.run(['obsinfo', subcommand, '--quiet', str(f)],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           check=True)
    assert value.returncode == 0, print('obsinfo {} {} returned {}'.format(
                                        subcommand, str(f), value.returncode))
    assert value.stdout == b'', print(value.stdout.decode('UTF-8'))
    
        
if __name__=="__main__":
    test_templates()