# THIS FILE IS FUNCTIONAL BUT HIGHLY INEFFICIENT. IT IS CONTINUALLY UPDATED (ADDED FEATURES AND BETTER OPTIMISATION). MEGAFY WILL ALSO BE TURNED INTO A CLASS IN THE NEAR FUTURE.
# CURRENTLY, SCRIPT REQUIRES FOR MANUAL PATH INPUT. THIS IS TEMPORARY.

from librosa import load
from moviepy.editor import AudioFileClip
from os import chdir, walk, path, listdir
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
BASS_BOOST_CHOICE = True
SOFT_CLIPPER_CHOICE = True
PITCH_SHIFT_CHOICE = True
REVERB_CHOICE = True
CONFIGURATION_CHOICES_MADE = False

#Convert audio file to usable form for graph
def load_audio_file(file_path, duration=None):
    chdir(INPUT_FOLDER)
    sig, rate = load(file_path, duration=duration, mono=False, sr=SAMPLE_RATE)
    assert(rate == SAMPLE_RATE)
    return sig

def basicUserAsk(pluginName, effectName, effectUnits, effectLowEnd, effectHighEnd):
    while(1):
        try:
            userInput = float(input("["+pluginName.upper()+"] Please input a value for the "+pluginName+"'s '"+effectName+"' ["+effectUnits+"] (from "+effectLowEnd+" to "+effectHighEnd+"): "))
            if (userInput < float(effectLowEnd)) or (userInput > float(effectHighEnd)):
                print("["+pluginName.upper()+"] The value must be between "+effectLowEnd+" and "+effectHighEnd+"!")
            else:
                break
        except Exception:
            print("["+pluginName.upper()+"] Please input a number between "+effectLowEnd+" and "+effectHighEnd+"!")
        
    return float(userInput)

def binaryUserAsk(pluginName, effectName, effectLowEnd, effectHighEnd):
    while(1):
        try:
            userInput = int(input("["+pluginName.upper()+"] Please input a value for the "+pluginName+"'s '"+effectName+"' (either a "+effectLowEnd+" for 'No' or "+effectHighEnd+" for 'Yes'): "))
            if (userInput == int(effectLowEnd)) or (userInput == int(effectHighEnd)):
                break
            else:
                print("["+pluginName.upper()+"] The value must be either a "+effectLowEnd+" or "+effectHighEnd+"!")
        except Exception:
            print("["+pluginName.upper()+"] Input must be one of two numbers: "+effectLowEnd+" or "+effectHighEnd)
        
    return int(userInput)

def ternaryUserAsk(pluginName, effectName, effectLowEnd, effectMidEnd, effectHighEnd):
    while(1):
        try:
            userInput = float(input("["+pluginName.upper()+"] Please input a value for the "+pluginName+"'s '"+effectName+"' (either a "+effectLowEnd+" for 'Classic', "+effectMidEnd+" for 'Passive', or "+effectHighEnd+" for 'Combo'): "))
            if (userInput == float(effectLowEnd)) or (userInput == float(effectMidEnd)) or (userInput == float(effectHighEnd)):
                break
            else:
                print("["+pluginName.upper()+"] The value must be either a "+effectLowEnd+", "+effectMidEnd+", or "+effectHighEnd+"!")
        except Exception:
            print("["+pluginName.upper()+"] Input must be one of three numbers: "+effectLowEnd+", "+effectMidEnd+", or "+effectHighEnd)
        
    return float(userInput)

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

print("\n-------------------------- MEGAFY --------------------------\n")

#Get user basic choices
print("Type 'n' for No and any other key for Yes:")
pitchShiftInput = str(input("    Would you like your files pitch shifted? (will be slowed if lowered and sped up if highered): "))
bassBoostInput = str(input("    Would you like your files bass boosted?: "))
reverbInput = str(input("    Would you like to add reverb to your files?: "))
softClipperInput = str(input("    Would you like your files soft clipped? (HIGHLY SUGGESTED): "))
print("\nProcessing choices......")

#Set user basic choices
if (bassBoostInput == 'N') or (bassBoostInput == 'n'):
    BASS_BOOST_CHOICE = False
if (softClipperInput == 'N') or (softClipperInput == 'n'):
    SOFT_CLIPPER_CHOICE = False
if (pitchShiftInput == 'N') or (pitchShiftInput == 'n'):
    PITCH_SHIFT_CHOICE = False
if (reverbInput == 'N') or (reverbInput == 'n'):
    REVERB_CHOICE = False

#Get the files and set the engine
filesToMEGAFY = next(walk(INPUT_FOLDER), (None, None, []))[2]
engine = daw.RenderEngine(SAMPLE_RATE, BUFFER_SIZE)

#Customize all files in the input folder
for counter in range(len(filesToMEGAFY)):

    #Reset graph
    OUR_GRAPH = []

    #Other files sometime appear in the output folder for some reason (like a jpeg called "album art" but I cant see it?)
    chdir(INPUT_FOLDER)
    myExtension = path.splitext(filesToMEGAFY[counter])[1]
    if myExtension not in VALID_FILETYPES:
        continue

    #Get song
    chdir(INPUT_FOLDER)
    song = load_audio_file(filesToMEGAFY[counter])

    #Set pitch shift and its parameters
    if PITCH_SHIFT_CHOICE == True:
        ORDER = ORDER+'w'
        if CONFIGURATION_CHOICES_MADE == True:
            playback_processor = engine.make_playbackwarp_processor("my_playback", song)
            playback_processor.transpose = tranposeValue
            playback_processor.time_ratio = 2**(-tranposeValue/12)
            OUR_GRAPH.append((playback_processor, []))
        else:
            print("\n-------------------------- PITCH SHIFT -------------------------\n")
            while(1):
                try:
                    tranposeValue = float(input("[PITCH SHIFTING] How many semitones would you like to tranpose (Ex: Type '4' for raising 4 semitones or type '-6' to lower 6 semitones): "))
                    if (float(tranposeValue) > 12) or (float(tranposeValue) < -12):
                        print("[PITCH SHIFTING] The tranpose value must be a number between -12 and 12 (inclusive).")
                        continue
                    else:
                        break
                except ValueError:
                    print("[PITCH SHIFTING] The tranpose value must be a number between -12 and 12 (inclusive).")
                except Exception:
                    print("[PITCH SHIFTING] Yea you did something wrong there. Try again.")
                
            playback_processor = engine.make_playbackwarp_processor("my_playback", song)
            playback_processor.transpose = tranposeValue
            playback_processor.time_ratio = 2**(-tranposeValue/12)
            OUR_GRAPH.append((playback_processor, []))
    else:
        ORDER = ORDER+'p'
        playback_processor = engine.make_playback_processor("my_playback", song)
        OUR_GRAPH.append((playback_processor, []))

    #Set bass booster and its parameters
    if BASS_BOOST_CHOICE == True:
        if CONFIGURATION_CHOICES_MADE == True:
            bass_boost = engine.make_plugin_processor("my_bass_boost", BASS_BOOST_PLUGIN)
            bass_boost.set_parameter(2, outputGain)  #Output gain (dB)
            bass_boost.set_parameter(3, frequency) #Freq. (Hz)
            bass_boost.set_parameter(4, boost)  #Boost (dB)
            bass_boost.set_parameter(5, mode)  #Mode (0.0==Classic, 0.5==Passive, 1.0==Combo)
        else:
            print("\n------------------------- BASS BOOST -------------------------\n")
            customizeBassBoost = str(input("[BASS BOOST] Would you like to customize the effect (Type 'Y') or load a preset (Type any other key)?: "))
            if customizeBassBoost == 'Y':

                outputGain = basicUserAsk('Bass Boost', 'Output Gain', 'dB', '0.000', '1.000')
                frequency = basicUserAsk('Bass Boost', 'Frequency', 'Hz', '0.000', '1.000')
                boost = basicUserAsk('Bass Boost', 'Boost', 'dB', '0.000', '1.000')
                mode = ternaryUserAsk('Bass Boost', 'Mode', '0.0', '0.5', '1.0')

                bass_boost = engine.make_plugin_processor("my_bass_boost", BASS_BOOST_PLUGIN)
                bass_boost.set_parameter(2, outputGain)  #Output gain (dB)
                bass_boost.set_parameter(3, frequency) #Freq. (Hz)
                bass_boost.set_parameter(4, boost)  #Boost (dB)
                bass_boost.set_parameter(5, mode)  #Mode (0.0==Classic, 0.5==Passive, 1.0==Combo)

                userInputAboutBassBoostConfigurations = str(input("Would you like to save these bass boost configurations as a preset for future use? (Input 'Y' for Yes and any other key for No): "))
                if userInputAboutBassBoostConfigurations == 'Y':
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
        
        if ORDER[-1] == 'p' or 'w':
            OUR_GRAPH.append((bass_boost, ["my_playback"]))
        ORDER = ORDER+'b'

    #Set reverb levels and its parameters
    if REVERB_CHOICE == True:
        if CONFIGURATION_CHOICES_MADE == True:
            reverb = engine.make_plugin_processor("my_reverb", REVERB_PLUGIN)
            reverb.set_parameter(0, wetLevel) #Reverb (0==Super Dry, 1==Super Wet)
            reverb.set_parameter(1, wide) #Wide (0.333333==Off, 0==Mono, 1==200%)
            reverb.set_parameter(2, highPass)    #High-pass (0==Off)
            reverb.set_parameter(3, lowPass)  #Low-pass (1==Off)
        else:
            print("\n---------------------------- REVERB ----------------------------\n")
            customizeReverb = str(input("[REVERB] Would you like to customize the effect (Type 'Y') or load a preset (Type any other key)?: "))
            if customizeReverb == 'Y':
                wetLevel = basicUserAsk('Reverb', 'Wet/Dry Level', 'dB', '0.000', '1.000')
                wide = basicUserAsk('Reverb', 'Wide', '%', '0.000', '1.000')
                highPass = basicUserAsk('Reverb', 'High Pass', 'Hz', '0.000', '1.000')
                lowPass = basicUserAsk('Reverb', 'Low Pass', 'Hz', '0.000', '1.000') 
                
                reverb = engine.make_plugin_processor("my_reverb", REVERB_PLUGIN)
                reverb.set_parameter(0, wetLevel) #Reverb (0==Super Dry, 1==Super Wet)
                reverb.set_parameter(1, wide) #Wide (0.333333==Off, 0==Mono, 1==200%)
                reverb.set_parameter(2, highPass)    #High-pass (0==Off)
                reverb.set_parameter(3, lowPass)  #Low-pass (1==Off)

                userInputAboutBassBoostConfigurations = str(input("Would you like to save these bass boost configurations as a preset for future use? (Input 'Y' for Yes and any other key for No): "))

                if userInputAboutBassBoostConfigurations == 'Y':
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

        if ORDER[-1] == 'p' or 'w':
            OUR_GRAPH.append((reverb, ["my_playback"]))
        if ORDER[-1] == 'b':
            OUR_GRAPH.append((reverb, ["my_bass_boost"]))
        ORDER = ORDER+'r'

    #Set soft clipper and its parameters
    if SOFT_CLIPPER_CHOICE == True:
        if CONFIGURATION_CHOICES_MADE == True:
            soft_clipper = engine.make_plugin_processor("my_soft_clipper", SOFT_CLIPPER_PLUGIN)
            soft_clipper.set_parameter(0, threshold) #Threshold
            soft_clipper.set_parameter(1, inputGain) #Input gain
            soft_clipper.set_parameter(2, positiveSaturation) #Positive saturation
            soft_clipper.set_parameter(3, negativeSaturation) #Negative saturation
            soft_clipper.set_parameter(4, saturate) #Saturate (0.0==False, 1.0==True)
        else:
            print("\n------------------------- SOFT CLIPPER -------------------------\n")
            customizeSoftClipper = str(input("[SOFT CLIPPER] Would you like to customize the effect (Type 'Y') or load a preset (Type any other key)?: "))
            if customizeSoftClipper == 'Y':
                threshold = basicUserAsk('Soft Clipper', 'Threshold', 'dB', '0.000', '1.000')
                inputGain = basicUserAsk('Soft Clipper', 'Input Gain', 'dB', '0.000', '1.000')
                positiveSaturation = basicUserAsk('Soft Clipper', 'Positive Saturation', 'dB', '0.000', '1.000')
                negativeSaturation = basicUserAsk('Soft Clipper', 'Negative Saturation', 'dB', '0.000', '1.000')
                saturate = binaryUserAsk('Soft Clipper', 'Saturate', '0', '1')

                soft_clipper = engine.make_plugin_processor("my_soft_clipper", SOFT_CLIPPER_PLUGIN)
                soft_clipper.set_parameter(0, threshold) #Threshold
                soft_clipper.set_parameter(1, inputGain) #Input gain
                soft_clipper.set_parameter(2, positiveSaturation) #Positive saturation
                soft_clipper.set_parameter(3, negativeSaturation) #Negative saturation
                soft_clipper.set_parameter(4, saturate) #Saturate (0.0==False, 1.0==True)

                userInputAboutSoftClipperConfigurations = str(input("Would you like to save these soft clipper configurations as a preset for future use? (Input 'Y' for Yes and any other key for No): "))
                    
                if userInputAboutSoftClipperConfigurations == 'Y':
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

        if ORDER[-1] == 'p' or 'w':
            OUR_GRAPH.append((soft_clipper, ["my_playback"]))
        if ORDER[-1] == 'b':
            OUR_GRAPH.append((soft_clipper, ["my_bass_boost"]))
        if ORDER[-1] == 'r':
            OUR_GRAPH.append((soft_clipper, ["my_reverb"]))
        ORDER = ORDER+'s'
    
    if counter == 0:
        print("\n---------------------- MEGAFYING FILES ----------------------\n")
    else:
        print('\n')

    CONFIGURATION_CHOICES_MADE = True

    #Load graph onto engine
    engine.load_graph(OUR_GRAPH)

    #Render clip
    chdir(INPUT_FOLDER)
    durationOfClip = AudioFileClip(filesToMEGAFY[counter])
    if ORDER[0] == 'w':
        durationOfClip = (durationOfClip.duration)*(2**(-tranposeValue/12))
    else:
        durationOfClip = durationOfClip.duration
    engine.render(durationOfClip)
        
    #Extract audio from engine
    audio = engine.get_audio()

    #Write audio to file
    chdir(OUTPUT_FOLDER)
    print((filesToMEGAFY[counter])[0:25]+'.... has been MEGAFIED.')
    write('MEGAFY '+str(filesToMEGAFY[counter].upper())[:-4]+'.wav', SAMPLE_RATE, audio.transpose())

print("\n------------------ FILES HAVE BEEN MEGAFIED -----------------\n")