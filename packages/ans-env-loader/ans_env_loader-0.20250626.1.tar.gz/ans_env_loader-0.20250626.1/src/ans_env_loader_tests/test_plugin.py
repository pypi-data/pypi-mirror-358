from pathlib import Path
import subprocess

from ans_env_loader_tasks_lib import sub_run


ansible_dpath = Path(__file__).parent.parent.parent / 'ansible'


def run_test(ident, inv_fpath='hosts', **kwargs) -> subprocess.CompletedProcess:
    dpath = ansible_dpath.joinpath(f'test-{ident}')

    return sub_run(
        'ansible-playbook',
        '-i',
        inv_fpath,
        'playbook.yaml',
        cwd=dpath,
        capture=True,
        **kwargs,
    )


class TestPlugin:
    def test_env_vars_not_present(self):
        result = run_test('ok', check=False)
        assert result.returncode == 1
        assert result.stderr.strip() == 'ERROR! Required env variables not set: foo, FLASK_SECRET'

        result = run_test('ok', env={'foo': 'baz'}, check=False)
        assert result.returncode == 1
        assert result.stderr.strip() == 'ERROR! Required env variables not set: FLASK_SECRET'

        result = run_test('ok', env={'foo': 'baz', 'FLASK_SECRET': 'make it so'})
        stdout = result.stdout
        assert '"foo": "baz"' in stdout
        assert '"app_flask_secret": "make it so"' in stdout

    def test_var_files_missing(self, tmp_path: Path):
        error_msg_start = 'ERROR! Expected "ans-env-vars.yaml" to exist in'
        error_msg_len = len(error_msg_start)

        result = run_test('file-missing', check=False)
        assert result.returncode == 1
        assert result.stderr.strip()[0:error_msg_len] == error_msg_start

        hosts_fpath = tmp_path.joinpath('hosts')
        hosts_fpath.write_text('localhost')

        result = run_test('file-missing', inv_fpath=hosts_fpath, check=False)
        assert result.returncode == 1
        assert result.stderr.strip()[0:47] == error_msg_start

    def test_not_list(self):
        result = run_test('not-list', check=False)
        assert result.returncode == 1
        assert (
            result.stderr.strip() == 'ERROR! Expected "ans-env-vars.yaml" to be a list of strings'
        )

    def test_nested_inventory(self):
        result = run_test(
            'nested-inv',
            inv_fpath='inv/hosts',
            env={'foo': 'baz', 'FLASK_SECRET': 'make it so'},
        )
        stdout = result.stdout
        assert '"foo": "baz"' in stdout
        assert '"app_flask_secret": "make it so"' in stdout
