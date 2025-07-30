from __future__ import annotations

import json
import logging
import time
import urllib.parse
from pathlib import Path
from typing import Any, TypedDict, cast

import libcst as cst
from libcst.metadata import MetadataWrapper
from lsprotocol import types as lst
from pygls.lsp.server import LanguageServer
from pygls.uris import to_fs_path

import logfire_lsp
from logfire_lsp.models import CallType, LevelName
from logfire_lsp.visitor import LogfireVisitor


class LogfireLanguageServer(LanguageServer):
    """The Logfire language server."""

    workspace_path: Path
    """The path of the workspace."""

    project_url: str
    """The URL of the Logfire project.

    Example:
        `https://logfire-eu.pydantic.dev/my_org/my_project`
    """

    environment: str | None
    """The environment to use when creating Logfire URLs."""

    def log_to_output(self, message: str) -> None:
        self.window_log_message(lst.LogMessageParams(lst.MessageType.Log, message))

    def show_error(self, message: str) -> None:
        self.window_log_message(lst.LogMessageParams(lst.MessageType.Error, message))
        self.window_show_message(lst.ShowMessageParams(lst.MessageType.Error, message))


logfire_server = LogfireLanguageServer(
    name='Logfire',
    version=logfire_lsp.__version__,
)
"""The Logfire language server instance."""


# CodeLens server feature:


class CodeLensData(TypedDict):
    call_type: CallType
    span_name: str
    level_name: LevelName | None


@logfire_server.feature(lst.TEXT_DOCUMENT_CODE_LENS)
def code_lens(ls: LogfireLanguageServer, params: lst.CodeLensParams) -> list[lst.CodeLens] | None:
    """Return a list of CodeLens elements to be inserted on `logfire` calls."""

    document = ls.workspace.get_text_document(params.text_document.uri)
    try:
        parsed = cst.parse_module(document.source)
    except cst.ParserSyntaxError:
        logging.debug('Failed to parse document %s', params.text_document.uri)
        return

    wrapper = MetadataWrapper(module=parsed)
    logfire_visitor = LogfireVisitor()
    wrapper.visit(logfire_visitor)

    return [
        lst.CodeLens(
            range=call.code_range,
            data={
                'call_type': call.call_type,
                'span_name': call.span_name,
                'level_name': call.level_name,
            },
        )
        for call in logfire_visitor.calls
    ]


@logfire_server.feature(lst.CODE_LENS_RESOLVE)
def code_lens_resolve(ls: LogfireLanguageServer, item: lst.CodeLens) -> lst.CodeLens:
    """Resolve the command to be executed by the client for the resolved CodeLens."""

    logging.info('Resolving code lens: %s', item)

    data = cast(CodeLensData, item.data)

    item.command = lst.Command(
        title=f'view this {data["call_type"]} in Logfire',
        command='codeLens.openLogfireLink',
        arguments=[item.data],
    )
    return item


@logfire_server.command('codeLens.openLogfireLink')
def open_logfire_link(ls: LogfireLanguageServer, args: CodeLensData) -> None:
    """Open the Logfire link corresponding to the CodeLens."""

    logging.info("'codeLens.openLogfireLink' arguments: %s", args)

    sql_query = f'span_name={args["span_name"]!r}'
    if args['call_type'] == 'log':
        sql_query += f'AND level={args["level_name"]!r}'
    sql_query = urllib.parse.quote(sql_query)

    link = f'{ls.project_url}?q={sql_query}'

    if ls.environment is not None:
        link += f'&env={ls.environment}'

    # Add a small delay to deal with VSCode issue https://github.com/microsoft/vscode/issues/251935:
    time.sleep(0.25)

    ls.window_show_document(
        lst.ShowDocumentParams(
            uri=link,
            external=True,
        )
    )


# Initialization:


def _supports_code_lens(capabilities: lst.ClientCapabilities) -> bool:
    return capabilities.text_document is not None and capabilities.text_document.code_lens is not None


@logfire_server.feature(lst.INITIALIZE)
def initialize(ls: LogfireLanguageServer, params: lst.InitializeParams) -> None:
    """Initialize the language server."""

    if not _supports_code_lens(params.capabilities):
        ls.show_error('The CodeLens feature is required to use the Logfire language server.')
        return

    if params.workspace_folders is None:
        ls.show_error('Workspace folders are required to use the Logfire language server.')
        return

    fs_path = to_fs_path(params.workspace_folders[0].uri)
    if fs_path is None:
        ls.show_error(f'Unsupported scheme for workspace URI {params.workspace_folders[0].uri}')
        return

    ls.workspace_path = Path(fs_path)
    logfire_credentials_path = ls.workspace_path.joinpath('.logfire', 'logfire_credentials.json')

    if not logfire_credentials_path.is_file():
        ls.show_error("No credentials found at '.logfire/logfire_credentials.json'. Run 'logfire projects use' first.")
        return

    with logfire_credentials_path.open('rb') as fp:
        try:
            logfire_credentials = json.load(fp)
            if not isinstance(logfire_credentials, dict):
                raise ValueError('Not a dict')
        except (ValueError, UnicodeDecodeError):
            ls.show_error("Failed to parse credentials at '.logfire/logfire_credentials.json'.")
            return

    project_url = logfire_credentials.get('project_url')
    if not (project_url and isinstance(project_url, str)):
        ls.show_error("No 'project_url' set in credentials at '.logfire/logfire_credentials.json'.")
        return

    init_options = params.initialization_options or {}
    global_settings = init_options.get('globalSettings')
    settings = init_options.get('settings')

    _unset: Any = object()

    environment: str = _unset
    if settings:
        if isinstance(settings, list):
            environment = settings[0].get('environment', _unset)
        elif isinstance(settings, dict):
            environment = settings.get('environment', _unset)

    if environment is _unset and global_settings:
        environment = global_settings.get('environment', _unset)

    ls.project_url = project_url
    ls.environment = environment if environment is not _unset else None


def start() -> None:
    """Start the server."""

    logfire_server.start_io()
