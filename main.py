"""
Ulauncher Extension to search folders using Tracker 3
"""

import logging
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from pathlib import Path
import urllib.parse
from tracker import tracker

logger = logging.getLogger(__name__)


class FolderSearchExtension(Extension):
    """ Main Extension Class """
    def __init__(self):
        """ Initializes the extension """
        super(FolderSearchExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def search(self, query):
        """ Searches folders that match the specified query """
        if not query or len(query) < 3:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='Folder search',
                                    description='Keep typing to search ...',
                                    on_enter=HideWindowAction())
            ])

        try:
            folders = tracker.search(query)
        except Exception as error:
            logging.error(error)
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='An error occurred',
                                    description=str(error),
                                    highlightable=False,
                                    on_enter=HideWindowAction())
            ])

        if len(folders) == 0:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='No folders found matching your criteria',
                    description=
                    'If you were expecting results,please check your Tracker index settings',
                    highlightable=False,
                    on_enter=HideWindowAction())
            ])

        items = []
        home = str(Path.home())
        for folder in folders[:15]:
            name = folder.replace(home, '~').replace('&', 'And')
            name = urllib.parse.unquote_plus(name)
            path = urllib.parse.unquote_plus(folder)
            items.append(
                ExtensionSmallResultItem(icon='images/icon.png',
                                         name=name,
                                         on_enter=ExtensionCustomAction(
                                             {
                                                 'action': 'detail',
                                                 'path': path
                                             },
                                             keep_app_open=True)))

        return RenderResultListAction(items)

    def show_detail(self, path):
        """ Shows the folder detail menu, where the user can select an action to do it with that folder """
        return RenderResultListAction([
            ExtensionSmallResultItem(
                icon='images/icon.png',
                name=path,
                on_enter=DoNothingAction(),
                highlightable=False,
            ),
            ExtensionSmallResultItem(
                icon='images/folder.png',
                name='Open in File Manager',
                on_enter=OpenAction(path),
                highlightable=False,
            ),
            ExtensionSmallResultItem(
                icon='images/terminal.png',
                name='Open in Terminal',
                on_enter=ExtensionCustomAction({
                    'action': 'open-in-terminal',
                    'path': path
                }),
                highlightable=False,
            ),
            ExtensionSmallResultItem(
                icon='images/vscode-icon.png',
                name='Open in VS Code',
                on_enter=ExtensionCustomAction({
                    'action': 'open-in-code',
                    'path': path
                }),
                highlightable=False,
            ),
            ExtensionSmallResultItem(
                icon='images/copy-clipboard.png',
                name='Copy Path to clipboard',
                on_enter=CopyToClipboardAction(path),
                highlightable=False,
            )
        ])

    def open_in_terminal(self, path):
        """ Opens the specified folder path in the configured terminal """
        default_terminal = self.preferences['default_terminal']

        if default_terminal == 'gnome':
            subprocess.run(["gnome-terminal", "--working-directory", path])

        if default_terminal == 'tilix':
            subprocess.run(["tilix", "-w", path])

    def open_in_code(self, path):
        """ Opens the specified folder path in VS Code"""
        subprocess.run(["code", path])


class KeywordQueryEventListener(EventListener):
    """ Listener that handles the user input """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event, extension):
        """ Handles the event """
        return extension.search(event.get_argument())


class ItemEnterEventListener(EventListener):
    """ Listener that handles the click on an item """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event, extension):
        """ Handles the event """
        data = event.get_data()

        folder_path = data['path']
        action = data['action']

        if action == 'detail':
            return extension.show_detail(folder_path)

        if action == 'open-in-terminal':
            return extension.open_in_terminal(folder_path)

        if action == 'open-in-code':
            return extension.open_in_code(folder_path)


if __name__ == '__main__':
    FolderSearchExtension().run()
