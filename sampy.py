import re, sys
import yaml
from pydub import AudioSegment
from pydub.playback import play

def load_samples(samples):
    bank = {}
    for instr,path in samples.items():
        if path.find('[') < 0:
            regex_match = re.search('(^.*?)\.(\w*)\s*\*?(.*)$', path)
            file_path = regex_match.group(1) + '.' + regex_match.group(2)
            path_ext = regex_match.group(2)
            bank[instr] = AudioSegment.from_file(file_path, format=path_ext)
            speed_rate = float(regex_match.group(3) or 1)
            bank[instr].frame_rate = int(bank[instr].frame_rate * speed_rate)

    for instr,path in samples.items():
        if path.find('[') > 0:
            regex_match = re.search('(^\w*)\[(.*)\]\s*\*?(.*)$', path)
            source_instr = regex_match.group(1)
            source_range = regex_match.group(2).split(':')
            source_begin_time = int(source_range[0])
            source_end_time = int(source_range[1])
            bank[instr] = bank[source_instr][source_begin_time:source_end_time] 
            speed_rate = float(regex_match.group(3) or 1)
            bank[instr].frame_rate = int(bank[instr].frame_rate * speed_rate)

    return bank

def registry_patterns(bank, patterns, bpm, ratio):
    for name,pattern in patterns.items():
        bank[name] = create_pattern(bank, pattern, bpm, ratio)

def create_pattern(bank, pattern, bpm, ratio):
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

    try:
        score_content = file(yaml_path, 'r').read()
    except:
        print('File ' + yaml_path + ' does not exist') 
        return 0

    score = yaml.load(score_content)

    samples = score['samples']
    patterns = score['patterns']
    song = score['song']
    bpm = score['bpm']
    ratio = score.get('ratio') or 2

    bank = load_samples(samples)
    registry_patterns(bank, patterns, bpm, ratio)
    music = create_pattern(bank, song, bpm, ratio)

    if len(sys.argv) == 2:
        play(music)
    else:
        export_path = sys.argv[2]
        extension = export_path.split('.')[1]
        music.export(export_path, format=extension)
        print('Song ' + export_path + ' created with success.')

if __name__ == '__main__': main()
