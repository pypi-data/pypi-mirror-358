import click
from loguru import logger
from jinja_rdf import register_filters, get_context
from rdflib import Graph, URIRef
from rdflib.util import from_n3
from jinja_rdf.rdf_resource import RDFResource
import jinja2
import sys
from pathlib import Path


def jinja_template(
    template: str | jinja2.Template | Path,
    graph: Graph,
    template_searchpath: Path = None,
):
    templateLoader = None
    """Configure the searchpath to look in the current directory, so that it
    find templates specified with relative paths, and in the templates parent so
    that it find relative includes."""
    searchpath = [template_searchpath or "."]
    if isinstance(template, Path):
        searchpath.insert(0, str(template.parent))
    templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
    environment = jinja2.Environment(loader=templateLoader)
    register_filters(environment)
    if isinstance(template, Path):
        return environment.get_template(str(template))
    else:
        return environment.from_string(template)


def render(
    template: str | jinja2.Template | Path,
    graph: Graph,
    resource: RDFResource | URIRef | str,
    template_searchpath: Path = None,
):
    return jinja_template(template, graph, template_searchpath).render(
        get_context(graph, resource)
    )


def stream(
    template: str | jinja2.Template | Path,
    graph: Graph,
    resource: RDFResource | URIRef | str,
    template_searchpath: Path = None,
):
    return jinja_template(template, graph, template_searchpath).stream(
        get_context(graph, resource)
    )


@click.group()
@click.option("--loglevel", default="INFO")
def cli(loglevel):
    logger.remove()
    logger.add(sys.stderr, level=loglevel)
    if loglevel in ["DEBUG"]:
        logger.debug(f"Loglevel is {loglevel}")


@cli.command()
@click.option("--template", "-t")
@click.option("--template-searchpath", "-s", default=None)
@click.option("--graph", "-g")
@click.option(
    "--resource",
    "-r",
    help="Provide the resource IRI in n3 syntax (e.g. <https://example.org/res>)",
)
@click.option("--compatibility", "-c", default=None)
@click.option("--output", "-o", default="-")
def build(template, template_searchpath, graph, resource, output, compatibility):
    if compatibility == "jekyll-rdf":
        click.echo(
            "Currently there is no compatibility to jekyll-rdf implemented, it will probably not cover 100% but if you would like to implement some thing, please send me pull-requests."
        )
        return

    if output == "-":
        output = sys.stdout

    if template_searchpath:
        template_searchpath = Path(template_searchpath)

    g = Graph()
    g.parse(graph)

    stream(
        template=Path(template),
        graph=g,
        resource=from_n3(resource),
        template_searchpath=template_searchpath,
    ).dump(output)
