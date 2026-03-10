import click
import yaml
from ..storage.sqlalchemy import SQLAlchemyStore
from ..core.models import Zone, Role, Operation
from ..validation.checker import validate_config

@click.group()
def cli():
    """ZRB Toolkit Command Line Interface"""
    pass

@cli.command()
@click.option('--db', default='sqlite:///zrb.db', help='Database URL')
def init(db):
    """Initialize the database."""
    store = SQLAlchemyStore(db)
    store.create_all()
    click.echo(f"Database initialized at {db}")

@cli.command()
@click.argument('file')
@click.option('--db', default='sqlite:///zrb.db')
def import_config(file, db):
    """Import configuration from YAML file."""
    with open(file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    store = SQLAlchemyStore(db)
    for z in data.get('zones', []):
        store.add_zone(Zone(**z))
    for op in data.get('operations', []):
        store.add_operation(Operation(**op))
    for r in data.get('roles', []):
        if isinstance(r.get('base_permissions'), list):
            r['base_permissions'] = set(r['base_permissions'])
        store.add_role(Role(**r))
    click.echo(f"Imported configuration from {file}")

@cli.command()
@click.option('--db', default='sqlite:///zrb.db')
def validate(db):
    """Validate the current configuration."""
    store = SQLAlchemyStore(db)
    errors = validate_config(store)
    if errors:
        for e in errors:
            click.echo(f"Error: {e}")
    else:
        click.echo("Configuration is valid.")

@cli.command()
@click.argument('zone_id')
@click.option('--db', default='sqlite:///zrb.db')
def zone_show(zone_id, db):
    """Show details of a zone."""
    store = SQLAlchemyStore(db)
    zone = store.get_zone(zone_id)
    if not zone:
        click.echo(f"Zone {zone_id} not found")
        return
    click.echo(f"Zone: {zone.name} ({zone.id})")
    click.echo(f"Parent: {zone.parent_id}")
    roles = store.get_zone_roles(zone_id)
    click.echo("Roles:")
    for r in roles:
        click.echo(f"  {r.name} ({r.id})")
