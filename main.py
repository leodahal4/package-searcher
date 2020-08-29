from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
import requests
import subprocess
import os
import logging

#Proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}


class Extension(Extension):

    def __init__(self):
        super(Extension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        logger = logging.getLogger(__name__)
        query = event.get_argument() or str()
        if len(query.strip()) == 0:
            return RenderResultListAction([
                ExtensionResultItem(icon='icon.png',
                                    name='No input',
                                    on_enter=HideWindowAction())
            ])
        else:
            try:
                data = subprocess.Popen(["aurman", "-Ss", str(query)], stdout = subprocess.PIPE)
                logger.info("aurman package found")
            except FileNotFoundError:
                pass
            try:
                data = subprocess.Popen(["yay", "-Ss", str(query)], stdout = subprocess.PIPE)
                logger.info("yay package found")
            except FileNotFoundError:
                pass
            try:
                data = subprocess.Popen(["apt", "search", str(query)], stdout = subprocess.PIPE)
                logger.info("apt package found")
            except FileNotFoundError:
                pass
            cmd = str(data.communicate())

            packages = [] # List of packages
            packages_number = 0 # Number of packages
            i = 3 # Character index
            while i < len(cmd):
                packages.append([])
                repo = ""
                name = ""
                description = ""
                while i < len(cmd) and cmd[i] != '/':
                    repo += cmd[i]
                    i += 1
                i += 1
                while i < len(cmd) and cmd[i] != ' ':
                    name += cmd[i]
                    i += 1
                while i < len(cmd) and cmd[i] != '\\':
                    i += 1
                i += 6
                while i < len(cmd) and cmd[i] != '\\':
                    description += cmd[i]
                    i += 1
                packages[packages_number].append(name)
                packages[packages_number].append(description)
                packages[packages_number].append(repo)
                packages_number += 1
                i += 2

            del packages[len(packages) - 1]

            items = []
            logger.info(packages)
            for q in packages:
                if q[2] == "aur":
                    items.append(ExtensionResultItem(icon='icon.png',
                                                     name=q[0] + "  (" + q[2] + ")",
                                                     description=q[1],
                                                     on_enter=CopyToClipboardAction("aurman -S " + q[0])))
                else:
                    items.append(ExtensionResultItem(icon='icon.png',
                                                     name=q[0] + "  (" + q[2] + ")",
                                                     description=q[1],
                                                     on_enter=CopyToClipboardAction("sudo pacman -S " + q[0])))

            return RenderResultListAction(items)


if __name__ == '__main__':
    Extension().run()
