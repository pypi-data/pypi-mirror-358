from importlib.resources import as_file, files
from textwrap import dedent
from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx


class VizJs(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    def get_mm_code(self) -> str:
        mmcode = "\n".join(self.content)
        return mmcode

    def run(self) -> Any:
        mmcode = self.get_mm_code()
        # mmcode is a list, so it's a system message, not content to be included in the
        # document.
        if not isinstance(mmcode, str):
            return mmcode

        # if mmcode is empty, ignore the directive.
        if not mmcode.strip():
            return [
                self.state_machine.reporter.warning(
                    'Ignoring "vizjs" directive without content.',
                    line=self.lineno,
                )
            ]

        # Wrap the graphviz code into a code node.
        node = vizjs()
        node["code"] = mmcode
        node["options"] = {}
        return [node]


class vizjs(nodes.General, nodes.Inline, nodes.Element):
    pass


def html_visit_vizjs(self: Any, node: dict[str, Any]) -> None:
    render_vizjs_html(self, node["code"])


def render_vizjs_html(self: Any, code: str) -> None:
    tag_template = dedent(
        f"""\
        <div class="vizjs">
            {code}
        </div>
        """
    )

    self.body.append(tag_template)
    raise nodes.SkipNode


def setup(app: Sphinx) -> None:
    viz_standalone = files(__package__).joinpath("viz-standalone.js").read_text()
    app.add_js_file(None, body=viz_standalone)
    app.add_js_file(
        None,
        body=dedent(
            """
            document.addEventListener("DOMContentLoaded", function() {
                Viz.instance().then(function(viz) {
                    var elems = document.getElementsByClassName("vizjs");
                    console.log("vizjs: processing", elems.length, "items");
                    for (let index = elems.length - 1; index >= 0; index--) {
                        let elem = elems[index];
                        console.log("vizjs: processing", elem);
                        var svg = viz.renderSVGElement(elem.textContent);
                        var graph = document.createElement('div');
                        graph.appendChild(svg);
                        elem.replaceWith(graph);
                    }
                });
            });
            """
        ),
    )
    app.add_node(
        vizjs,
        html=(html_visit_vizjs, None),
    )
    app.add_directive("vizjs", VizJs)
