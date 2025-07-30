# pylint: disable=missing-docstring,unused-argument
from pathlib import Path
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from gbp_webhook_tts import utils

EVENT = {"name": "build_pulled", "machine": "babette", "data": {}}


@given("tmpdir")
@mock.patch.object(utils, "event_to_speech")
@mock.patch.object(utils.platformdirs, "user_cache_path")
class AcquireSoundFileTests(TestCase):
    def test(
        self, user_cache_path: mock.Mock, event_to_speech: mock.Mock, fixtures: Fixtures
    ) -> None:
        tmpdir = fixtures.tmpdir
        user_cache_path.return_value = tmpdir
        event_to_speech.return_value = b"test"
        path = utils.acquire_sound_file(EVENT)

        self.assertEqual(tmpdir / "tts" / "babette.mp3", path)
        self.assertTrue(path.parent.is_dir())
        self.assertEqual(path.read_bytes(), b"test")

    def test_makes_path(
        self, user_cache_path: mock.Mock, event_to_speech: mock.Mock, fixtures: Fixtures
    ) -> None:
        tmpdir = fixtures.tmpdir
        user_cache_path.return_value = tmpdir / "foo"
        event_to_speech.return_value = b"test"
        path = utils.acquire_sound_file(EVENT)

        self.assertEqual(tmpdir / "foo" / "tts" / "babette.mp3", path)
        self.assertTrue(path.parent.is_dir())
        self.assertEqual(path.read_bytes(), b"test")


@mock.patch.object(utils.platformdirs, "user_cache_path")
class EventToPathTests(TestCase):

    def test(self, user_cache_path: mock.Mock) -> None:
        user_cache_path.return_value = Path("/dev/null")
        path = utils.event_to_path(EVENT)

        self.assertEqual(Path("/dev/null/tts/babette.mp3"), path)


@mock.patch.object(utils.boto3, "Session")
class EventToSpeechTests(TestCase):

    def test(self, session_cls: mock.Mock) -> None:
        text = utils.get_speech_text_for_machine("babette")
        audio = utils.event_to_speech(EVENT)

        session = session_cls.return_value
        session.client.assert_called_once_with("polly")
        polly = session.client.return_value
        polly.synthesize_speech.assert_called_once_with(
            VoiceId="Ivy", OutputFormat="mp3", Text=text, TextType="ssml"
        )
        speech = polly.synthesize_speech.return_value
        self.assertEqual(speech["AudioStream"].read.return_value, audio)


@given("environ")
class GetSpeechTextForMachineTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        environ = fixtures.environ
        environ["GBP_WEBHOOK_TTS_PHONETIC_KDE_DESKTOP"] = "foobar"

        self.assertEqual(
            ssml("foobar", 0), utils.get_speech_text_for_machine("kde-desktop")
        )

    def test_default(self, fixtures: Fixtures) -> None:
        self.assertEqual(
            ssml("kde desktop", 0), utils.get_speech_text_for_machine("kde-desktop")
        )

    def test_with_delay(self, fixtures: Fixtures) -> None:
        environ = fixtures.environ
        environ["GBP_WEBHOOK_TTS_DELAY"] = "0.8"

        self.assertEqual(
            ssml("kde desktop", 0.8), utils.get_speech_text_for_machine("kde-desktop")
        )


@given("environ")
class MapMachineToTextTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        environ = fixtures.environ
        environ["GBP_WEBHOOK_TTS_PHONETIC_KDE_DESKTOP"] = "foobar"

        self.assertEqual("foobar", utils.map_machine_to_text("kde-desktop"))

    def test_default(self, fixtures: Fixtures) -> None:
        self.assertEqual(None, utils.map_machine_to_text("kde-desktop"))


@given("environ")
class GetSoundFileTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        environ = fixtures.environ
        environ["GBP_WEBHOOK_PLAYSOUND_PLAYER"] = "blahblahblah blah"

        self.assertEqual(["blahblahblah", "blah"], utils.get_sound_player())

    def test_default(self, fixtures: Fixtures) -> None:
        self.assertEqual(["pw-play"], utils.get_sound_player())


def ssml(text: str, delay: float) -> str:
    return f"""\
<speak>
  <break time="{delay}s"/>
  {text}
</speak>"""
