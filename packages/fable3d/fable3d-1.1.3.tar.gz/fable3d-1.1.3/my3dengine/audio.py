import numpy as np
import sounddevice as sd
import soundfile as sf
import threading

class AudioListener:
    def __init__(self, position):
        self.position = np.array(position, dtype=float)

class AudioSource:
    def __init__(self, position, sound_path, emit_radius=15.0, volume=1.0, loop=False, fade_duration=1.0):
        self.position = np.array(position, dtype=float)
        self.sound_path = sound_path
        self.emit_radius = emit_radius
        self.base_volume = volume
        self.loop = loop

        self._data, self._fs = sf.read(self.sound_path, dtype='float32')
        self._stream = None
        self._stop_flag = threading.Event()
        self._lock = threading.Lock()

        self._volume = 0.0        # aktualna głośność (płynna)
        self._target_volume = 0.0 # docelowa głośność (fade target)
        self._fade_duration = fade_duration  # czas fade w sekundach

        self._pos = 0
        self.playing = False
        self._paused = False

        self.MIN_VOLUME_TO_PLAY = 0.01

    def _callback(self, outdata, frames, time, status):
        with self._lock:
            if self._stop_flag.is_set():
                raise sd.CallbackStop()

            chunk_start = self._pos
            chunk_end = self._pos + frames

            if chunk_end > len(self._data):
                if self.loop:
                    part1 = self._data[chunk_start:]
                    part2 = self._data[:chunk_end - len(self._data)]
                    chunk = np.concatenate((part1, part2))
                    self._pos = chunk_end - len(self._data)
                else:
                    chunk = self._data[chunk_start:]
                    chunk = np.pad(chunk, ((0, frames - len(chunk)), (0, 0)), mode='constant')
                    self._pos = len(self._data)
            else:
                chunk = self._data[chunk_start:chunk_end]
                self._pos = chunk_end

            current_vol = self._volume
            target_vol = self._target_volume

            fade_step = 1.0 / (self._fs * self._fade_duration)  # ile głośności na 1 próbkę

            steps = np.arange(frames, dtype=np.float32)

            if target_vol > current_vol:
                volumes = current_vol + fade_step * steps * (target_vol - current_vol)
                volumes = np.clip(volumes, 0.0, target_vol)
            else:
                volumes = current_vol - fade_step * steps * (current_vol - target_vol)
                volumes = np.clip(volumes, target_vol, 1.0)

            self._volume = volumes[-1]

            if self._paused or self._volume < self.MIN_VOLUME_TO_PLAY:
                outdata[:] = 0
            else:
                if chunk.ndim > 1:
                    volumes = volumes[:, np.newaxis]
                outdata[:] = chunk * volumes

            if not self.loop and self._pos >= len(self._data):
                raise sd.CallbackStop()

    def _on_finished(self):
        with self._lock:
            self._stream = None
            self.playing = False
            self._volume = 0.0
            self._target_volume = 0.0
            self._pos = 0
            self._paused = False

    def play(self, volume):
        with self._lock:
            if self.playing:
                if self._paused:
                    # Jeśli jest pauza, wznow i ustaw docelową głośność
                    self._paused = False
                    self._target_volume = volume
                    return
                else:
                    # Już gra, więc ustaw tylko docelową głośność
                    self._target_volume = volume
                    return

            # Nowe odtwarzanie od zera z głośnością 0 i fade-in
            self._volume = 0.0
            self._target_volume = volume
            self._pos = 0
            self._stop_flag.clear()

            self._stream = sd.OutputStream(
                samplerate=self._fs,
                channels=self._data.shape[1] if self._data.ndim > 1 else 1,
                callback=self._callback,
                finished_callback=self._on_finished
            )
            self._stream.start()
            self.playing = True
            self._paused = False

    def pause(self):
        with self._lock:
            if self.playing and not self._paused:
                self._target_volume = 0.0  # fade out do 0, ale stream działa
                # _paused ustawiane w callbacku, gdy głośność spadnie do zera

    def resume(self):
        with self._lock:
            if self.playing and self._paused:
                self._paused = False
                self._volume = 0.0  # zaczynamy z 0, fade-in w callbacku
                self._target_volume = self.base_volume  # docelowa głośność

    def stop(self):
        with self._lock:
            if self._stream:
                self._stop_flag.set()
            self.playing = False
            self._volume = 0.0
            self._target_volume = 0.0
            self._pos = 0
            self._paused = False

    def set_target_volume(self, volume):
        with self._lock:
            self._target_volume = max(0.0, min(volume, 1.0))

class BackgroundMusic:
    def __init__(self, sound_path, volume=1.0, loop=True, fade_duration=1.0):
        self._data, self._fs = sf.read(sound_path, dtype='float32')
        self._stream = None
        self._stop_flag = threading.Event()
        self._lock = threading.Lock()
        self._volume = 0.0
        self._target_volume = volume
        self._fade_duration = fade_duration
        self._pos = 0
        self.loop = loop
        self.playing = False
        self._paused = False

    def _callback(self, outdata, frames, time, status):
        with self._lock:
            if self._stop_flag.is_set():
                raise sd.CallbackStop()

            chunk_start = self._pos
            chunk_end = self._pos + frames

            if chunk_end > len(self._data):
                if self.loop:
                    part1 = self._data[chunk_start:]
                    part2 = self._data[:chunk_end - len(self._data)]
                    chunk = np.concatenate((part1, part2))
                    self._pos = chunk_end - len(self._data)
                else:
                    chunk = self._data[chunk_start:]
                    chunk = np.pad(chunk, ((0, frames - len(chunk)), (0, 0)), mode='constant')
                    self._pos = len(self._data)
            else:
                chunk = self._data[chunk_start:chunk_end]
                self._pos = chunk_end

            current_vol = self._volume
            target_vol = self._target_volume
            fade_step = 1.0 / (self._fs * self._fade_duration)
            steps = np.arange(frames, dtype=np.float32)

            if target_vol > current_vol:
                volumes = current_vol + fade_step * steps * (target_vol - current_vol)
                volumes = np.clip(volumes, 0.0, target_vol)
            else:
                volumes = current_vol - fade_step * steps * (current_vol - target_vol)
                volumes = np.clip(volumes, target_vol, 1.0)

            self._volume = volumes[-1]

            if self._paused:
                outdata[:] = 0
            else:
                if chunk.ndim > 1:
                    volumes = volumes[:, np.newaxis]
                outdata[:] = chunk * volumes

            if not self.loop and self._pos >= len(self._data):
                raise sd.CallbackStop()

    def _on_finished(self):
        with self._lock:
            self._stream = None
            self.playing = False
            self._volume = 0.0
            self._target_volume = 0.0
            self._pos = 0
            self._paused = False

    def play(self):
        with self._lock:
            if self.playing:
                return

            self._volume = 0.0
            self._stop_flag.clear()
            self._stream = sd.OutputStream(
                samplerate=self._fs,
                channels=self._data.shape[1] if self._data.ndim > 1 else 1,
                callback=self._callback,
                finished_callback=self._on_finished
            )
            self._stream.start()
            self.playing = True
            self._paused = False

    def pause(self):
        with self._lock:
            self._target_volume = 0.0
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False
            self._target_volume = 1.0

    def stop(self):
        with self._lock:
            self._stop_flag.set()
            self.playing = False
            self._volume = 0.0
            self._target_volume = 0.0
            self._pos = 0
            self._paused = False

    def set_target_volume(self, volume):
        with self._lock:
            self._target_volume = max(0.0, min(volume, 1.0))

def update_audio_system(listener, sources, debug=False):
    for source in sources:
        dist = np.linalg.norm(listener.position - source.position)

        if dist <= source.emit_radius:
            attenuation = 1.0 - dist / source.emit_radius
            volume = source.base_volume * attenuation

            if debug:
                print(f"[Audio] Distance: {dist:.2f}, Volume: {volume:.2f}")

            if not source.playing:
                source.play(volume)
            else:
                if source._paused:
                    # Jeśli był pauzowany, startuj od nowa z głośnością 0 i fade-in
                    source.stop()
                    source.play(volume)
                else:
                    source.set_target_volume(volume)

        else:
            if source.playing:
                source.set_target_volume(0.0)
                # Poczekaj, aż głośność spadnie prawie do zera, wtedy pauzuj
                if source._volume <= 0.01 and not source._paused:
                    if debug:
                        print(f"[PAUSE] {source.sound_path} - volume zero")
                    source.pause()
