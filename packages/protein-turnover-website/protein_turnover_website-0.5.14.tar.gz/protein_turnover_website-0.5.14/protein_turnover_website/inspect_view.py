from __future__ import annotations

import sys
from dataclasses import asdict
from io import BytesIO
from typing import cast
from typing import NamedTuple
from typing import NoReturn

from flask import abort as fabort
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import Response
from flask import send_file
from flask import url_for
from protein_turnover.jobs import TurnoverJob
from protein_turnover.sqla.query import calc_stats
from protein_turnover.sqla.query import Stats

from .inspect import Column
from .inspect import encode_img
from .inspect import get_columns
from .jobs import get_jobs_manager
from .sqla.export import make_export_table
from .sqla.inspect import get_engine
from .sqla.inspect import make_enrichment_plot
from .sqla.inspect import make_nnls_plot
from .sqla.inspect import make_peptide_table
from .sqla.inspect import make_plot_table
from .sqla.inspect import make_protein_table


# mypy is broken ATM
def abort(num: int) -> NoReturn:
    fabort(num)
    raise RuntimeError()


class Group(NamedTuple):
    dataid: str
    group: int


def get_group_from_request(dataid: str | None = None) -> Group:
    groupid = request.values.get("group")
    if groupid is None:
        abort(404)
    if dataid is None:
        dataid = request.values.get("dataid")
        if dataid is None:
            abort(404)

    try:
        igroup = int(groupid)
        return Group(dataid, igroup)
    except ValueError:
        abort(404)


def init_length() -> int:
    if "length" in request.values:
        try:
            return int(request.values["length"])
        except ValueError:
            pass
    return current_app.config["PROTEIN_PAGE_LENGTH"]


def mk_plot_all(
    dataid: str,
    rowid: int,
    *,
    fmt: str = "png",
    enrichmentColumns: int = 0,
) -> BytesIO:
    if rowid < 0:
        abort(404)
    layout = current_app.config["FIG_LAYOUT"]
    figsize = current_app.config["FIG_SIZE"]
    r, c = layout
    figsize = figsize[0] * c, figsize[1] * r

    mp = make_plot_table(dataid)
    pdata = mp.plot_all(
        rowid,
        figsize=figsize,
        image_format=fmt,
        layout=layout,
        enrichmentColumns=enrichmentColumns,
    )
    if pdata is None:
        abort(404)
        assert pdata is not None
    plotio, _ = pdata
    return plotio


def get_rowid() -> int:
    s = request.args.get("rowid")
    if s is None:
        abort(404)
    try:
        return int(s)
    except ValueError:
        abort(404)
    raise ValueError()


def get_enrichmentColumns() -> int:
    s = request.args.get("enrichment_cols")
    if s is None:
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


inspect = Blueprint("inspect", __name__)


@inspect.route("/inspect/<path:dataid>")
def data(dataid: str) -> str | tuple[str, int]:
    from protein_turnover.sqla.model import MINRSQ100

    # from protein_turnover.sqla.query import sqlite_version
    from protein_turnover.sqla.iso_peaks import fixsqlite

    # entrypoint for dataview page
    filtered = request.values.get("filter", "true") in {"true", "yes", "1"}
    try:
        locator = get_jobs_manager().locate_from_url(dataid)
        config = locator.locate_config_file()
        if not config.exists():
            return (
                render_template("bad-file.html", dataid=dataid, error="no such data"),
                404,
            )
        sqldata = locator.locate_data_file()
        if not sqldata.exists():
            return (
                render_template("bad-file.html", dataid=dataid, error="no such data"),
                404,
            )

        # eventually we can remove this....
        # Add iso_peaks_nr_<n> columns if they
        # don't exist.
        if current_app.config.get("FIXSQLITE", False):
            fixsqlite(sqldata, force=False)

        job = TurnoverJob.restore(config)

        # statsd = calc_stats(get_engine(dataid), round=True)
        # placeholder values see stats below
        statsd = Stats(
            max_nnls_residual=current_app.config.get("MAX_NNLS_RESIDUAL", 0.2),
        )
        return render_template(
            "inspect.html",
            dataid=dataid,
            job=job,
            length=init_length(),
            filtered=filtered,
            stat=sqldata.stat(),
            stats=statsd,
            split_width=40,
            minrsq=MINRSQ100,
            # sqlite_version=sqlite_version(get_engine(dataid))
        )
    except Exception as e:
        current_app.log_exception(sys.exc_info())
        return render_template("bad-file.html", dataid=dataid, error=str(e)), 404


@inspect.route("/stats/<path:dataid>")
def stats(dataid: str) -> Response:
    # get stats for this data source
    statsd = calc_stats(get_engine(dataid), round=True)
    return jsonify(asdict(statsd))


@inspect.route("/datatable/<path:dataid>")
def datatable(dataid: str) -> Response:
    # request by javascript to load protein table (meta) data
    return jsonify(make_protein_table(dataid).dt_config(init_length()))


@inspect.route("/ajax/<path:dataid>", methods=["POST"])
def ajax(dataid: str) -> Response:
    # request by javascript to update protein table data
    q = make_protein_table(dataid).query()
    if q is None:
        abort(404)  # datatables will show an alert box :(
    return jsonify(q)


@inspect.route("/group/<path:dataid>", methods=["POST", "GET"])
def group(dataid: str) -> Response:
    # fetch peptide table data for group
    # .. user has clicked on a protein table row.
    grp = get_group_from_request(dataid)
    res = make_peptide_table(grp.dataid, grp.group, with_data=True).dt_config()
    return jsonify(res)


@inspect.route("/plot/<path:dataid>")
def plot(dataid: str) -> Response:

    plotio = mk_plot_all(
        dataid,
        get_rowid(),
        fmt="png",
        enrichmentColumns=get_enrichmentColumns(),
    )
    return send_file(plotio, mimetype="image/png")


@inspect.route("/plot_url/<path:dataid>")
def plot_url(dataid: str) -> Response:
    """Send plot as data: url"""

    plotio = mk_plot_all(
        dataid,
        get_rowid(),
        fmt="png",
        enrichmentColumns=get_enrichmentColumns(),
    )
    url = encode_img(plotio, image_format="png")
    return jsonify({"image_url": url})


@inspect.route("/enrichment_plot/<path:dataid>", methods=["POST", "GET"])
def enrichment_plot(dataid: str) -> Response:
    p = make_enrichment_plot(dataid, column="enrichment")
    if p is None:
        abort(404)
    return jsonify({"enrichment_url": p})


@inspect.route("/nnls_plot/<path:dataid>", methods=["POST", "GET"])
def nnls_plot(dataid: str) -> Response:
    p = make_nnls_plot(dataid, percent=0.01)
    if p is None:
        abort(404)
    return jsonify({"nnls_url": p})


@inspect.route("/pdf/<path:dataid>")
def pdf(dataid: str) -> Response:
    rowid = get_rowid()
    if rowid < 0:
        abort(404)

    return make_plot_table(dataid).send_pdf(
        rowid,
        enrichmentColumns=get_enrichmentColumns(),
    )


@inspect.route("/about.html")
def about() -> str:
    return render_template("about.html")


@inspect.route("/download/<path:dataid>", methods=["POST", "GET"])
def download(dataid: str) -> Response:
    fmt = request.values.get("format", "xlsx")
    if fmt not in {"all", "tsv", "xlsx"}:
        abort(404)

    export = make_export_table(dataid)
    if fmt == "all":
        return export.send_all()
    return export.send(fmt=fmt)


def init_view(app: Flask, dataid: str, url_prefix: str = "/") -> None:
    from .jobs import view_jobsdir

    @inspect.route("/")
    def index() -> Response:
        return cast(Response, redirect(url_for("inspect.data", dataid=dataid)))

    view_jobsdir(app)
    init_app(app, url_prefix)


def init_app(app: Flask, url_prefix: str = "/") -> None:
    with app.app_context():
        pcolumns = get_columns("peptides.toml")
        if pcolumns is not None:
            pcolumns = [Column("peptideid", view=False)] + pcolumns
        app.config["PEPTIDE_COLUMNS"] = pcolumns

        pcolumns = get_columns("proteins.toml")
        if pcolumns is not None:
            pcolumns = [Column("proteinid", view=False, search=False)] + pcolumns
        app.config["PROTEIN_COLUMNS"] = pcolumns

        pcolumns = get_columns("export.toml")
        app.config["EXPORT_COLUMNS"] = pcolumns

    app.register_blueprint(inspect, url_prefix=url_prefix)
