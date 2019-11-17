# Human readable sample sequencer file
It's easy to create music with simple YAML files.

## Header
```yaml
title: Song title
bpm: 180
```

## Samples
Declare sample file paths and start/end in miliseconds.
You can multiply if want to change the pitch.

```yaml
samples:
  audio:  sample.mp3
  kick:   audio[10701:10937]*2
  snare:  audio[10185:10679] * 1.8
  guitar: audio[800:2010]
  vocal:  audio[181220:186905]
```

## Patterns
Patterns works like samples, but you can presequence parts of song or riffs

```yaml
patterns:
  drums:
    kick:   X...|X...|X...|X..X
    snare:  ...X|..X.|...X|..X.
  riff:
    guitar: ..X.|..XX
```

## Song
Here is where the magic happens. Use call samples or patterns sequencing in a horizontal line.
You can use '=' symbol if want to fit the sample inside de measurement.

- X symbol will shot the sample or pattern
- = symbol will slice sample or pattern proportionally and fit in measurement
- - symbol stops sound

```yaml
song:
  drums:    X...|....|....|....|X...|....|....|....
            X...|....|....|....|X...|....|....|....

  riff:     X...|....|X...|....|X...|....|X...|....
            X...|....|X...|....|X...|....|X...|....

  vocal:    ....|....|....|....|X===|====|====|====
            ====|====|====|====|....|....|....|....
```
