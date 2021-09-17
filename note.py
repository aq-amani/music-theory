# Octave 4
basic_notes = {
    "C"  : {"alt_name" : "",   "frequency" : 261.63},
    "C#" : {"alt_name" : "Db", "frequency" : 277.18},
    "D"  : {"alt_name" : "",   "frequency" : 293.66},
    "D#" : {"alt_name" : "Eb", "frequency" : 311.13},
    "E"  : {"alt_name" : "",   "frequency" : 329.63},
    "F"  : {"alt_name" : "",   "frequency" : 349.23},
    "F#" : {"alt_name" : "Gb", "frequency" : 369.99},
    "G"  : {"alt_name" : "",   "frequency" : 392.00},
    "G#" : {"alt_name" : "Ab", "frequency" : 415.30},
    "A"  : {"alt_name" : "",   "frequency" : 440.00},
    "A#" : {"alt_name" : "Bb", "frequency" : 466.16},
    "B"  : {"alt_name" : "",   "frequency" : 493.88},
}

class Note:

    def __init__(self, name, octave):
        #Ensure first character of name is in upper case
        name = name[0].upper() + name[1:]
        self.name = name
        self.octave = octave
        octave_multiplier = self.octave_converter()
        self._frequency = basic_notes[name]['frequency'] * octave_multiplier

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

    @octave.setter
    def octave(self, value):
        if value not in range(2,7):
            raise ValueError("Invalid octave value")
        self._octave = value

    def octave_converter(self):
        """Converts an octave to a frequency multiplier.
        Octave 4 translates to x1 multiplier since our basic_notes list is based on the 4th octave.

        Arguments:
        octave -- octave at which to play the scale
        """
        return 2 ** (self.octave - 4)

    def get_consecutive_notes(self, note_count):
        """Get note_count consecutive notes half step apart while updating octave as necessary"""

        note_names = list(basic_notes.keys())
        note_index = note_names.index(self.name)
        note_list = [self]
        octave = self.octave
        for i in range(1, note_count):
            note_index += 1
            normalized_note_index = note_index%len(note_names)
            if normalized_note_index == 0:
                octave += 1
            note_list.append(Note(note_names[normalized_note_index], octave))
        return note_list