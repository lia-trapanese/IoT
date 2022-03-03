import pwm
def note(baseFreq, octave):
    diff = octave - 4
    if diff > 0:
        return baseFreq * (2 ** diff)
    else:
        return baseFreq / (2 ** (-1 * diff))

def A(octave):
    return note(443.00, octave)

def As(octave):
    return note(466.16,	octave)

def Bb(octave):
    return As(octave)

def B(octave):
    return note(493.88, octave)

def C(octave):
    return note(261.63, octave)

def Cs(octave):
    return note(277.18, octave)

def Eb(octave):
    return Cs(octave)

def D(octave):
    return note(293.66, octave)

def Ds(octave):
    return note(311.13, octave)

def Eb(octave):
    return Ds(octave)

def E(octave):
    return note(329.63, octave)

def F(octave):
    return note(349.23, octave)

def Fs(octave):
    return note(369.99, octave)

def Gb(octave):
    return Fs(octave)

def G(octave):
    return note(392.00, octave)

def Gs(octave):
    return note(415.30, octave)
 
#Inno alla gioia                          
notes       = [B(4), B(4), C(5), D(5), D(5), C(5), B(4), A(4), G(4), G(4), A(4), B(4), B(4), A(4), A(4), B(4), B(4), C(5), D(5), D(5), C(5), B(4), A(4), G(4), G(4), A(4), B(4), A(4), G(4), G(4), 0.01]
durations   = [  1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   2,   1,   2,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   2,   1,   2,   4]

#Hallelujah
#notes      = [ E(4), G(4), G(4), G(4), G(4), A(4), A(4), A(4), E(4), G(4), G(4), G(4), G(4), A(4), A(4), A(4), G(4), A(4), A(4), A(4), A(4), A(4), G(4), G(4), F(4), G(4), G(4),   B(1), E(4), G(4), G(4), G(4), G(4), A(4), A(4), B(4), G(4), C(5), C(5), C(5), C(5), C(5), C(5), D(5), C(5), D(5), D(5), D(5), E(5), E(5), D(5), D(5), C(5), E(4), G(4), A(4), A(4), A(4), G(4), E(4), E(4), E(4), G(4), A(4), A(4), A(4), G(4), E(4), E(4), E(4), G(4), A(4), A(4), A(4), G(4), E(5), D(5), C(5)]
#durations = [   .5,    1,   .5,    1,   .5,   .5,   .5,  1.5,   .5,    1,    .5,   1,   .5,   .5,   .5,  1.5,   .5,    1,    1,   .5,   .5,    1,   .5,    1,   .5,  1.5,  1.5,   2.5,   .5,    1,   .5,    1,   .5,    1,   .5,    1,   .5,    1,   .5,    1,   .5,    1,   .5,    1,   .5,    1,  1.5,   .5,  1.5,    1,   .5,  1.5,    3,    1,   .5,  1.5,    3,     1,  .5,  1.5,    3,    1,   .5,  1.5,    3,     1,  .5,  1.5,     3,   1,    .5,  1.5,    3,   1,    .5,    3,    3,    3]


def reproduce(notes, durations, pin, event):
    currentNote = 0
    duration = 0
    frequency = 440
    pwm.write(pin, 20000, 2, MICROS)
    while True:
        event.wait()
        sleep(2000)
        while event.is_set():
            sleep(10)
            frequency = notes[currentNote]
            duration = int(durations[currentNote] * 1000 // (120 // 60))
            if notes[currentNote] == 0.01:
                period = 0 
            else:
                period = int(1000000 // frequency)
        
            pwm.write(pin, period, int(period * .9), MICROS)
        
            currentNote += 1
            
            if currentNote >= len(notes):
                currentNote = 0
                
            sleep(duration - 10)
        currentNote = 0
        pwm.write(pin, 20000, 2, MICROS)
        sleep(30)
        
