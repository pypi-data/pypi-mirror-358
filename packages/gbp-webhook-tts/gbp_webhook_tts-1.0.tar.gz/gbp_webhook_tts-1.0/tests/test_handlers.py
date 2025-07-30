# pylint: disable=missing-docstring
from unittest import TestCase, mock

from gbp_webhook_tts import handlers, utils


@mock.patch.object(handlers.utils, "acquire_sound_file")
@mock.patch.object(handlers.sp, "Popen")
class BuildPulledTests(TestCase):
    def test(self, popen_cls: mock.Mock, acquire_sound_file: mock.Mock) -> None:
        event = {"name": "build_pulled", "machine": "babette", "data": {}}
        handlers.build_pulled(event)
        player = utils.get_sound_player()
        sound_file = acquire_sound_file.return_value

        acquire_sound_file.assert_called_once_with(event)
        popen_cls.assert_called_once_with([*player, str(sound_file)])
