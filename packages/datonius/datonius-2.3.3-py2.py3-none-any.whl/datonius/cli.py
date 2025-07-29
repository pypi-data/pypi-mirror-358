import click

import simplejson

import functools
import logging

from tabulate import tabulate
from datonius import *
import datonius.util as util
from peewee import DoesNotExist

@click.group()
@click.option('-d', '--db', 'database', default=None, metavar='PATH', help='path to a Datonius database in SQLite format.')
@click.option('-v', '--verbose', count=True)
@click.pass_context
def cli(ctx, database, verbose):
    ctx.ensure_object(dict)
    ctx.obj['database'] = database
    log_level = {0:60, 1:30, 2:20, 3:10}[verbose]
    logging.basicConfig(level=log_level,
                        format='[%(asctime)s][%(name)-12s][%(levelname)-8s] %(message)s',
                        datefmt='%m-%d %H:%M')


def first_value_or_default(iterable, default=None):
    try:
        return next(iter(iterable))
    except StopIteration:
        class DefaultEmptyObject:
            def __init__(self, default):
                self.default = default

            def __getattr__(self, name):
                return self.default
        return DefaultEmptyObject(default)


def isolate_to_dict(name, iso, can_nest=False):
    if not iso:
        click.echo(f"{name} not found.", err=True)
        return {}
    rec = dict(
            accession=iso.fda_accession,
            organism=str(iso.binomial),
            gims_barcode=iso.barcode,
            strain=iso.strain_name,
            pulsenet_key=iso.fda_pulse_net_key,
            biosample=iso.biosample,
            collection_date=iso.sample.collection_date.isoformat(),
            related_food=iso.sample.related_food
    )
    if can_nest:
        # formats where we can nest dictionaries
        rec['foodon'] = iso.sample.related_food_ontology_code
        rec['collection_date_range'] = f"{iso.sample.collection_date - iso.sample.collection_date_accuracy_mask} - {iso.sample.collection_date + iso.sample.collection_date_accuracy_mask}"
        rec['collection_reason'] = iso.sample.collection_reason
        rec['firms'] = [
            dict(
                rel_code = rel.relationship_code,
                firm_fei = rel.firm.fei,
                firm_name = rel.firm.name,
                firm_address = rel.firm.address.full,
                was_responsible = rel.responsibility
            )
        for rel in iso.sample.firm_relationships]
        #other stuff
    else:
        # alternate summary views
        rec['responsible_firm_fei'] = first_value_or_default(iso.sample.responsible_firms).fei
        rec['responsible_firm_name'] = first_value_or_default(iso.sample.responsible_firms).name
    return rec

def sample_to_dict(sam):
    return dict(

    )

table = functools.partial(tabulate, headers='keys', tablefmt='simple')
tsv = functools.partial(tabulate, headers='keys', tablefmt='tsv')
json = functools.partial(simplejson.dumps, indent=2, iterable_as_array=True)

@cli.command()
@click.argument('names', nargs=-1, metavar="NAME")
@click.option('-o', '--output', type=click.File('wt'), default=click.get_text_stream('stdout'))
@click.option('-h', '--human-readable', 'output_format', flag_value=util.TABLE, help='Output in a human-readable table.', default=util.TABLE)
@click.option('-j', '--json', 'output_format', flag_value=util.JSON, help='Output in JSON.')
@click.option('-t', '--tsv', 'output_format', flag_value=util.TSV, help='output in TSV format.')
@click.option('-a', '--all-fields', flag_value=True, default=False)
@click.pass_context
def lookup(ctx, names, output, output_format, all_fields=False):
    "Lookup a name and retreive isolate information."
    if output_format is util.TABLE and output is not click.get_text_stream('stdout'):
        output_format = util.TSV # coerce to TSV if we're going to a file
    try:
        with make_connection(ctx.obj['database']):
            click.echo(util.lookup(names, output_format, all_fields) or f"{names} not found.", file=output)
    except Exception as e:
        click.echo(str(e), err=True)
        exit(1)

@cli.command()
@click.argument('names', nargs=-1, metavar="TAXON")
@click.option('-o', '--output', type=click.File('wt'), default=click.get_text_stream('stdout'))
@click.option('-h', '--human-readable', 'output_format', flag_value=util.TABLE, help='Output in a human-readable table.', default=util.TABLE)
@click.option('-j', '--json', 'output_format', flag_value=util.JSON, help='Output in JSON.')
@click.option('-t', '--tsv', 'output_format', flag_value=util.TSV, help='output in TSV format.')
@click.option('-a', '--all-fields', flag_value=True, default=False)
@click.pass_context
def tax(ctx, names, output, output_format, all_fields=False):
    "Lookup a taxon and retreive information for its isolates."
    if output_format is util.TABLE and output is not click.get_text_stream('stdout'):
        output_format = util.TSV # coerce to TSV if we're going to a file
    with make_connection(ctx.obj['database']):
        try:
            click.echo(util.tax(names, output_format, all_fields), file=output)
        except DoesNotExist:
            click.echo(f"{' '.join(names)} isn't a taxon in the database.", err=True)
            exit(1)
        except Exception as e:
            click.echo(str(e), err=True)
            exit(1)

@cli.command()
@click.argument('names', nargs=1, metavar="ONTOLOGY TERM")
@click.option('-o', '--output', type=click.File('wt'), default=click.get_text_stream('stdout'))
@click.option('-h', '--human-readable', 'output_format', flag_value=util.TABLE, help='Output in a human-readable table.', default=util.TABLE)
@click.option('-j', '--json', 'output_format', flag_value=util.JSON, help='Output in JSON.')
@click.option('-t', '--tsv', 'output_format', flag_value=util.TSV, help='output in TSV format.')
@click.option('-a', '--all-fields', flag_value=True, default=False)
@click.pass_context
def ontology(ctx, names, output, output_format, all_fields=False):
    "Find isolates according to one or more ontology terms from the FOODON ontology."
    if output_format is util.TABLE and output is not click.get_text_stream('stdout'):
        output_format = util.TSV # coerce to TSV if we're going to a file
    with make_connection(ctx.obj['database']):
        try:
            click.echo(util.ontology(names, output_format, all_fields), file=output)
        except Exception as e:
            click.echo(str(e), err=True)
            exit(1)

if __name__ == '__main__':
    cli(obj={})