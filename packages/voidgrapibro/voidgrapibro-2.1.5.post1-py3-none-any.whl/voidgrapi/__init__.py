import logging
from urllib.parse import urlparse

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from voidgrapi.mixins.account import AccountMixin
from voidgrapi.mixins.album import DownloadAlbumMixin, UploadAlbumMixin
from voidgrapi.mixins.auth import LoginMixin
from voidgrapi.mixins.bloks import BloksMixin
from voidgrapi.mixins.challenge import ChallengeResolveMixin
from voidgrapi.mixins.clip import DownloadClipMixin, UploadClipMixin
from voidgrapi.mixins.collection import CollectionMixin
from voidgrapi.mixins.comment import CommentMixin
from voidgrapi.mixins.direct import DirectMixin
from voidgrapi.mixins.explore import ExploreMixin
from voidgrapi.mixins.fbsearch import FbSearchMixin
from voidgrapi.mixins.fundraiser import FundraiserMixin
from voidgrapi.mixins.hashtag import HashtagMixin
from voidgrapi.mixins.highlight import HighlightMixin
from voidgrapi.mixins.igtv import DownloadIGTVMixin, UploadIGTVMixin
from voidgrapi.mixins.insights import InsightsMixin
from voidgrapi.mixins.location import LocationMixin
from voidgrapi.mixins.media import MediaMixin
from voidgrapi.mixins.multiple_accounts import MultipleAccountsMixin
from voidgrapi.mixins.note import NoteMixin
from voidgrapi.mixins.notification import NotificationMixin
from voidgrapi.mixins.password import PasswordMixin
from voidgrapi.mixins.photo import DownloadPhotoMixin, UploadPhotoMixin
from voidgrapi.mixins.private import PrivateRequestMixin
from voidgrapi.mixins.public import (
    ProfilePublicMixin,
    PublicRequestMixin,
    TopSearchesPublicMixin,
)
from voidgrapi.mixins.share import ShareMixin
from voidgrapi.mixins.signup import SignUpMixin
from voidgrapi.mixins.story import StoryMixin
from voidgrapi.mixins.timeline import ReelsMixin
from voidgrapi.mixins.totp import TOTPMixin
from voidgrapi.mixins.track import TrackMixin
from voidgrapi.mixins.user import UserMixin
from voidgrapi.mixins.video import DownloadVideoMixin, UploadVideoMixin

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Used as fallback logger if another is not provided.
DEFAULT_LOGGER = logging.getLogger("voidgrapi")


class Client(
    PublicRequestMixin,
    ChallengeResolveMixin,
    PrivateRequestMixin,
    TopSearchesPublicMixin,
    ProfilePublicMixin,
    LoginMixin,
    ShareMixin,
    TrackMixin,
    FbSearchMixin,
    HighlightMixin,
    DownloadPhotoMixin,
    UploadPhotoMixin,
    DownloadVideoMixin,
    UploadVideoMixin,
    DownloadAlbumMixin,
    NotificationMixin,
    UploadAlbumMixin,
    DownloadIGTVMixin,
    UploadIGTVMixin,
    MediaMixin,
    UserMixin,
    InsightsMixin,
    CollectionMixin,
    AccountMixin,
    DirectMixin,
    LocationMixin,
    HashtagMixin,
    CommentMixin,
    StoryMixin,
    PasswordMixin,
    SignUpMixin,
    DownloadClipMixin,
    UploadClipMixin,
    ReelsMixin,
    ExploreMixin,
    BloksMixin,
    TOTPMixin,
    MultipleAccountsMixin,
    NoteMixin,
    FundraiserMixin,
):
    proxy = None

    def __init__(
        self,
        settings: dict = {},
        proxy: str | None = None,
        delay_range: list | None = None,
        logger=DEFAULT_LOGGER,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.settings = settings
        self.logger = logger
        self.delay_range = delay_range

        self.set_proxy(proxy)

        self.init()

    def set_proxy(self, dsn: str | None):
        if dsn:
            assert isinstance(
                dsn, str
            ), f'Proxy must been string (URL), but now "{dsn}" ({type(dsn)})'
            self.proxy = dsn
            proxy_href = "{scheme}{href}".format(
                scheme="http://" if not urlparse(self.proxy).scheme else "",
                href=self.proxy,
            )
            self.public.proxies = self.private.proxies = {
                "http": proxy_href,
                "https": proxy_href,
            }
            return True
        self.public.proxies = self.private.proxies = {}
        return False
