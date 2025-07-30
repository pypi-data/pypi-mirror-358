import logging
import subprocess
import sys
from argparse import ArgumentParser


def execute():
    parser = ArgumentParser(
        prog='dbgear',
        description='database management tools'
    )
    parser.add_argument(
        '--project',
        default='database',
        help='please specify the folder for the project.')

    sub = parser.add_subparsers(dest='command', help='sub-command help')

    # Import command
    import_parser = sub.add_parser('import', help='import schema from external formats')
    import_parser.add_argument(
        'format',
        help='source format (e.g., a5sql_mk2)')
    import_parser.add_argument(
        'source_file',
        help='source file path')
    import_parser.add_argument(
        '--output',
        help='output YAML file path (default: schema.yaml)')
    import_parser.add_argument(
        '--mapping',
        help='schema mapping in format "KEY:VALUE,KEY2:VALUE2" (default: MAIN:main)')

    apply_parser = sub.add_parser('apply', help='apply help')
    apply_parser.add_argument(
        'deploy',
        help='target deployment.')
    apply_parser.add_argument(
        'env',
        help='target environment.')
    apply_parser.add_argument(
        '--database',
        help='target database.')
    apply_parser.add_argument(
        '--target',
        help='target table.')
    apply_parser.add_argument(
        '--all',
        choices=['drop', 'delta'],
        help='apply all tables. Specify "drop" to drop database before applying, or "delta" to apply only the changes since the last deployment.'
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    if args.command is None:
        parser.print_help()
        return

    if args.command == 'import':
        # Delegate to dbgear-import package
        try:
            import_cmd = ['dbgear-import', 'schema', args.format, args.source_file]

            if args.output:
                import_cmd.extend(['--output', args.output])

            if args.mapping:
                import_cmd.extend(['--mapping', args.mapping])

            logging.info(f'Delegating to dbgear-import: {" ".join(import_cmd)}')
            subprocess.run(import_cmd, check=True)

        except subprocess.CalledProcessError as e:
            logging.error(f'Import failed: {e}')
            sys.exit(e.returncode)
        except FileNotFoundError:
            logging.error('dbgear-import package not found. Please install it with: pip install dbgear-import')
            sys.exit(1)
    else:
        # For other commands, load project and required modules
        from .models.project import Project
        from .cli import operations

        project = Project.load(args.project)

        if args.command == 'apply':
            if not args.all and args.target is None:
                logging.error('please specify --target or --all')
                return
            operations.apply(
                project,
                args.env,
                args.database,
                args.target,
                args.all,
                args.deploy
            )
