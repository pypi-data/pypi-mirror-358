from mkdocs.plugins import BasePlugin
from mkdocs.config import base, config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.utils.templates import TemplateContext
from jinja2 import Environment
from pathlib import PurePosixPath
from urllib.parse import urlsplit, urlunsplit
from rdflib import Graph, URIRef
from jinja_rdf import get_context, register_filters
from jinja_rdf.graph_handling import GraphToFilesystemHelper, TemplateSelectionHelper
from jinja_rdf.rdf_resource import RDFResource
from loguru import logger


def get_content(resource_iri, path):
    return f"""## {{{{ {path} | upper }}}}
iri: `{resource_iri}`
name: {path}
"""


class _MkRDFPluginConfig_Selection(base.Config):
    preset = c.Optional(c.Choice(("subject_relative", "subject_all", "none")))
    query = c.Optional(c.Type(str))
    queries = c.Optional(c.ListOfItems(c.Type(str)))
    list = c.Optional(c.ListOfItems(c.URL()))
    file = c.Optional(c.File(exists=True))
    files = c.Optional(c.ListOfItems(c.File(exists=True)))


class MkRDFPluginConfig(base.Config):
    graph_file = c.File(exists=True)
    base_iri = c.Optional(c.URL())
    selection = c.SubConfig(_MkRDFPluginConfig_Selection, validate=True)
    default_template = c.Optional(c.Type(str))
    class_template_map = c.DictOfItems(
        c.Type(str), default={}
    )  # keys are always strings, while we expect IRIs here
    instance_template_map = c.DictOfItems(
        c.Type(str), default={}
    )  # keys are always strings, while we expect IRIs here


class MkRDFPlugin(BasePlugin[MkRDFPluginConfig]):
    def on_files(self, files: Files, config: MkDocsConfig, **kwargs) -> Files | None:
        """For each resourceIri that results from the selection query, a File
        object is generated and registered."""

        g = Graph()
        g.parse(source=self.config.graph_file)
        self.graph = g

        gtfh = GraphToFilesystemHelper(self.config.base_iri)
        nodes = set(gtfh.selection_to_nodes(self.config.selection, g))

        for resource_iri, path, _ in gtfh.nodes_to_paths(nodes):
            logger.debug(f'Append file for iri: "{resource_iri}" at path: "{path}"')
            content = get_content(resource_iri, path)
            file = File.generated(config=config, src_uri=path + ".md", content=content)
            file.resource_iri = resource_iri
            files.append(file)
        return files

    def on_page_content(self, html, page, config, files):
        logger.debug(f"page meta: {page.meta}")
        if "title" not in page.meta:
            # insert some title
            pass

        # register resource IRIs
        if "resource_iri" in page.meta:
            page.meta["resource_iri"] = URIRef(page.meta["resource_iri"])
        elif hasattr(page.file, "resource_iri"):
            page.meta["resource_iri"] = page.file.resource_iri
        else:
            base_iri = urlsplit(self.config.base_iri)
            logger.debug(base_iri)
            page.meta["resource_iri"] = URIRef(
                urlunsplit(
                    (
                        base_iri.scheme,
                        base_iri.netloc,
                        str(PurePosixPath(base_iri.path) / page.url),
                        "",
                        "",
                    )
                )
            )
        logger.info(f"Registerd resource_iri: {page.meta['resource_iri']}")
        page.rdf_resource = RDFResource(
            self.graph, page.meta["resource_iri"], self.graph.namespace_manager
        )

        # select templates
        if "template" not in page.meta:
            template = TemplateSelectionHelper(
                self.graph,
                self.config.class_template_map,
                self.config.instance_template_map,
            ).get_template_for_resource(page.rdf_resource)
            if template:
                logger.debug(f"Select template: {template} for {page.rdf_resource}")
                page.meta["template"] = template

    def on_env(
        self, env: Environment, config: MkDocsConfig, files: Files, **kwargs
    ) -> Environment | None:
        """Register the jinja filters"""
        register_filters(env)
        return env

    def on_page_context(
        self,
        context: TemplateContext,
        page: Page,
        config: MkDocsConfig,
        nav: Navigation,
    ) -> TemplateContext:
        """Set the relevant variables for each page."""
        return {**get_context(self.graph, page.rdf_resource), **context}
