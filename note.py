# Octave 4
basic_notes = {
    "C"  : {"alt_name" : "",   "frequency" : 261.63, "midi_id" : 60},
    "C#" : {"alt_name" : "Db", "frequency" : 277.18, "midi_id" : 61},
    "D"  : {"alt_name" : "",   "frequency" : 293.66, "midi_id" : 62},
    "D#" : {"alt_name" : "Eb", "frequency" : 311.13, "midi_id" : 63},
    "E"  : {"alt_name" : "",   "frequency" : 329.63, "midi_id" : 64},
    "F"  : {"alt_name" : "",   "frequency" : 349.23, "midi_id" : 65},
    "F#" : {"alt_name" : "Gb", "frequency" : 369.99, "midi_id" : 66},
    "G"  : {"alt_name" : "",   "frequency" : 392.00, "midi_id" : 67},
    "G#" : {"alt_name" : "Ab", "frequency" : 415.30, "midi_id" : 68},
    "A"  : {"alt_name" : "",   "frequency" : 440.00, "midi_id" : 69},
    "A#" : {"alt_name" : "Bb", "frequency" : 466.16, "midi_id" : 70},
    "B"  : {"alt_name" : "",   "frequency" : 493.88, "midi_id" : 71},
}

MAX_OCTAVE = 8
MIN_OCTAVE = 0

class Note:

    def __init__(self, name, octave):
        #Ensure first character of name is in upper case
        name = name[0].upper() + name[1:]
        self.name = name
        self.octave = octave
        self._midi_id = self.get_midi_id()
        octave_multiplier = self.octave_converter()
        self._frequency = basic_notes[self.name]['frequency'] * octave_multiplier

    def __eq__(self, other):
        if not isinstance(other, Note):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and self.octave == other.octave


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        for note_name, note_info in basic_notes.items():
            if value == note_name or value == note_info['alt_name']:
                self._name = note_name
                self._alt_name = note_info['alt_name']
                return
        raise ValueError("Invalid note name")

    @property
    def alt_name(self):
        return self._alt_name

    @property
    def frequency(self):
        return self._frequency

    @property
    def octave(self):
        return self._octave

    @property
    def midi_id(self):
        return self._midi_id

    @octave.setter
    def octave(self, value):
        if value not in range(MIN_OCTAVE, MAX_OCTAVE+1):
            raise ValueError("Invalid octave value")
        self._octave = value

    def octave_converter(self):
        """Converts an octave to a frequency multiplier.
        Octave 4 translates to x1 multiplier since our basic_notes list is based on the 4th octave.

        Arguments:
        self -- note object that contains the octave
        """
        return round(2 ** (self.octave - 4), 2)

    def get_midi_id(self):
        """Shifts midi id by multiples of 12 depending on the octave.
        Octave 4 translates to 0 offset since our basic_notes list is based on the 4th octave.

        Arguments:
        self -- note object that contains the octave
        """
        return  basic_notes[self.name]['midi_id'] + 12 * (self.octave - 4)

    def get_consecutive_notes(self, halfstep_count):
        """Get halfstep_count consecutive notes half step apart while updating octave as necessary"""

        note = self
        note_list = [note]
        for i in range(1, halfstep_count):
            note = note.get_next_step_note(1)
            note_list.append(note)
        return note_list

    def get_next_step_note(self, halfstep_count):
        """Gets the next note that is halfstep_count above or below while updating octave as necessary
        Arguments:
        halfstep_count -- (int) number of half steps to increase/decrease (negative value for decrements)
        """

        note_names = list(basic_notes.keys())
        note_index = note_names.index(self.name)
        octave = self.octave
        note_index += halfstep_count
        normalized_note_index = note_index%len(note_names) if note_index >= 0 else (len(note_names) - abs(note_index)%len(note_names))%len(note_names)
        octave += int(note_index/len(note_names)) if note_index >= 0 else (int((abs(note_index)-1)/len(note_names)) + 1) * -1
        return Note(note_names[normalized_note_index], octave)
