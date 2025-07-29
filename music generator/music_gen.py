from music21 import converter, instrument, note, chord, stream
import glob
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical

def get_notes(folder):
    notes = []
    for file in glob.glob(folder + "/*.mid"):
        midi = converter.parse(file)
        parts = instrument.partitionByInstrument(midi)
        notes_to_parse = parts.parts[0].recurse() if parts else midi.flat.notes
        for element in notes_to_parse:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes.append('.'.join(str(n) for n in element.normalOrder))
    return notes

notes = get_notes("midi_songs")
seq_len = 100
pitchnames = sorted(set(notes))
note_to_int = {n:i for i,n in enumerate(pitchnames)}

seq_in = []
seq_out = []
for i in range(len(notes) - seq_len):
    seq_in.append([note_to_int[n] for n in notes[i:i+seq_len]])
    seq_out.append(note_to_int[notes[i+seq_len]])

n_patterns = len(seq_in)
X = np.reshape(seq_in, (n_patterns, seq_len, 1)) / float(len(pitchnames))
y = to_categorical(seq_out)

model = Sequential([
    LSTM(512, input_shape=(X.shape[1], X.shape[2]), return_sequences=True),
    Dropout(0.3),
    LSTM(512),
    Dense(256, activation='relu'),
    Dropout(0.3),
    Dense(len(pitchnames), activation='softmax')
])
model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
model.fit(X, y, epochs=50, batch_size=64)

def gen_notes(mdl, seq_in, names, n_to_i, length=500):
    i_to_n = {i:n for n,i in n_to_i.items()}
    start = np.random.randint(0, len(seq_in)-1)
    pattern = list(seq_in[start])
    output = []
    for _ in range(length):
        x = np.reshape(pattern, (1, len(pattern), 1)) / float(len(names))
        pred = mdl.predict(x, verbose=0)
        idx = np.argmax(pred)
        output.append(i_to_n[idx])
        pattern.append(idx)
        pattern = pattern[1:]
    return output

def create_midi(pred, filename="output.mid"):
    offset = 0
    out_notes = []
    for p in pred:
        if '.' in p:
            c_notes = [note.Note(midi=n) for n in map(int, p.split('.'))]
            c = chord.Chord(c_notes)
            c.offset = offset
            out_notes.append(c)
        else:
            n = note.Note(p)
            n.offset = offset
            out_notes.append(n)
        offset += 0.5
    stream.Stream(out_notes).write('midi', fp=filename)

gen = gen_notes(model, seq_in, pitchnames, note_to_int)
create_midi(gen)
