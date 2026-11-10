# -*- coding: UTF-8 -*-
"""Soft background music that plays while Friends Mirror is open (an option in Profile and privacy)."""
import os
import threading
import wave

SOUNDS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sounds"))
TRACKS = [("Lo-fi groove", "music_lofi"), ("Piano dreams", "music_dream"), ("Calm pads", "music_calm")]
PATH = os.path.join(SOUNDS, "music_lofi.wav")
_state = {"stop": None, "gain": 0.6, "track": "music_lofi"}
ABOUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sounds", "about.wav"))


def playing():
	return _state["stop"] is not None


def set_track(name):
	if name in [t[1] for t in TRACKS] and name != _state["track"]:
		_state["track"] = name
		if playing():
			stop()
			start()


def set_gain(g):
	_state["gain"] = max(0.05, min(1.0, float(g)))


def start(force=False):
	path = os.path.join(SOUNDS, _state["track"] + ".wav")
	if _state["stop"] is not None or not os.path.isfile(path):
		return
	stop_ev = threading.Event()
	_state["stop"] = stop_ev
	threading.Thread(target=_run, args=(stop_ev, path), daemon=True).start()


def stop():
	ev = _state["stop"]
	_state["stop"] = None
	if ev:
		ev.set()


def _run(stop_ev, path):
	player = None
	try:
		import nvwave
		with wave.open(path, "rb") as w:
			rate, ch, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
			data = w.readframes(w.getnframes())
		if width == 2 and _state["gain"] < 0.99:
			import array
			a = array.array("h")
			a.frombytes(data)
			g = _state["gain"]
			data = array.array("h", [int(x * g) for x in a]).tobytes()
		player = nvwave.WavePlayer(channels=ch, samplesPerSec=rate, bitsPerSample=width * 8)
		step = rate * ch * width // 4
		step -= step % (ch * width)
		import time
		t0, fed = time.time(), 0.0
		per = step / float(rate * ch * width)
		while not stop_ev.is_set():
			for i in range(0, len(data), step):
				if stop_ev.is_set():
					break
				player.feed(data[i:i + step])
				fed += per
				ahead = fed - (time.time() - t0)
				if ahead > 0.4:
					stop_ev.wait(ahead - 0.3)
	except Exception:
		pass
	finally:
		try:
			if player:
				player.stop()
				player.close()
		except Exception:
			pass


def sync(ctrl):
	"""Play while a Friends Mirror window is open and the option is on."""
	try:
		on = ctrl.engine.me and ctrl.engine.setting("bgmusic") and (ctrl.main or ctrl.windows)
	except Exception:
		on = False
	try:
		set_gain(ctrl.engine.setting("bgmvol"))
		tr = ctrl.engine.setting("bgmtrack")
		if tr:
			set_track(tr)
	except Exception:
		pass
	start() if on else stop()


class Clip(object):
	"""Plays one WAV file once, mixed with whatever else is playing (the background music keeps going)."""

	def __init__(self, path):
		self.path = path
		self.ev = threading.Event()
		self.paused = False
		self.resume_ev = threading.Event()
		self.player = None
		threading.Thread(target=self._run, daemon=True).start()

	def stop(self):
		self.ev.set()
		self.resume_ev.set()

	def toggle(self):
		"""Pause or resume. Returns True when now paused."""
		self.paused = not self.paused
		try:
			if self.player:
				self.player.pause(self.paused)
		except Exception:
			pass
		if not self.paused:
			self.resume_ev.set()
		return self.paused

	def _run(self):
		player = None
		try:
			import nvwave
			import time
			with wave.open(self.path, "rb") as w:
				rate, ch, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
				data = w.readframes(w.getnframes())
			player = nvwave.WavePlayer(channels=ch, samplesPerSec=rate, bitsPerSample=width * 8)
			self.player = player
			step = rate * ch * width // 4
			step -= step % (ch * width)
			per = step / float(rate * ch * width)
			t0, fed = time.time(), 0.0
			for i in range(0, len(data), step):
				if self.ev.is_set():
					break
				if self.paused:
					self.resume_ev.clear()
					self.resume_ev.wait()
					t0, fed = time.time(), 0.0
					if self.ev.is_set():
						break
				player.feed(data[i:i + step])
				fed += per
				ahead = fed - (time.time() - t0)
				if ahead > 0.4:
					self.ev.wait(ahead - 0.3)
			if not self.ev.is_set():
				player.idle()
		except Exception:
			pass
		finally:
			try:
				if player:
					player.stop()
					player.close()
			except Exception:
				pass
