# -*- coding: utf-8 -*-
"""
Copyright 2009 iACT, universite de Montreal, Jean Piche, Olivier Belanger, Dominic Thibault

This file is part of Cecilia 4.

Cecilia 4 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cecilia 4 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cecilia 4.  If not, see <http://www.gnu.org/licenses/>.
"""
import wx
import sys, os, math
import CeciliaLib
from constants import *
from pyo import *
from API_interface import *

if sys.platform == "linux2": # ???
    sys.path.append("/usr/lib/python2.6/site-packages")

class CeciliaFilein:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        userInputs = CeciliaLib.getVar("userInputs")
        info = userInputs[name]
        self.table = SndTable(info['path'], start=info["off"+self.name])

    def sig(self):
        return self.table

class CeciliaSampler:
    def __init__(self, parent, name, user_pitch, user_amp):
        self.parent = parent
        self.name = name
        self.user_pitch = user_pitch
        self.user_amp = user_amp
        userInputs = CeciliaLib.getVar("userInputs")
        info = userInputs[name]
        totalTime = CeciliaLib.getVar("totalTime")
        chnls = CeciliaLib.getVar("nchnls")
        samplerList = CeciliaLib.getVar("userSamplers")
        for sampler in samplerList:
            if sampler.name == name:
                sinfo = sampler.getSamplerInfo()
                break
            
        graph_lines = {}
        for line in CeciliaLib.getVar("grapher").plotter.getData():
            if line.name.startswith(self.name):
                graph_lines[line.name] = line

        if 1:
            print info
            print sinfo
            print graph_lines
        
        paths = [slider.getPath() for slider in sampler.getSamplerSliders()]
        
        start_init, self.start_play, self.start_rec = sinfo['loopIn'][0], sinfo['loopIn'][1], sinfo['loopIn'][2]
        line = graph_lines[self.name+'start']
        curved = line.getCurved()
        if curved:
            self.start_table = CosTable()
        else:
            self.start_table = LinTable()
        if not self.start_play:
            self.start = SigTo(value=start_init, time=0.025, init=start_init)
        if self.start_rec:
            self.start_record = ControlRec(self.start, filename=paths[0], rate=1000, dur=totalTime).play()
        if self.start_play:
            data = line.getData()
            data = [tuple(x) for x in data]
            self.setGraph('start', data)
            self.start = TableRead(self.start_table, freq=1.0/totalTime).play()
        
        dur_init, self.dur_play, self.dur_rec = sinfo['loopOut'][0], sinfo['loopOut'][1], sinfo['loopOut'][2]
        line = graph_lines[self.name+'end']
        curved = line.getCurved()
        if curved:
            self.dur_table = CosTable()
        else:
            self.dur_table = LinTable()
        if not self.dur_play:
            self.dur = SigTo(value=dur_init, time=0.025, init=dur_init)
        if self.dur_rec:
            self.dur_record = ControlRec(self.dur, filename=paths[1], rate=1000, dur=totalTime).play()
        if self.dur_play:
            data = line.getData()
            data = [tuple(x) for x in data]
            self.setGraph('end', data)
            self.dur = TableRead(self.dur_table, freq=1.0/totalTime).play()
        
        xfade_init, self.xfade_play, self.xfade_rec = sinfo['loopX'][0], sinfo['loopX'][1], sinfo['loopX'][2]
        line = graph_lines[self.name+'xfade']
        curved = line.getCurved()
        if curved:
            self.xfade_table = CosTable()
        else:
            self.xfade_table = LinTable()
        if not self.xfade_play:
            self.xfade = SigTo(value=xfade_init, time=0.025, init=xfade_init)
        if self.xfade_rec:
            self.xfade_record = ControlRec(self.xfade, filename=paths[2], rate=1000, dur=totalTime).play()
        if self.xfade_play:
            data = line.getData()
            data = [tuple(x) for x in data]
            self.setGraph('xfade', data)
            self.xfade = TableRead(self.xfade_table, freq=1.0/totalTime).play()
       
        gain_init, self.gain_play, self.gain_rec = sinfo['gain'][0], sinfo['gain'][1], sinfo['gain'][2]
        line = graph_lines[self.name+'gain']
        curved = line.getCurved()
        if curved:
            self.gain_table = CosTable()
        else:
            self.gain_table = LinTable()
        if not self.gain_play:
            self.gain_in = SigTo(value=gain_init, time=0.025, init=gain_init)
        if self.gain_rec:
            self.gain_record = ControlRec(self.gain_in, filename=paths[3], rate=1000, dur=totalTime).play()
        if self.gain_play:
            data = line.getData()
            data = [tuple(x) for x in data]
            self.setGraph('gain', data)
            self.gain_in = TableRead(self.gain_table, freq=1.0/totalTime).play()
        self.gain = Pow(10, self.gain_in * 0.05)
        
        pitch_init, self.pitch_play, self.pitch_rec = sinfo['transp'][0], sinfo['transp'][1], sinfo['transp'][2]
        line = graph_lines[self.name+'trans']
        curved = line.getCurved()
        if curved:
            self.pitch_table = CosTable()
        else:
            self.pitch_table = LinTable()
        if not self.pitch_play:
            self.pitch_in = SigTo(value=pitch_init, time=0.025, init=pitch_init)
        if self.pitch_rec:
            self.pitch_record = ControlRec(self.pitch_in, filename=paths[4], rate=1000, dur=totalTime).play()
        if self.pitch_play:
            data = line.getData()
            data = [tuple(x) for x in data]
            self.setGraph('trans', data)
            self.pitch_in = TableRead(self.pitch_table, freq=1.0/totalTime).play()
        self.pitch = Pow(1.0594630943593, self.pitch_in)
    
        self.table = SndTable(info['path'], start=info["off"+self.name])
        if self.parent.number_of_voices > 1:
            self.pitch_rnd = [random.uniform(1.0-self.parent.polyphony_spread, 
                    1.0+self.parent.polyphony_spread) for i in range(self.parent.number_of_voices*len(self.table))]
        else:
            self.pitch_rnd = 1.0
        self.looper = Looper( table=self.table,
                                    pitch=self.pitch*self.pitch_rnd,
                                    start=self.start,
                                    dur=self.dur,
                                    xfade=self.xfade,
                                    mode=sinfo['loopMode'],
                                    xfadeshape=sinfo['xfadeshape'],
                                    startfromloop=sinfo['startFromLoop'],
                                    interp=4,
                                    autosmooth=True,
                                    mul=self.gain)
        self.mix = Mix(self.looper, voices=chnls)

    def setGraph(self, which, func):
        totalTime = CeciliaLib.getVar("totalTime")
        func = [(int(x/float(totalTime)*8192), y) for x, y in func]
        if which.endswith('start'):
            self.start_table.replace(func)
        elif which.endswith('end'):
            self.dur_table.replace(func)
        elif which.endswith('xfade'):
            self.xfade_table.replace(func)
        elif which.endswith('gain'):
            self.gain_table.replace(func)
        elif which.endswith('trans'):
            self.pitch_table.replace(func)
    
    def checkForAutomation(self):
        if self.start_rec:
            self.start_record.write()
        if self.dur_rec:
            self.dur_record.write()
        if self.xfade_rec:
            self.xfade_record.write()
        if self.gain_rec:
            self.gain_record.write()
        if self.pitch_rec:
            self.pitch_record.write()

    def sig(self):
        return self.mix
    
    def setSound(self, snd):
        self.table.setSound(snd)
    
    def setStart(self, x):
        if not self.start_play:
            self.start.value = x
    
    def setDur(self, x):
        if not self.dur_play:
            self.dur.value = x
    
    def setXfade(self, x):
        if not self.xfade_play:
            self.xfade.value = x
    
    def setGain(self, x):
        if not self.gain_play:
            self.gain_in.value = x
    
    def setPitch(self, x):
        if not self.pitch_play:
            self.pitch_in.value = x

    def setLoopMode(self, x):
        self.looper.mode = x
    
    def setXfadeShape(self, x):
        self.looper.xfadeshape = x

class CeciliaSlider:
    def __init__(self, dic):
        self.type = "slider"
        self.name = dic["name"]
        init = dic["init"]
        gliss = dic["gliss"]
        totalTime = CeciliaLib.getVar("totalTime")

        for line in CeciliaLib.getVar("grapher").plotter.getData():
            if line.name == self.name:
                break
        
        self.widget = line.slider
        self.play = self.widget.getPlay()
        self.rec = self.widget.getRec()
        if 0:
            print self.widget, self.play, self.rec
        
        curved = line.getCurved()
        if curved:
            self.table = CosTable()
        else:
            self.table = LinTable()
        self.slider = SigTo(init, time=gliss, init=init)
        if self.rec:
            self.record = ControlRec(self.slider, filename=self.widget.getPath(), rate=1000, dur=totalTime).play()
        if self.play > 0:
            data = line.getData()
            data = [tuple(x) for x in data]
            self.setGraph(data)
            self.reader = TableRead(self.table, freq=1.0/totalTime).play()
    
    def sig(self):
        if self.play == 0:
            return self.slider
        else:
            return self.reader

    def setValue(self, x):
        self.slider.value = x

    def setGraph(self, func):
        totalTime = CeciliaLib.getVar("totalTime")
        func = [(int(x/float(totalTime)*8192), y) for x, y in func]
        self.table.replace(func)

    def updateWidget(self):
        self.widget.setValue(self.reader.get())

class CeciliaRange:
    def __init__(self, dic):
        self.type = "range"
        self.name = dic["name"]
        init = dic["init"]
        gliss = dic["gliss"]
        totalTime = CeciliaLib.getVar("totalTime")

        self.graph_lines = [None, None]
        for line in CeciliaLib.getVar("grapher").plotter.getData():
            if self.name in line.name:
                if line.suffix == "min":
                    self.graph_lines[0] = line
                elif line.suffix == "max":
                    self.graph_lines[1] = line

        self.widget = self.graph_lines[0].slider
        self.play = self.widget.getPlay()
        self.rec = self.widget.getRec()
        if 0:
            print self.widget, self.play, self.rec

        curved = [line.getCurved() for line in self.graph_lines]
        if curved[0]:
            self.table_min = CosTable()
        else:
            self.table_min = LinTable()
        if curved[1]:
            self.table_max = CosTable()
        else:
            self.table_max = LinTable()

        self.slider = SigTo(init, time=gliss, init=init)
        if self.rec:
            self.record = ControlRec(self.slider, filename=self.widget.getPath(), rate=1000, dur=totalTime).play()
        if self.play > 0:
            data = self.graph_lines[0].getData()
            data = [tuple(x) for x in data]
            self.setGraph(0, data)
            self.reader_min = TableRead(self.table_min, freq=1.0/totalTime).play()
            data = self.graph_lines[1].getData()
            data = [tuple(x) for x in data]
            self.setGraph(1, data)
            self.reader_max = TableRead(self.table_max, freq=1.0/totalTime).play()
            self.reader = Mix([self.reader_min, self.reader_max], voices=2)

    def sig(self):
        if self.play == 0:
            return self.slider
        else:
            return self.reader

    def setValue(self, x):
        self.slider.value = x

    def setGraph(self, which, func):
        totalTime = CeciliaLib.getVar("totalTime")
        func = [(int(x/float(totalTime)*8192), y) for x, y in func]
        if which == 0:
            self.table_min.replace(func)
        else:
            self.table_max.replace(func)

    def updateWidget(self):
        self.widget.setValue(self.reader.get(all=True))

class CeciliaGraph:
    def __init__(self, dic):
        self.name = dic["name"]
        self.isTable = dic["table"]
        self.size = dic["size"]
        totalTime = CeciliaLib.getVar("totalTime")
        func = [(int(x/float(totalTime)*self.size), y) for x, y in dic["func"]]
        for line in CeciliaLib.getVar("grapher").plotter.getData():
            if line.name == self.name:
                break
        curved = line.getCurved()
        if curved:
            self.table = CosTable(func)
        else:
            self.table = LinTable(func)
        if not self.isTable:
            self.reader = TableRead(self.table, freq=1.0/totalTime).play()

    def sig(self):
        if self.isTable:
            return self.table
        else:
            return self.reader

    def setValue(self, func):
        totalTime = CeciliaLib.getVar("totalTime")
        func = [(int(x/float(totalTime)*self.size), y) for x, y in func]
        self.table.replace(func)

class BaseModule:
    def __init__(self):
        self.fileins = {}
        self.samplers = {}
        self.sliders = {}
        self.toggles = {}
        self.popups = {}
        self.buttons = {}
        self.gens = {}
        self.graphs = {}
        self.polyphony = None
        totalTime = CeciliaLib.getVar("totalTime")
        interfaceWidgets = CeciliaLib.getVar("interfaceWidgets")
        for widget in interfaceWidgets:
            if widget['type'] == "cslider":
                self.addSlider(widget)
            elif widget['type'] == "crange":
                self.addRange(widget)
            elif widget['type'] == "cgraph":
                self.addGraph(widget)
            elif widget['type'] == "ctoggle":
                self.toggles[widget["name"]] = widget
            elif widget['type'] == "cpopup":
                self.popups[widget["name"]] = widget
            elif widget['type'] == "cbutton":
                self.buttons[widget["name"]] = widget
            elif widget['type'] == "cgen":
                self.gens[widget["name"]] = widget
            elif widget['type'] == "cpoly" and self.polyphony == None:
                self.polyphony = widget

        userTogglePopups = CeciliaLib.getVar("userTogglePopups")
        polyname = "noPolyphonyWidget"
        self.number_of_voices = 1
        self.polyphony_spread = 0.0
        if self.polyphony != None:
            polyname = self.polyphony["name"]
        for togPop in userTogglePopups:
            if togPop.name.startswith(polyname):
                if togPop.name.endswith("num"):
                    self.number_of_voices = togPop.getValue() + 1
                else:
                    self.polyphony_spread = togPop.getValue()

        self._metro = Metro(.06).play(dur=totalTime)
        self._updater = TrigFunc(self._metro, self.update).play(dur=totalTime)

    def checkForAutomation(self):
        for sampler in self.samplers.values():
            sampler.checkForAutomation()
        for slider in self.sliders.values():
            if slider.rec:
                slider.record.write()

    def update(self):
        for slider in self.sliders.values():
            if slider.play == 1:
                slider.updateWidget()

    def setWidgetValues(self):
        # graph lines
        for line in CeciliaLib.getVar("grapher").plotter.getData():
            name = line.getName()
            if name in self.graphs.keys():
                data = line.getData()
                self.graphs[name].setValue(data)
        # sliders
        for slider in CeciliaLib.getVar("userSliders"):
            name = slider.getName()
            self.sliders[name].setValue(slider.getValue())
        # toggles and popups
        for togPop in CeciliaLib.getVar("userTogglePopups"):
            name = togPop.getName()
            if name in self.toggles:
                getattr(self, name)(togPop.getValue())
            elif name in self.popups:
                index, label = togPop.getFullValue()
                getattr(self, name)(index, label)
            elif name in self.gens:
                getattr(self, name)(togPop.getValue())
        
    def addFilein(self, name):
        self.fileins[name] = CeciliaFilein(self, name)
        return self.fileins[name].sig()

    def addSampler(self, name, pitch=1, amp=1):
        self.samplers[name] = CeciliaSampler(self, name, pitch, amp)
        return self.samplers[name].sig()

    def addSlider(self, dic):
        self.sliders[dic["name"]] = CeciliaSlider(dic)
        setattr(self, dic["name"], self.sliders[dic["name"]].sig())

    def addRange(self, dic):
        self.sliders[dic["name"]] = CeciliaRange(dic)
        setattr(self, dic["name"], self.sliders[dic["name"]].sig())

    def addGraph(self, dic):
        self.graphs[dic["name"]] = CeciliaGraph(dic)
        setattr(self, dic["name"], self.graphs[dic["name"]].sig())

class DefaultModule(BaseModule):
    def __init__(self):
        BaseModule.__init__(self)
        self.out = self.addSampler("snd")

class CeciliaPlugin:
    def __init__(self, input, params=None):
        self.input = Sig(input)
        if params == None:
            self._p1 = SigTo(0, time=0.025)
            self._p2 = SigTo(0, time=0.025)
            self._p3 = SigTo(0, time=0.025)
        else:
            self._p1 = SigTo(params[0], time=0.025, init=params[0])
            self._p2 = SigTo(params[1], time=0.025, init=params[1])
            self._p3 = SigTo(params[2], time=0.025, init=params[2])
            self.preset = params[3]

    def setInput(self, input):
        self.input.value = input

    def stopControls(self):
        self._p1.stop()
        self._p2.stop()
        self._p3.stop()

    def startControls(self):
        self._p1.play()
        self._p2.play()
        self._p3.play()

    def setValue(self, which, x):
        if which == 0:
            self._p1.value = x
        elif which == 1:
            self._p2.value = x
        elif which == 2:
            self._p3.value = x

class CeciliaNonePlugin(CeciliaPlugin):
    def __init__(self, input):
        CeciliaPlugin.__init__(self, input)
        self.out = self.input
        self.stopControls()

class CeciliaReverbPlugin(CeciliaPlugin):
    def __init__(self, input, params):
        CeciliaPlugin.__init__(self, input, params)
        self.out = Freeverb(self.input, size=self._p2/10.0, damp=self._p3, bal=self._p1*self.preset)

    def setPreset(self, x, label):
        self.preset = x
        self.out.bal = self._p1 * self.preset

class AudioServer():
    def __init__(self):
        sr, bufsize, nchnls, duplex, host = self.getPrefs()
        if CeciliaLib.getVar("DEBUG"):
            print "AUDIO CONFIG:\nsr: %s, buffer size: %s, num of channels: %s, duplex: %s, host: %s" % (sr, bufsize, nchnls, duplex, host)
        self.server = Server(sr=sr, buffersize=bufsize, nchnls=nchnls, duplex=duplex, audio=host)
        self.server.verbosity = 15
        self.boot()
        self.setTimeCallable()
        self.plugins = [None, None, None]
        self.plugin1 = CeciliaNonePlugin(0)
        self.plugin2 = CeciliaNonePlugin(0)
        self.plugin3 = CeciliaNonePlugin(0)
        self.pluginDict = {"Reverb": CeciliaReverbPlugin}

    def getPrefs(self):
        sr = CeciliaLib.getVar("sr")
        bufsize = CeciliaLib.getVar("bufferSize")
        nchnls = CeciliaLib.getVar("nchnls")
        duplex = CeciliaLib.getVar("enableAudioInput")
        host = CeciliaLib.getVar("audioHostAPI")
        return sr, bufsize, nchnls, duplex, host

    def start(self, timer=True):
        if timer:
            self.endcall = CallAfter(function=CeciliaLib.stopCeciliaSound, time=CeciliaLib.getVar("totalTime"))
        self.server.start()

    def stop(self):
        self.server.stop()

    def shutdown(self):
        self.server.shutdown()

    def boot(self):
        sr, bufsize, nchnls, duplex, host = self.getPrefs()
        self.server.setSamplingRate(sr)
        self.server.setBufferSize(bufsize)
        self.server.setNchnls(nchnls)
        self.server.setDuplex(duplex)
        self.server.boot()

    def reinit(self):
        if CeciliaLib.getVar("outputFile") == 'dac':
            sr, bufsize, nchnls, duplex, host = self.getPrefs()
            self.server.reinit(audio=host)
        else:
            self.server.reinit(audio="offline")
            dur = CeciliaLib.getVar("totalTime")
            filename = CeciliaLib.getVar("outputFile")
            fileformat = {"wav": 0, "aiff": 1}[CeciliaLib.getVar("audioFileType")]
            sampletype = CeciliaLib.getVar("sampSize")
            self.server.recordOptions(dur=dur, filename=filename, fileformat=fileformat, sampletype=sampletype)

    def setAmpCallable(self, callable):
        self.server._server.setAmpCallable(callable)

    def setTimeCallable(self):
        self.server._server.setTimeCallable(self)

    def setTime(self, *args):
        if len(args) >= 4:
            time = args[1]*60 + args[2] + args[3]*0.001
            CeciliaLib.getVar("grapher").cursorPanel.setTime(time)
            CeciliaLib.getVar("interface").controlPanel.setTime(time, args[1], args[2], args[3]/10)
        else:
            CeciliaLib.getVar("grapher").cursorPanel.setTime(0)
            CeciliaLib.getVar("interface").controlPanel.setTime(0, 0, 0, 0)

    def recstart(self):
        self.server.recstart()

    def recstop(self):
        self.server.recstop()

    def setAmp(self, x):
        amp = math.pow(10.0, x * 0.05)
        self.server.amp = amp

    def setOutputDevice(self, device):
        self.server.setOutputDevice(device)

    def setMidiInputDevice(self, device):
        self.server.setMidiInputDevice(device)

    def setSamplingRate(self, sr):
        self.server.setSamplingRate(sr)

    def recordOptions(self, dur, filename, fileformat, sampletype):
        self.server.recordOptions(dur=dur, filename=filename, fileformat=fileformat, sampletype=sampletype)
    
    def isAudioServerRunning(self):
        if self.server.getIsStarted():
            return True
        else:
            return False

    def openCecFile(self, filepath):
        execfile(filepath, globals())
        CeciliaLib.setVar("currentModuleRef", Module)
        CeciliaLib.setVar("interfaceWidgets", Interface)
        CeciliaLib.getVar("mainFrame").onUpdateInterface(None)

    def loadModule(self, module=DefaultModule):
        self.currentModule = module()
        self.out = self.currentModule.out
        self.plugins = CeciliaLib.getVar("plugins")
        print self.plugins
        if self.plugins[0] == None:
            del self.plugin1
            self.plugin1 = CeciliaNonePlugin(self.out)
        else:
            pl = self.plugins[0]
            name = pl.getName()
            print "Plugin Name :", name
            params = pl.getParams()
            print "Values :", params
            states = pl.getStates()
            print "States :", states
            knobs = pl.getKnobs()
            print "Knobs :", knobs
            del self.plugin1
            self.plugin1 = self.pluginDict[name](self.out, params)
        if self.plugins[1] == None:
            del self.plugin2
            self.plugin2 = CeciliaNonePlugin(self.plugin1.out)
        if self.plugins[2] == None:
            del self.plugin3
            self.plugin3 = CeciliaNonePlugin(self.plugin2.out)
        self.plugin3.out.out()
        CeciliaLib.setVar("currentModule", self.currentModule)
        self.currentModule.setWidgetValues()

    def setPluginValue(self, order, which, x):
        pl = self.plugins[order]
        if pl != None:
            if order == 0:
                self.plugin1.setValue(which, x)
            elif order == 1:
                self.plugin2.setValue(which, x)
            elif order == 2:
                self.plugin3.setValue(which, x)

    def setPluginPreset(self, order, x, label):
        pl = self.plugins[order]
        if pl != None:
            if order == 0:
                self.plugin1.setPreset(x, label)
            elif order == 1:
                self.plugin2.setPreset(x, label)
            elif order == 2:
                self.plugin3.setPreset(x, label)

    def midiLearn(self, slider, rangeSlider=False):
        pass
    
    def getAvailableAudioMidiDrivers(self):
        inputDriverList, inputDriverIndexes = pa_get_input_devices()
        selectedInputDriver = inputDriverList[inputDriverIndexes.index(pa_get_default_input())]
        outputDriverList, outputDriverIndexes = pa_get_output_devices()
        selectedOutputDriver = outputDriverList[outputDriverIndexes.index(pa_get_default_output())]
        midiDriverList, midiDriverIndexes = pm_get_input_devices()
        if midiDriverList == []:
            selectedMidiDriver = ""
        else:
            selectedMidiDriver = midiDriverList[midiDriverIndexes.index(pm_get_default_input())]
        return inputDriverList, selectedInputDriver, outputDriverList, selectedOutputDriver, midiDriverList, selectedMidiDriver
    
    def getSoundInfo(self, path):
        """
        Retrieves information of the sound and prints it to the console.
    
        return (number of channels, sampling rate, duration, fraction of a table, length in samples, bitrate)
        """
        print '--------------------------------------'
        print path

        info = sndinfo(path)
                
        if info != None:
            samprate = info[2]
            chnls = info[3]
            nsamps = info[0]
            dur = info[1]
            bitrate = info[5]
            format = info[4]
            for i in range(24):
                size = math.pow(2,(i+1))
                if size > nsamps:
                    break
            tableFrac = nsamps / size
            
            print "channels = %d" % chnls
            print "sampling rate = %s" % samprate
            print "number of samples = %s" % nsamps
            print "duration in sec. = %s" % dur
            print "bitrate = %s" % bitrate
            print "file format = %s" % format

            return (chnls, samprate, dur, tableFrac, nsamps, bitrate, format)
        else:
            print "Unable to get sound infos..."
            return None

    def getSoundsFromList(self, pathList):
        soundDict = dict()
        for path in pathList:
            if os.path.isfile(path):
                infos = self.getSoundInfo(path)
                if infos != None:
                    sndfile = os.path.split(path)[1] 
                    if sndfile not in soundDict.keys():
                        soundDict[CeciliaLib.ensureNFD(sndfile)] = {'samprate': infos[1],
                                        'chnls': infos[0],
                                        'dur': infos[2],
                                        'bitrate': infos[5],
                                        'type': infos[6],
                                        'path': path}
            else:
                print 'not a file'
        return soundDict
        