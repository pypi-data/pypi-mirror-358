import logging
from os import environ
from pathlib import Path
import sys

import click

from . import aws, config, utils
from .core import BashEnvConfig, FishEnvConfig, UserError


ENVVAR_PREFIX = 'ENV_CONFIG'
log = logging.getLogger(__name__)


def print_err(*args, **kwargs):
    # Flush is only needed to get tests to pass, see https://github.com/pallets/click/issues/2682
    print(*args, file=sys.stderr, flush=True, **kwargs)


def init_logs():
    utils.TMP_DPATH.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=utils.TMP_DPATH / 'env-config.log',
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s %(module)s %(funcName)s %(message)s',
    )


@click.command()
@click.argument('profiles', nargs=-1)
@click.option('--shell', type=click.Choice(('fish', 'bash')), required=True)
@click.option(
    '--config',
    'config_fpath',
    type=click.Path(dir_okay=False, path_type=Path),
    help='Default looks for env-config.yaml in CWD & parents',
)
@click.option(
    '--update',
    '-u',
    'is_update',
    is_flag=True,
    help='Only add new vars to environment.  Do not delete existing first.',
)
@click.option(
    '--debug',
    '-d',
    'is_debug',
    is_flag=True,
    help="Show info but don't actually set vars.",
)
@click.option(
    '--clear',
    '-c',
    'is_clear',
    is_flag=True,
    help='Delete vars from any profile from environment',
)
@click.option(
    '--list',
    '-l',
    'list_profiles',
    is_flag=True,
    help='List profile and group names in config',
)
@click.pass_context
def env_config(
    ctx: click.Context,
    shell: str,
    profiles: list[str],
    config_fpath: Path | None,
    is_update: bool,
    is_debug: bool,
    is_clear: bool,
    list_profiles: bool,
):
    try:
        start_at = config_fpath or Path.cwd()
        conf = config.load(start_at)

        envconf = FishEnvConfig(conf) if shell == 'fish' else BashEnvConfig(conf)

        if list_profiles:
            print('Profiles:\n    ', end='')
            print('\n    '.join(conf.profile))
            print('Groups:\n    ', end='')
            print('\n    '.join(conf.group))
            return

        is_show = False
        if not is_clear and len(profiles) == 0:
            is_show = True
            profiles = environ.get('_ENV_CONFIG_PROFILES', '').strip().split()
            if not profiles:
                print_err('No env-config profiles currently in use.')
                return

        if not is_update and not is_show:
            present_vars = sorted(envconf.present_env_vars())
            print_err('Clearing:')
            if present_vars:
                print_err('    ', ', '.join(present_vars))
            else:
                print_err('    ', 'No configured vars present to clear.')
            if not is_debug:
                envconf.clear_present_env_vars()

        if is_clear:
            return

        print_err('Profiles active:', ' '.join(profiles))
        print_err(
            'Active profile(s) configuration:' if is_show else 'Setting:',
        )
        for var, value in envconf.select(profiles).items():
            # Print to stderr for the user to see what's happening and keep stdout for the shell to
            # source
            print_err(f'    {var}:', value)

        if not is_debug and not is_show:
            envconf.set(profiles)
    except UserError as e:
        ctx.fail(str(e))


@click.command()
@click.argument('shell', type=click.Choice(('fish', 'bash')))
def env_config_shell(shell):
    fname = f'init.{shell}'
    config_fpath = Path(__file__).parent.joinpath('shells', fname)
    print(config_fpath.read_text())


@click.command()
@click.argument('aws_profile')
def env_config_aws(aws_profile: str):
    init_logs()

    config = aws.profile_config(aws_profile)
    sess_creds = aws.op_sess_creds(config.op_ref_base, config.mfa_serial)
    print(sess_creds.cli_json())


def main():
    env_config(auto_envvar_prefix=ENVVAR_PREFIX)
