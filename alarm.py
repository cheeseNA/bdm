import simpleaudio


def alarm():
    print('alarm')
    wave_obj = simpleaudio.WaveObject.from_wave_file(
        '/usr/share/sounds/alsa/Front_Center.wav')
    play_obj = wave_obj.play()
    print('playing')
    play_obj.wait_done()
    print('playing done')


if __name__ == '__main__':
    alarm()
