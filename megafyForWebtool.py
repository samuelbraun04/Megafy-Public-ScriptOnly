# THIS FILE IS A WORK IN PROGRESS. IT'LL BE USED WITHIN THE DJANGO PROJECT (THE WEBTOOL) – ONCE WE'RE FINISHED DEVELOPPING THE FRONT END.
# CURRENTLY, THIS FILE IS NOT FUNCTIONAL. USE megafyUserInteractive.py TO USE MEGAFY (FOR NOW).

from librosa import load
from moviepy.editor import AudioFileClip
from os import chdir, walk, path
from scipy.io.wavfile import write
import dawdreamer as daw

#MAIN PATHS (replace with your paths)
INPUT_FOLDER = r'C:\Users\samlb\Documents\MEGAFY\Input Folder'
OUTPUT_FOLDER = r'C:\Users\samlb\Documents\MEGAFY\Output Folder'

#PRESETS
BASS_BOOST_PRESETS = r'C:\Users\samlb\Documents\MEGAFY\Presets\BarkOfDog2'
SOFT_CLIPPER_PRESETS = r'C:\Users\samlb\Documents\MEGAFY\Presets\Initial Clipper'
REVERB_PRESETS = r'C:\Users\samlb\Documents\MEGAFY\Presets\MConvolutionEZ'

#PLUGINS
SOFT_CLIPPER_PLUGIN = r'C:\Users\samlb\Documents\MEGAFY\Plugins\Initial Clipper.dll'
BASS_BOOST_PLUGIN = r'C:\Users\samlb\Documents\MEGAFY\Plugins\BarkOfDog2.dll'
REVERB_PLUGIN = r'C:\Users\samlb\Documents\MEGAFY\Plugins\MConvolutionEZ.dll'

#MAIN VARIABLES
VALID_FILETYPES = ['.mp3', '.wav', '.m4a', '.aac']
ILLEGAL_CHARACTERS = ['<','>',':','"','/','\\','|','?','*']
SAMPLE_RATE = 44100
BUFFER_SIZE = 512
OUR_GRAPH = []
ORDER = ""
CONFIGURATION_CHOICES_MADE = False

#Convert audio file to usable form for graph
def load_audio_file(file_path, duration=None):
    chdir(INPUT_FOLDER)
    sig, rate = load(file_path, duration=duration, mono=False, sr=SAMPLE_RATE)
    assert(rate == SAMPLE_RATE)
    return sig

def savePreset(presetFolder, presetValues):
        while(1):
            presetName = str(input("What would you like to name your preset?: "))
            if  len([e for e in ILLEGAL_CHARACTERS if e in presetName]) != 0:
                print("Please use legal file characters!")
            else:
                break
        
        for counter in range(len(presetValues)):
            presetValues[counter] = str(presetValues[counter])

        chdir(presetFolder)
        with open(presetName+'.txt', 'w') as file_handler:
            for item in presetValues:
                file_handler.write("{}\n".format(item))

def loadPreset(presetFolder):
    
    currentPresets = next(walk(presetFolder), (None, None, []))[2]
    
    print("Here are the available presets: ")
    originalFiles = []
    for files in range(len(currentPresets)):
        originalFiles.append(currentPresets[files])
        currentPresets[files] = '    '+str(files+1)+': '+currentPresets[files][:-4]
        print(currentPresets[files])

    while(1):
        try:
            presetAnswer = int(input("Please input the number associated with the preset you'd like to choose: "))
            chosenPreset = originalFiles[presetAnswer-1]
            break
        except IndexError:
            print("Please input a number that's associated with a preset!")
        except ValueError:
            print("Please input a number!")

    chdir(presetFolder)
    with open(chosenPreset) as file: #the txt file would be their preset
        presetValues = file.readlines()
        presetValues = [line.rstrip() for line in presetValues]
    
    return presetValues

#Get user basic choices
PITCH_SHIFT_CHOICE = True #Would user like files pitch shifted?
BASS_BOOST_CHOICE = True #Would user like files bass boosted?
REVERB_CHOICE = True #Would user like files reverbed?
SOFT_CLIPPER_CHOICE = True #Would user like files soft clipped?

#Get the files and set the engine
filesToMegafy = next(walk(INPUT_FOLDER), (None, None, []))[2]
engine = daw.RenderEngine(SAMPLE_RATE, BUFFER_SIZE)

#Customize all files in the input folder
for counter in range(len(filesToMegafy)):

    #Reset graph
    OUR_GRAPH = []

    #Other files sometime appear in the output folder for some reason (like a jpeg called "album art" but I cant see it?)
    chdir(INPUT_FOLDER)
    myExtension = path.splitext(filesToMegafy[counter])[1]
    if myExtension not in VALID_FILETYPES:
        continue

    #Get song
    chdir(INPUT_FOLDER)
    song = load_audio_file(filesToMegafy[counter])

    #Set pitch shift and its parameters
    if PITCH_SHIFT_CHOICE == True:
        tranposeValue = -5.0 #How much would you like your files tranposed (unit:semitones, type:float, syntax:positive means up negative means down, maxes:-12 to 12)                
        playback_processor = engine.make_playbackwarp_processor("my_playback", song)
        playback_processor.transpose = tranposeValue
        playback_processor.time_ratio = 2**(-tranposeValue/12)
        OUR_GRAPH.append((playback_processor, []))
    else:
        playback_processor = engine.make_playback_processor("my_playback", song)
        OUR_GRAPH.append((playback_processor, []))

    #Set bass booster and its parameters
    if BASS_BOOST_CHOICE == True:
        customizeBassBoost = True #Would user like to customize the bass boost or load a plugin
        if customizeBassBoost == True:
            bass_boost = engine.make_plugin_processor("my_bass_boost", BASS_BOOST_PLUGIN)
            bass_boost.set_parameter(2, outputGain)  #Output gain (dB)
            bass_boost.set_parameter(3, frequency) #Freq. (Hz)
            bass_boost.set_parameter(4, boost)  #Boost (dB)
            bass_boost.set_parameter(5, mode)  #Mode (0.0==Classic, 0.5==Passive, 1.0==Combo)

            userInputAboutBassBoostConfigurations = True #Would use like to save configurations as a preset
            if userInputAboutBassBoostConfigurations == True:
                savePreset(BASS_BOOST_PRESETS, [outputGain, frequency, boost, mode])
        else:

            bassBoostPresetValues = loadPreset(BASS_BOOST_PRESETS)
            outputGain = float(bassBoostPresetValues[0])
            frequency = float(bassBoostPresetValues[1])
            boost = float(bassBoostPresetValues[2])
            mode = float(bassBoostPresetValues[3])

            #Set parameters within plugin
            bass_boost = engine.make_plugin_processor("my_bass_boost", BASS_BOOST_PLUGIN)
            bass_boost.set_parameter(2, outputGain) #Output gain (dB)
            bass_boost.set_parameter(3, frequency) #Freq. (Hz)
            bass_boost.set_parameter(4, boost) #Boost (dB)
            bass_boost.set_parameter(5, mode) #Mode (0.0==Classic, 0.5==Passive, 11.0==Combo)


    #Set reverb levels and its parameters
    if REVERB_CHOICE == True:
        customizeReverb = True #Would user like to customize the bass boost or load a plugin
        if customizeReverb == True:            
            reverb = engine.make_plugin_processor("my_reverb", REVERB_PLUGIN)
            reverb.set_parameter(0, wetLevel) #Reverb (0==Super Dry, 1==Super Wet)
            reverb.set_parameter(1, wide) #Wide (0.333333==Off, 0==Mono, 1==200%)
            reverb.set_parameter(2, highPass)    #High-pass (0==Off)
            reverb.set_parameter(3, lowPass)  #Low-pass (1==Off)

            userInputAboutReverbConfigurations = True #Would user like to save configurations as preset

            if userInputAboutReverbConfigurations == True:
                savePreset(REVERB_PRESETS, [wetLevel, wide, highPass, lowPass])
        else:
            reverbPresetValues = loadPreset(REVERB_PRESETS)
            
            #Set parameters within plugin
            wetLevel = float(reverbPresetValues[0])
            wide = float(reverbPresetValues[1])
            highPass = float(reverbPresetValues[2])
            lowPass = float(reverbPresetValues[3])

            reverb = engine.make_plugin_processor("my_reverb", REVERB_PLUGIN)
            reverb.set_parameter(0, wetLevel) #Reverb (0==Super Dry, 1==Super Wet)
            reverb.set_parameter(1, wide) #Wide (0.333333==Off, 0==Mono, 1==200%)
            reverb.set_parameter(2, highPass) #High-pass (0==Off)
            reverb.set_parameter(3, lowPass) #Low-pass (1==Off)

    #Set soft clipper and its parameters
    if SOFT_CLIPPER_CHOICE == True:
        customizeSoftClipper = True #Would use like to load preset or customize configurations
        if customizeSoftClipper == 'Y':
            soft_clipper = engine.make_plugin_processor("my_soft_clipper", SOFT_CLIPPER_PLUGIN)
            soft_clipper.set_parameter(0, threshold) #Threshold
            soft_clipper.set_parameter(1, inputGain) #Input gain
            soft_clipper.set_parameter(2, positiveSaturation) #Positive saturation
            soft_clipper.set_parameter(3, negativeSaturation) #Negative saturation
            soft_clipper.set_parameter(4, saturate) #Saturate (0.0==False, 1.0==True)

            userInputAboutSoftClipperConfigurations = True #Would user like to save configurations as preset
                
            if userInputAboutSoftClipperConfigurations == True:
                savePreset(SOFT_CLIPPER_PRESETS, [threshold, inputGain, positiveSaturation, negativeSaturation, saturate])

        else:
            softClipperPresetValues = loadPreset(SOFT_CLIPPER_PRESETS)

            threshold = float(softClipperPresetValues[0])
            inputGain = float(softClipperPresetValues[1])
            positiveSaturation = float(softClipperPresetValues[2])
            negativeSaturation = float(softClipperPresetValues[3])
            saturate = int(softClipperPresetValues[4])

            #Set parameters within plugin
            soft_clipper = engine.make_plugin_processor("my_soft_clipper", SOFT_CLIPPER_PLUGIN)
            soft_clipper.set_parameter(0, threshold) #Threshold (dB)
            soft_clipper.set_parameter(1, inputGain) #Input Gain
            soft_clipper.set_parameter(2, positiveSaturation) #Positive Saturation (dB)
            soft_clipper.set_parameter(3, negativeSaturation) #Negative Saturation
            soft_clipper.set_parameter(4, saturate)   #Saturate (0==Off, 1==On)

    #Load graph onto engine
    engine.load_graph(OUR_GRAPH)

    #Render clip
    chdir(INPUT_FOLDER)
    durationOfClip = AudioFileClip(filesToMegafy[counter])
    if ORDER[0] == 'w':
        durationOfClip = (durationOfClip.duration)*(2**(-tranposeValue/12))
    else:
        durationOfClip = durationOfClip.duration
    engine.render(durationOfClip)
        
    #Extract audio from engine
    audio = engine.get_audio()

    #Write audio to file
    chdir(OUTPUT_FOLDER)
    write('MEGAFY '+str(filesToMegafy[counter].upper())[:-4]+'.wav', SAMPLE_RATE, audio.transpose())