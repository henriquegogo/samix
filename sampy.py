import re, sys
import yaml
from pydub import AudioSegment
from pydub.playback import play

def load_samples(samples):
    bank = {}
    for instr,path in samples.items():
        if path.find('[') < 0:
            path_ext = path.split('.')[-1]
            bank[instr] = AudioSegment.from_file(path, format=path_ext)

    for instr,path in samples.items():
        if path.find('[') > 0:
            source_instr = path.split('[')[0]
            source_range = path.split('[')[1][:-1].split(':')
            source_begin_time = int(source_range[0])
            source_end_time = int(source_range[1])
            bank[instr] = bank[source_instr][source_begin_time:source_end_time] 

    return bank

def create_music(bank, pattern, bpm):
    beat_duration = 60000 / 2 / bpm 
    first_beats_length = len(re.sub("[^X\.]", '', pattern[pattern.keys()[0]]))
    total_duration = first_beats_length * beat_duration

    music = AudioSegment.silent(duration=total_duration)

    for instr,beats in pattern.items():
        beats = re.sub("[^X\.]", '', beats)
        sample = bank[instr]
        for i in range(len(beats)):
            if beats[i] == 'X':
                position = i * beat_duration
                music = music.overlay(sample, position=position)

    return music


def main():
    if len(sys.argv) <= 1: sys.exit('YAML file missing. Please type as command line argument.')
        
    yaml_path = sys.argv[1]
    score_content = file(yaml_path, 'r').read()
    score = yaml.load(score_content)

    samples = score['samples']
    pattern = score['pattern']
    bpm = score['bpm']

    bank = load_samples(samples)
    music = create_music(bank, pattern, bpm)

    play(music)

if __name__ == '__main__': main()
