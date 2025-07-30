# Copyright © 2021 Maxime “pep” Buquet <pep@bouah.net>
# Copyright © 2025 Tim “Syndace” Henkes <me@syndace.dev>
#
# Distributed under terms of the GPLv3 license.

import base64
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, FrozenSet, List, Optional, Tuple


import oldmemo
from omemo.storage import Just, Maybe, Nothing, Storage
from omemo.types import DeviceInformation, JSONType

from poezio import colors
from poezio.plugin_e2ee import ChatTabs, E2EEPlugin
from poezio.tabs import ChatTab, DynamicConversationTab, StaticConversationTab, MucTab
from poezio.theming import Theme, dump_tuple

try:
    from poezio.xdg import DATA_HOME
except ImportError:
    from poezio.libpoezio import XDG  # pylint: disable=import-error,no-name-in-module
    DATA_HOME = XDG.data_dir

from slixmpp import JID
from slixmpp.plugins import register_plugin  # type: ignore[attr-defined]
from slixmpp.stanza import Message
from slixmpp_omemo import XEP_0384


__all__ = [
    "encode_jid_for_path",
    "Plugin"
]


log = logging.getLogger(__name__)


def encode_jid_for_path(jid: JID) -> str:
    """
    Encode a JID in a way that makes it safe to use in filesystem paths.

    Args:
        jid: The JID to encode.

    Returns:
        A string uniquely representing the JID, safe for use in file names.
    """

    # Encode the bare JID to bytes using UTF-8
    bare_jid_bytes = jid.bare.encode("utf-8")

    # JIDs can be long. Using the hash of the JID ensures that its length does not violate file system length
    # restrictions.
    bare_jid_hash = hashlib.sha256(bare_jid_bytes).digest()

    # Encode the hash to urlsafe base64
    return base64.urlsafe_b64encode(bare_jid_hash).decode("ASCII")


class StorageImpl(Storage):
    """
    Storage implementation that stores all data in a single JSON file.
    """

    def __init__(self, path: Path) -> None:
        super().__init__()

        self.__path = path
        self.__data: Dict[str, JSONType] = {}
        try:
            with open(self.__path, encoding="utf8") as f:
                self.__data = json.load(f)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    async def _load(self, key: str) -> Maybe[JSONType]:
        if key in self.__data:
            return Just(self.__data[key])

        return Nothing()

    async def _store(self, key: str, value: JSONType) -> None:
        self.__data[key] = value
        with open(self.__path, "w", encoding="utf8") as f:
            json.dump(self.__data, f)

    async def _delete(self, key: str) -> None:
        self.__data.pop(key, None)
        with open(self.__path, "w", encoding="utf8") as f:
            json.dump(self.__data, f)


# TODO: This should probably be moved in plugins/base.py?
class PluginCouldNotLoad(Exception):
    pass


class Xep0384Impl(XEP_0384):
    """
    Implementation of the OMEMO plugin for Slixmpp for usage by Poezio.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Just the type definition here
        self.__storage: Storage

    def plugin_init(self) -> None:
        data_dir = os.path.join(DATA_HOME, "omemo")

        try:
            # Raise if the folder already exists so that we don't chmod again.
            os.makedirs(data_dir, mode=0o700, exist_ok=False)
        except OSError:  # Folder already exists
            pass

        self.__storage = StorageImpl(data_dir / Path(encode_jid_for_path(self.xmpp.boundjid) + ".json"))

        super().plugin_init()

    @property
    def storage(self) -> Storage:
        return self.__storage

    @property
    def _btbv_enabled(self) -> bool:
        return True

    async def _devices_blindly_trusted(
        self,
        blindly_trusted: FrozenSet[DeviceInformation],
        identifier: Optional[str]
    ) -> None:
        log.info(f"[{identifier}] Devices trusted blindly: {blindly_trusted}")  # TODO

    async def _prompt_manual_trust(
        self,
        manually_trusted: FrozenSet[DeviceInformation],
        identifier: Optional[str]
    ) -> None:
        # Since BTBV is enabled and we don't do any manual trust adjustments yet, this method should never be
        # called. All devices should be automatically trusted blindly by BTBV.
        raise NotImplementedError("Manual trust is not supported yet.")


register_plugin(Xep0384Impl)  # type: ignore[no-untyped-call]


# TODO: This plugin can/will be able to handle both versions of OMEMO, this might require changes to
# E2EEPlugin
class Plugin(E2EEPlugin):  # type: ignore[misc]
    """
    OMEMO plugin for version 0.3.0 of XEP-0384, under the `eu.siacs.conversations.axolotl` namespace.
    """

    encryption_name = "omemo"
    eme_ns = oldmemo.oldmemo.NAMESPACE
    replace_body_with_eme = True
    stanza_encryption = False

    encrypted_tags = [
        (oldmemo.oldmemo.NAMESPACE, "encrypted")
    ]

    supported_tab_types = (DynamicConversationTab, StaticConversationTab, MucTab)

    def init(self) -> None:
        super().init()

        try:
            self.core.xmpp.register_plugin(
                "xep_0384",
                {},
                module=sys.modules[__name__]
            )  # OMEMO
        except PluginCouldNotLoad:
            log.exception("And error occured when loading the omemo plugin.")

    def display_error(self, txt: str) -> None:
        """
        Helper to log an error in Poezio.

        Args:
            txt: The error message to log.
        """

        self.api.information(txt, "Error")

    async def get_fingerprints(self, jid: JID) -> List[Tuple[str, bool]]:
        # Note: The second entry of the returned tuples is a boolean indicating whether the fingerprint
        # belongs to this device.

        xep_0384: XEP_0384 = self.core.xmpp["xep_0384"]

        # Make sure the cached device list is up-to-date.
        await xep_0384.refresh_device_lists({ jid })

        fingerprints: List[Tuple[str, bool]] = []

        session_manager = await xep_0384.get_session_manager()

        other_devices_info: List[DeviceInformation]
        if jid.bare == self.core.xmpp.boundjid.bare:
            this_device_info, other_own_devices_info = await session_manager.get_own_device_information()

            fingerprints.append((
                "".join(session_manager.format_identity_key(this_device_info.identity_key)),
                True
            ))

            other_devices_info = list(other_own_devices_info)
        else:
            other_devices_info = list(await session_manager.get_device_information(jid.bare))

        for device_info in other_devices_info:
            fingerprints.append((
                "".join(session_manager.format_identity_key(device_info.identity_key)),
                False
            ))

        return fingerprints

    @staticmethod
    def format_fingerprint(fingerprint: str, own: bool, theme: Theme) -> str:
        """
        Color fingerprint as specified in in XEP-0384 0.8.3 "§8 Security Considerations".

        "When displaying the fingerprint as a hex-string, the RECOMMENDED way to make it easier to compare the
        fingerprint is to split the lowercase hex-string into 8 substrings of 8 chars each, then coloring each
        group of 8 lowercase hex chars using Consistent Color Generation (XEP-0392)"

        Args:
            fingerprint: The fingerprint to format.
            own: Whether this fingerprint belongs to this device.
            theme: The theme to use.

        Returns:
            The colored and formatted fingerprint.
        """

        size = len(fingerprint) // 8
        parts = map("".join, zip(*[iter(fingerprint)] * 8))
        colored_fp = ""

        for i, part in enumerate(parts):
            fg_color = colors.ccg_text_to_color(theme.ccg_palette, part)
            separator = " "
            if i == (size // 2 - 1):
                separator = "\n"
            elif i == size - 1:
                separator = ""
            colored_fp += f"\x19{fg_color}}}{part}{separator}"

        if own:
            normal_color = dump_tuple(theme.COLOR_NORMAL_TEXT)
            colored_fp += f"\x19{normal_color}}} (this device)"

        return colored_fp

    async def decrypt(self, message: Message, jid: Optional[JID], tab: Optional[ChatTab]) -> None:
        xep_0384: XEP_0384 = self.core.xmpp["xep_0384"]

        if not xep_0384.is_encrypted(message):
            self.display_error("Unable to decrypt the message: not encrypted.")
            return

        try:
            decrypted_message, _sender_device_info = await xep_0384.decrypt_message(message)
            message["body"] = decrypted_message["body"]
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.display_error(f"An error occured while decrypting: {e}")

    async def encrypt(self, message: Message, jids: Optional[List[JID]], tab: ChatTabs) -> None:
        xep_0384: XEP_0384 = self.core.xmpp["xep_0384"]

        if jids is None:
            self.display_error("Unable to encrypt the message: recipients not specified.")
            return

        try:
            encrypted_messages, errors = await xep_0384.encrypt_message(message, set(jids))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.display_error(f"A critical error occured while encrypting: {e}")
            return

        if len(errors) > 0:
            self.display_error(f"Non-critical errors occured while encrypting: {errors}")

        encrytped_tag = encrypted_messages[oldmemo.oldmemo.NAMESPACE].xml.find(
            f"{{{oldmemo.oldmemo.NAMESPACE}}}encrypted"
        )

        assert encrytped_tag is not None

        message.append(encrytped_tag)

        # Copy the new id over such that message reflection in MUCs can be handled correctly
        message["id"] = encrypted_messages[oldmemo.oldmemo.NAMESPACE]["id"]
