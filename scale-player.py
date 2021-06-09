import pyaudio
import numpy as np

p = pyaudio.PyAudio()

volume = 0.5     # range [0.0, 1.0]
sample_rate = 44100       # sampling rate, Hz, must be integer
duration = 1   # in seconds, may be float
start_note_frequency = 262.0        # sine frequency, Hz, may be float
end_note_frequency = 530.0
octave = 2

S = 2**(1/12) # Semi-tone frequency multiplier
T = S ** 2 # Full-tone frequency multiplier
major_scale_signature = [T,T,S,T,T,T,S]
starting_note_offset = 0 # 0 when starting from Do, 1 for Re..etc. To define where to start reading the scale_signature.
note = start_note_frequency * octave
iteration_number = 0
while note <= end_note_frequency*octave:
    print(note)
    # generate samples, note conversion to float32 array
    samples = (np.sin(2*np.pi*np.arange(sample_rate*duration)*note/sample_rate)).astype(np.float32)

    # for paFloat32 sample values must be in range [-1.0, 1.0]
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # play. May repeat with different volume values (if done interactively)
    stream.write(volume*samples)

    stream.stop_stream()
    stream.close()
    note *= major_scale_signature[starting_note_offset + iteration_number%7]
    iteration_number += 1

p.terminate()
