from enum import StrEnum


class FolderTypes(StrEnum):
    """Типы папкок в чате."""

    GROUPS = 'g'
    DIRECTS = 'd'
    HIDDEN = 'h'
    ALL = 'a'
    CUSTOM = 'c'
    UNREAD = 'u'  # /pages/viewpage.action?pageId=130365575


class RoomTypes(StrEnum):
    """Типы комнат в чате."""

    DIRECT = 'd'
    PRIVATE = 'p'
    TELECONFERENCE = 'tc'
    SUPERGROUP = 's'
    TOPIC = 't'
    THREAD_ROOM = 'thread'
