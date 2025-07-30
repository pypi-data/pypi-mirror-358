import pytest
import subprocess
from pathlib import Path

inst_files = list(Path("../_examples/instrumentation_files").glob("**/*.yaml"))
subnetwork_files = list(Path("../_examples/subnetwork_files").glob("**/*.yaml"))

@pytest.mark.parametrize("f", inst_files)
def test_instrumentation_examples(f):
    print(f)
    _test_subcommand('schema', f)
    _test_subcommand('print', f)
    _test_subcommand('configurations', f)
    _test_subcommand('plot', f)
    
@pytest.mark.parametrize("f", subnetwork_files)
def test_subnetwork_examples(f):
    print(f)
    _test_subcommand('schema', f)
    _test_subcommand('print', f)
    _test_subcommand('configurations', f)
    _test_subcommand('plot', f)
    
def _test_subcommand(subcommand, f):
    value = subprocess.run(['obsinfo', subcommand, '--quiet', f],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           check=True)
    assert value.returncode == 0, print('obsinfo {} {} returned {}'.format(
                                        subcommand, str(f), value.returncode))
    assert value.stdout == b'', print(value.stdout.decode('UTF-8'))
    
if __name__=='__main__':
    test_examples()
