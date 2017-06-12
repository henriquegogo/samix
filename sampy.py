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

def create_music(bank, pattern, bpm, ratio=2):
    beat_duration = 60000 / bpm / ratio
    first_beats_length = len(re.sub("[^X\.=]", '', pattern[pattern.keys()[0]]))
    total_duration = first_beats_length * beat_duration

    music = AudioSegment.silent(duration=total_duration)

    for instr,beats in pattern.items():
        beats = re.sub("[^X\.=]", '', beats)
        last_play_position = None
        for i in range(len(beats)):
            if beats[i] == 'X':
                last_play_position = int(i)
                if i+1 < len(beats) and beats[i+1] == '=':
                    sample = bank[instr][:beat_duration]
                else:
                    sample = bank[instr][0:]
                position = i * beat_duration
                music = music.overlay(sample, position=position)
            elif beats[i] == '=':
                counter = 0
                while counter + i < len(beats) and beats[counter+i] == '=':
                    counter += 1
                counter += i - last_play_position
                position = i * beat_duration
                sample_begin_time = (len(bank[instr]) / counter) * (i - last_play_position)
                sample_end_time = sample_begin_time + beat_duration
                sample = bank[instr][sample_begin_time:sample_end_time]
                music = music.overlay(sample, position=position)
            else:
                last_play_position = None

    return music


def main():
    if len(sys.argv) <= 1: sys.exit('YAML file missing. Please type as command line argument.')
        
    yaml_path = sys.argv[1]
    score_content = file(yaml_path, 'r').read()
    score = yaml.load(score_content)

    samples = score['samples']
    pattern = score['pattern']
    bpm = score['bpm']
    ratio = score.get('ratio') or 2

    bank = load_samples(samples)
    music = create_music(bank, pattern, bpm, ratio)

    if len(sys.argv) == 2:
        play(music)
    else:
        export_path = sys.argv[2]
        extension = export_path.split('.')[1]
        music.export(export_path, format=extension)
        print('Song ' + export_path + ' created with success.')

if __name__ == '__main__': main()
