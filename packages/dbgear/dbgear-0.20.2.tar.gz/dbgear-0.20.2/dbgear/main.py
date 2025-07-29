import logging
from argparse import ArgumentParser

from .cli.importer import import_schema


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
        # Parse mapping parameter
        mapping = {'MAIN': 'main'}  # default
        if args.mapping:
            mapping = {}
            for pair in args.mapping.split(','):
                key, value = pair.split(':')
                mapping[key.strip()] = value.strip()

        # Determine source file directory and filename
        from pathlib import Path
        source_path = Path(args.source_file)
        folder = str(source_path.parent)
        filename = source_path.name

        # Import schema
        try:
            logging.info(f'Importing schema from {args.source_file} using {args.format} format...')
            schema_manager = import_schema(args.format, folder, filename, mapping)

            # Save to YAML file
            output_path = args.output or 'schema.yaml'
            schema_manager.save(output_path)
            logging.info(f'Schema successfully imported and saved to {output_path}')

        except Exception as e:
            logging.error(f'Import failed: {e}')
            return
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
