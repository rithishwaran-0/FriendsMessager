# -*- coding: UTF-8 -*-
"""Sound effects for Friends Mirror, played through NVDA's audio output."""
import json
import os
import globalVars
import addonHandler

addonHandler.initTranslation()

SOUND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sounds"))
CONFIG_FILE = os.path.join(globalVars.appArgs.configPath, "friendsMirrorSounds.json")
# Put your own enter.wav, exit.wav, move.wav (or any other sound name below) in this folder and they replace the built-in ones.
USER_DIR = os.path.join(globalVars.appArgs.configPath, "friendsMirrorSounds")


# Notification tones to choose from in NVDA settings, Friends Mirror (label, file name).
TONES = [
	(_("Galaxy bell"), "t01"),
	(_("Over the horizon"), "t02"),
	(_("Crystal glass"), "t03"),
	(_("Water drop"), "t04"),
	(_("Soft chime"), "t05"),
	(_("Xylophone run"), "t06"),
	(_("Kalimba pop"), "t07"),
	(_("Harp sparkle"), "t08"),
	(_("Flute whistle"), "t09"),
	(_("Ding dong"), "t10"),
	(_("Bubble pop"), "t11"),
	(_("Rising stars"), "t12"),
	(_("Gentle piano"), "t13"),
	(_("Morning dew"), "t14"),
	(_("Triple tap"), "t15"),
	(_("Sunrise"), "t16"),
	(_("Coin sparkle"), "t17"),
	(_("Silver bells"), "t18"),
	(_("Soft pulse"), "t19"),
	(_("Cheerful ping"), "t20"),
	(_("Bird song"), "t21"),
	(_("Music box"), "t22"),
	(_("Steel drum"), "t23"),
	(_("Bicycle bell"), "t24"),
	(_("Old telephone"), "t25"),
	(_("Sonar ping"), "t26"),
	(_("Message pop"), "t27"),
	(_("Fanfare"), "t28"),
	(_("Guitar strum"), "t29"),
	(_("Cash register"), "t30"),
	(_("Tri tone"), "t31"),
	(_("Door bell"), "t32"),
	(_("Wind chimes"), "t33"),
	(_("Cuckoo"), "t34"),
	(_("Nokia style"), "t35"),
	(_("Bright ding"), "t36"),
	(_("Laser blip"), "t37"),
	(_("Ship bell"), "t38"),
	(_("Dreamy harp"), "t39"),
	(_("Happy whistle"), "t40"),
]
TONE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sounds", "tones"))
DEFAULT_TONE = "t05"

_state = {"enabled": None, "tone": None}


def is_enabled():
	if _state["enabled"] is None:
		try:
			with open(CONFIG_FILE, "r", encoding="utf-8") as f:
				_state["enabled"] = bool(json.load(f).get("enabled", True))
		except Exception:
			_state["enabled"] = True
	return _state["enabled"]


def set_enabled(value):
	_state["enabled"] = bool(value)
	try:
		d = _cfg()
		d["enabled"] = _state["enabled"]
		with open(CONFIG_FILE, "w", encoding="utf-8") as f:
			json.dump(d, f)
	except Exception:
		pass


def _find(name):
	"""Your own file in the NVDA configuration folder wins over the one inside the add-on."""
	for folder in (USER_DIR, SOUND_DIR):
		path = os.path.join(folder, name + ".wav")
		if os.path.isfile(path):
			return path
	return None


def play(name, force=False):
	"""Play a sound effect without blocking. Never raises."""
	if not force and not is_enabled():
		return
	try:
		import nvwave
		path = _find(name)
		if path:
			nvwave.playWaveFile(path, asynchronous=True)
	except Exception:
		pass


def play_file(path):
	"""Play any WAV file without blocking ."""
	try:
		import nvwave
		if os.path.isfile(path):
			nvwave.playWaveFile(path, asynchronous=True)
	except Exception:
		pass


def _cfg():
	try:
		with open(CONFIG_FILE, "r", encoding="utf-8") as f:
			return json.load(f)
	except Exception:
		return {}


def get_tone():
	if _state["tone"] is None:
		t = _cfg().get("tone", DEFAULT_TONE)
		_state["tone"] = t if t in [x[1] for x in TONES] else DEFAULT_TONE
	return _state["tone"]


def set_tone(name):
	_state["tone"] = name
	d = _cfg()
	d["tone"] = name
	d["enabled"] = is_enabled()
	try:
		with open(CONFIG_FILE, "w", encoding="utf-8") as f:
			json.dump(d, f)
	except Exception:
		pass


def preview_tone(name):
	play_file(os.path.join(TONE_DIR, name + ".wav"))


def play_tone():
	"""The message ringtone chosen in NVDA settings. Plays when a Friends Mirror notification appears."""
	path = os.path.join(TONE_DIR, get_tone() + ".wav")
	if not os.path.isfile(path):
		return
	try:
		import nvwave
		nvwave.playWaveFile(path, asynchronous=True)
		return
	except Exception:
		pass
	try:
		import winsound
		winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
	except Exception:
		pass
