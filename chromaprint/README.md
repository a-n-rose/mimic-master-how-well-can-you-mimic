 
# Mimic Master

A game using spectral fingerprints to compare target sounds and mimicked sounds.

## Getting Started

In the directory with the python files, create a subdirectory called 'soundfiles'. In this directory put any wave files you would like the game to play. I collected free sounds from freesound.org.

The game currently requires a "go_wave" wavefile in the 'soundfiles directory'. I used the recording: 
231277__steel2008__race-start-ready-go.wav
from freesound.org. Whatever file you use, change the name in 'play_go' function in the file 'voice_master.py'

When everything is set up, run 'voice_master_main.py'.


### Prerequisites

A microphone is necessary, headphones are advised, and definitely don't do this in a library or similar quiet setting. You will look crazy.

All the dependencies can be installed using

```
pip install __________
```
For the dependencies necessary, please refer to the installations.md file

### Installing

To set up a virtual environment, in the directory you have your project in, type the following into your commandline:
```
python -m venv env
source env/bin/activate
```
Your virtual environment should be activated and you can install all the dependencies via:
```
pip install __________
```

## Authors

* **Aislyn Rose**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Audacity's open-source code definitely inspired my own noise reduction function. Hat tip to you, Audacity!

* Free Sound (freesound.org) for offering such a variety of sounds
