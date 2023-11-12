

from OpenGL.GL import *
from OpenGL.GL.shaders import *
from imgui.integrations.glfw import GlfwRenderer

import glfw
import glm
import imgui

import numpy as np
import freetype as ft

import math
import random
import os
import time


class Index:
    SPECIFIC_PROGRAM_INFO_COLOR = 0
    SPECIFIC_PROGRAM_INFO_TEXT_POS = 1
    SPECIFIC_PROGRAM_INFO_TEXT_INTERVAL = 2
    SPECIFIC_PROGRAM_INFO_NUM_TEXTS = 3
    SPECIFIC_PROGRAM_INFO_FONT_SIZE = 4
    SPECIFIC_PROGRAM_INFO_TEXT_START = 5

    IMGUI_WINDOW_HIERARCHY = 0
    IMGUI_WINDOW_INSPECTOR = 1

    SHADER_DEFAULT = 0
    SHADER_SIMPLE_USE_UNIFORMCOLOR = 1
    SHADER_FRAGMENT_COORDINATE = 2
    SHADER_TEST = 100

    SHADER_VERTEX_CODE_DEFAULT = 2001    
    SHADER_VERTEX_CODE_TEST = 2901

    SHADER_FRAGMENT_CODE_DEFAULT = 2001
    SHADER_FRAGMENT_CODE_SIMPLE_USE_UNIFORMCOLOR = 2002
    SHADER_FRAGMENT_CODE_FRAGMENT_COORDINATE = 2003
    SHADER_FRAGMENT_CODE_TEST = 2901

class SceneManager:
    def __init__(self, view3D):
        self.displaySize = (1280, 720)

        self.screenSize = (680, 680)        
        self.screenPos = []

        self.imguiSize = []
        self.imguiPos = []

        self.imguiFont = None

        self.drawingStuffVerticesList = []
        self.drawingStuffIndicesList = []

        self.coordAxesVertices = []
        self.coordAxesIndices = []

        self.programInfoAreaVertices = []
        self.programInfoAreaIndices = []

        self.fovy = 45.0
        self.aspect = self.screenSize[0] / self.screenSize[1]
        self.near = 0.1
        self.far = 1000.0

        self.shaders = {}

        self.camera = None
        self.enableCameraMove = False
        self.enableCameraSailing = False
        self.cameraSailingSpeed = 1.0

        self.view3D = view3D
        self.drawAxes = True

        self.perspectivePrjMat = glm.perspective(self.fovy, self.aspect, self.near, self.far)
        self.orthoPrjMat = glm.ortho(0, self.screenSize[0], 0, self.screenSize[1], 1.0, 100.0)
        self.GUIPrjMat = glm.ortho(0, self.displaySize[0], 0, self.displaySize[1], 1.0, 100.0)

        self.view3DMat = glm.mat4()
        self.view2DMat = glm.translate(glm.vec3(0.0, 0.0, 20.0))
        self.view2DMat = glm.inverse(self.view2DMat)

        self.coordAxesViewMat = glm.mat4()

        self.modelMat = glm.mat4()        

        self.resourcePath = "../../../Resource/"

        self.objects = []        
        self.smallFont = None
        self.font = None
        self.largeFont = None

        self.deltaTime = 0.0
        self.dirty = True

        self.colors = {}

        self.programInfo = False
        self.numProgramInfoElement = 7

        self.specificProgramInfo = True
        self.specificProgramArgs = []

        self.controlFPS = False
        self.FPS = 30
        self.oneFrameTime = 1.0 / self.FPS
        self.deltaTime = 0.0
        self.elapsedTime = 0.0        
        self.enableRender = True

        self.pause = False
        self.debug = False
        self.debugMat = glm.mat4()

        self.logFile = None
        self.startLog = False

        self.numVertexComponents = 7
        self.numDrawingStuff = 2

        self.drawingStuffVAO = None
        self.drawingStuffVBO = None
        self.drawingStuffEBO = None
        
        self._Initialize()        

    def GetDisplaySize(self):
        return self.displaySize

    def SetDisplaySize(self, width, height):
        self.displaySize[0] = width
        self.displaySize[1] = height
        self.aspect = self.displaySize[0] / self.displaySize[1]

        self.dirty = True   

    def GetCamera(self):
        return self.camera

    def SetCamera(self, camera):
        self.camera = camera

        self.dirty = True

    def GetView3D(self):
        return self.view3D

    def SetView3D(self, view3D):
        self.view3D = view3D

        if self.view3D == False:
            self.drawAxes = False

    def GetEnableCameraMove(self):
        return self.enableCameraMove

    def SetEnableCameraMove(self, enableCameraMove):
        self.enableCameraMove = enableCameraMove

        if self.enableCameraMove == False:
            self.enableCameraSailing = False

    def GetPerspectivePrjMat(self):
        return self.perspectivePrjMat

    def GetOrthoPrjMat(self):
        return self.orthoPrjMat        

    def GetGUIPrjMat(self):
        return self.GUIPrjMat

    def GetView3DMat(self):
        self.view3DMat = self.camera.GetViewMat()
        return self.view3DMat

    def GetView2DMat(self):
        return self.view2DMat

    def GetPause(self):
        return self.pause

    def GetDebug(self):
        return self.debug

    def GetColor(self, key, index):
        completedKey = key + str(index)
        return self.colors[completedKey]

    def GetShader(self, index):
        return self.shaders[index]

    def GetScreenSize(self):
        return self.screenSize

    def GetScreenPos(self):
        return self.screenPos

    def GetImguiSize(self, index):
        return self.imguiSize[index]

    def GetImguiPos(self, index):
        return self.imguiPos[index]

    def GetImguiFont(self):
        return self.imguiFont 
    
    def GetResourcePath(self):
        return self.resourcePath

    def SetDirty(self, value):
        self.dirty = value

    def SetCameraPos(self):
        cameraSpeed = 0.0

        if self.enableCameraSailing == True:
            cameraSpeed = self.cameraSailingSpeed
        else:
            cameraSpeed = 0.05

        if gInputManager.GetKeyState(glfw.KEY_W) == True:
            self.camera.ProcessKeyboard('FORWARD', cameraSpeed)
            self.dirty = True
        if gInputManager.GetKeyState(glfw.KEY_S) == True:
            self.camera.ProcessKeyboard('BACKWARD', cameraSpeed)
            self.dirty = True
        if gInputManager.GetKeyState(glfw.KEY_A) == True:
            self.camera.ProcessKeyboard('LEFT', cameraSpeed)
            self.dirty = True
        if gInputManager.GetKeyState(glfw.KEY_D) == True:
            self.camera.ProcessKeyboard('RIGHT', cameraSpeed)
            self.dirty = True 
        if gInputManager.GetKeyState(glfw.KEY_E) == True:
            self.camera.ProcessKeyboard('UPWARD', cameraSpeed)
            self.dirty = True
        if gInputManager.GetKeyState(glfw.KEY_Q) == True:
            self.camera.ProcessKeyboard('DOWNWARD', cameraSpeed)
            self.dirty = True     

    def SetSpecificProgramArgs(self, index, subIndex, value):        
        argsList = list(self.specificProgramArgs[index])

        argsList[subIndex] = value     

        self.specificProgramArgs[index] = tuple(argsList)

    def InitializeOpenGL(self, shaders):
        self.shaders = shaders

        for key, value in self.shaders.items():
            self.shaders[key].Use()
            self.shaders[key].SetVec2i('resolution', self.screenSize[0], self.screenSize[1])
            self.shaders[key].SetVec2i('screenLBPos', self.screenPos[0][0], self.screenPos[0][1])

        color = self.GetColor('DefaultColor_', 1)
        glClearColor(color[0], color[1], color[2], 1.0)

        glEnable(GL_DEPTH_TEST)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self.drawingStuffVAO = glGenVertexArrays(self.numDrawingStuff)
        self.drawingStuffVBO = glGenBuffers(self.numDrawingStuff)
        self.drawingStuffEBO = glGenBuffers(self.numDrawingStuff)

        for i in range(self.numDrawingStuff):
            glBindVertexArray(self.drawingStuffVAO[i])

            glBindBuffer(GL_ARRAY_BUFFER, self.drawingStuffVBO[i])
            glBufferData(GL_ARRAY_BUFFER, self.drawingStuffVerticesList[i].nbytes, self.drawingStuffVerticesList[i], GL_STATIC_DRAW)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.drawingStuffEBO[i])
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.drawingStuffIndicesList[i].nbytes, self.drawingStuffIndicesList[i], GL_STATIC_DRAW)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.drawingStuffVerticesList[i].itemsize * self.numVertexComponents, ctypes.c_void_p(0))

            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, self.drawingStuffVerticesList[i].itemsize * self.numVertexComponents, ctypes.c_void_p(self.drawingStuffVerticesList[i].itemsize * 3))

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)        

        #self.debugMat = glGetFloatv(GL_MODELVIEW_MATRIX)
        #cullFaceMode =  glGetIntegerv(GL_CULL_FACE_MODE)

    def MakeFont(self, imguiFont, fontPath = None):
        if fontPath == None:
            self.smallFont = Font(self.resourcePath + 'Font/comic.ttf', 10)
            self.font = Font(self.resourcePath + 'Font/comic.ttf', 14)
            self.largeFont = Font(self.resourcePath + 'Font/comic.ttf', 21)            

            self.smallFont.MakeFontTextureWithGenList()
            self.font.MakeFontTextureWithGenList()
            self.largeFont.MakeFontTextureWithGenList()

        self.imguiFont = imguiFont

    def AddObject(self, object):
        self.objects.append(object)        
        
    def AddSpecificProgramArgs(self, *args):
        self.specificProgramArgs.append(args)

    def ClearSpecificProgramArgs(self):
        self.specificProgramArgs.clear()

    def WriteLog(self, text):
        self.logFile.write('[' + time.strftime('%Y.%m.%d : %H.%M.%S') + ']' + ' ')
        self.logFile.write(text)
        self.logFile.write('\n')

        self.logFile.flush()

    def UpdateAboutKeyInput(self):
        numObjects = len(self.objects)

        if gInputManager.GetKeyState(glfw.KEY_SPACE) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_SPACE)
            gInputManager.SetKeyState(glfw.KEY_SPACE, False)    

        elif gInputManager.GetKeyState(glfw.KEY_1) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_1)            
            gInputManager.SetKeyState(glfw.KEY_1, False)
        elif gInputManager.GetKeyState(glfw.KEY_2) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_2)
            gInputManager.SetKeyState(glfw.KEY_2, False)
        elif gInputManager.GetKeyState(glfw.KEY_3) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_3)
            gInputManager.SetKeyState(glfw.KEY_3, False)
        elif gInputManager.GetKeyState(glfw.KEY_4) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_4)
            gInputManager.SetKeyState(glfw.KEY_4, False)
        elif gInputManager.GetKeyState(glfw.KEY_5) == True:
            self.cameraSailingSpeed -= 0.1
            if self.cameraSailingSpeed < 0.1:
                self.cameraSailingSpeed = 0.1
            gInputManager.SetKeyState(glfw.KEY_5, False)
        elif gInputManager.GetKeyState(glfw.KEY_6) == True:
            self.cameraSailingSpeed += 0.1
            if self.cameraSailingSpeed > 1.0:
                self.cameraSailingSpeed = 1.0
            gInputManager.SetKeyState(glfw.KEY_6, False)

        elif gInputManager.GetKeyState(glfw.KEY_B) == True:
            self.debug = not self.debug
            self._InitializeLog()
            gInputManager.SetKeyState(glfw.KEY_B, False)        
        elif gInputManager.GetKeyState(glfw.KEY_F) == True:
            self.specificProgramInfo = not self.specificProgramInfo
            gInputManager.SetKeyState(glfw.KEY_F, False)        
        elif gInputManager.GetKeyState(glfw.KEY_I) == True:
            self.programInfo = not self.programInfo                
            gInputManager.SetKeyState(glfw.KEY_I, False)
        elif gInputManager.GetKeyState(glfw.KEY_L) == True:
            self.enableCameraSailing = not self.enableCameraSailing
            if self.enableCameraMove == False:
                self.enableCameraSailing = False
            gInputManager.SetKeyState(glfw.KEY_L, False)
        elif gInputManager.GetKeyState(glfw.KEY_P) == True:
            self.pause = not self.pause
            gInputManager.SetMouseEntered(False)
            gInputManager.SetKeyState(glfw.KEY_P, False)
        elif gInputManager.GetKeyState(glfw.KEY_R) == True:
            for i in range(numObjects):
                self.objects[i].Restart()
            gInputManager.SetKeyState(glfw.KEY_R, False)
        elif gInputManager.GetKeyState(glfw.KEY_V) == True:
            self.view3D = not self.view3D
            for i in range(numObjects):
                self.objects[i].Restart()
            gInputManager.SetKeyState(glfw.KEY_V, False)
        elif gInputManager.GetKeyState(glfw.KEY_X) == True:
            self.drawAxes = not self.drawAxes
            if self.view3D == False:
                self.drawAxes = False
            gInputManager.SetKeyState(glfw.KEY_X, False)

        if gInputManager.GetKeyState(glfw.KEY_LEFT) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_LEFT)
        if gInputManager.GetKeyState(glfw.KEY_RIGHT) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_RIGHT)  
        if gInputManager.GetKeyState(glfw.KEY_UP) == True:            
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_UP)
        if gInputManager.GetKeyState(glfw.KEY_DOWN) == True:
            for i in range(numObjects):
                self.objects[i].UpdateAboutKeyInput(glfw.KEY_DOWN)            

    def UpdateAboutMouseInput(self):
        numObjects = len(self.objects)       

        if gInputManager.GetMouseButtonClick(glfw.MOUSE_BUTTON_LEFT) == True:
            lastMousePosOnClick = gInputManager.GetLastMousePosOnClick()
            for i in range(numObjects):
                self.objects[i].UpdateAboutMouseInput(glfw.MOUSE_BUTTON_LEFT, lastMousePosOnClick)
            
    def Update(self, deltaTime):
        self.deltaTime = deltaTime

        #if gSceneManager.GetDebug() == True:
        #    self.WriteLog('deltaTime : {0}'.format(self.deltaTime))        

        if self.controlFPS == True:
            self.elapsedTime += self.deltaTime

            if self.elapsedTime < self.oneFrameTime:                
                return        
        
        self.enableRender = True        

        self.UpdateAboutKeyInput()

        self.UpdateAboutMouseInput()

        if self.view3D == True and self.enableCameraMove:
            self.SetCameraPos()            

        if self.pause == True:
            return

        numObjects = len(self.objects)

        for i in range(numObjects):
            if self.controlFPS == True:
                self.objects[i].Update(self.elapsedTime)
            else:
                self.objects[i].Update(deltaTime)        

        if self.dirty == False:
            return  

        self.view3DMat = self.camera.GetViewMat()
        self.coordAxesViewMat = self.camera.GetViewMat()
        
        self.dirty = False        

    def PostUpdate(self, deltaTime):    
        if gInputManager.GetKeyState(glfw.KEY_8) == True:
            if self.controlFPS == True:
                self.FPS -= 5
                if self.FPS <= 0:
                    self.FPS = 1

                self.oneFrameTime = 1.0 / self.FPS
                self.elapsedTime = 0.0
                self.enableRender = False

            gInputManager.SetKeyState(glfw.KEY_8, False)

        if gInputManager.GetKeyState(glfw.KEY_9) == True:
            if self.controlFPS == True:
                self.FPS = int(self.FPS / 5) * 5 + 5
                if self.FPS > 100:
                    self.FPS = 100

                self.oneFrameTime = 1.0 / self.FPS
                self.elapsedTime = 0.0
                self.enableRender = False        

            gInputManager.SetKeyState(glfw.KEY_9, False)        

        if gInputManager.GetKeyState(glfw.KEY_0) == True:
            self.controlFPS = not self.controlFPS

            if self.controlFPS == True:
                self.elapsedTime = 0.0        
                self.enableRender = False

            gInputManager.SetKeyState(glfw.KEY_0, False)

        if self.enableRender == True:
            self.elapsedTime = 0.0
            self.enableRender = False
        
    def Draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glViewport(self.screenPos[0][0], self.screenPos[0][1], self.screenSize[0], self.screenSize[1])

        self._DrawObjects()

        glViewport(0, 0, self.displaySize[0], self.displaySize[1])

        self._DrawGUI()

    def Finish(self):
        if self.debug == True or self.startLog == True:
            self.WriteLog('LOG End')

    def _InitializeDrawingStuff(self):
        self.screenPos.clear()

        screenLbPosX = int((self.displaySize[0] - self.screenSize[0]) / 2.0)
        screenLbPosY = 20
        
        screenLbPos = [screenLbPosX, screenLbPosY]
        screenRtPos = []
        screenRtPos.append(screenLbPos[0] + self.screenSize[0])
        screenRtPos.append(screenLbPos[1] + self.screenSize[1])

        self.screenPos.append(screenLbPos)
        self.screenPos.append(screenRtPos)

        imguiPos = []
        imguiSize = []

        imguiInterval = 5

        imguiPos.append(imguiInterval)
        imguiPos.append(self.displaySize[1] - self.screenPos[1][1] + imguiInterval)

        imguiSize.append(int((self.displaySize[0] - self.screenSize[0]) / 2.0) - imguiInterval * 2)
        imguiSize.append(self.displaySize[1] - self.screenPos[0][1] - imguiInterval - imguiPos[1])

        self.imguiPos.append([imguiPos[0], imguiPos[1]])
        self.imguiSize.append([imguiSize[0], imguiSize[1]])

        imguiPos[0] = self.screenPos[1][0] + imguiInterval
        imguiPos[1] = self.displaySize[1] - self.screenPos[1][1] + imguiInterval

        imguiSize[0] = int((self.displaySize[0] - self.screenSize[0]) / 2.0) - imguiInterval * 2
        imguiSize[1] = self.displaySize[1] - self.screenPos[0][1] - imguiInterval - imguiPos[1]

        self.imguiPos.append([imguiPos[0], imguiPos[1]])
        self.imguiSize.append([imguiSize[0], imguiSize[1]])

        coordAxesVerticesData = [
            0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
            1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,

            0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
            0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0,

            0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,
            0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0
            ]

        coordAxesIndicesData = [
            0, 1,
            2, 3,
            4, 5
            ]

        self.coordAxesVertices = np.array(coordAxesVerticesData, dtype = np.float32)
        self.coordAxesIndices = np.array(coordAxesIndicesData, dtype = np.uint32)

        startPos = [self.screenPos[0][0] + 10, self.screenPos[1][1] - 10]
        interval = [3.0, 5.0, 200.0]
        sideLength = interval[0] * 2 + interval[1] * 2 + interval[2]

        squarePos = []
        squarePos.append(startPos)
        squarePos.append([startPos[0] + sideLength, startPos[1]])
        squarePos.append([startPos[0] + sideLength, startPos[1] - sideLength])
        squarePos.append([startPos[0], startPos[1] - sideLength])

        programInfoAreaVerticesData = [
            squarePos[0][0] + interval[0] + interval[1], squarePos[0][1], 9.0, 1.0, 1.0, 1.0, 1.0,
            squarePos[1][0] - interval[0] - interval[1], squarePos[1][1], 9.0, 1.0, 1.0, 1.0, 1.0,
            squarePos[0][0] + interval[0] + interval[1], squarePos[0][1] - interval[0], 9.0, 1.0, 1.0, 1.0, 1.0,
            squarePos[1][0] - interval[0] - interval[1], squarePos[1][1] - interval[0], 9.0, 1.0, 1.0, 1.0, 1.0,

            squarePos[1][0], squarePos[1][1] - interval[0] - interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[2][0], squarePos[2][1] + interval[0] + interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[1][0] - interval[0], squarePos[1][1] - interval[0] - interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[2][0] - interval[0], squarePos[2][1] + interval[0] + interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,

            squarePos[2][0] - interval[0] - interval[1], squarePos[2][1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[3][0] + interval[0] + interval[1], squarePos[3][1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[2][0] - interval[0] - interval[1], squarePos[2][1] + interval[0], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[3][0] + interval[0] + interval[1], squarePos[3][1] + interval[0], 9.0, 0.0, 0.0, 1.0, 0.8,

            squarePos[3][0], squarePos[3][1] + interval[0] + interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[0][0], squarePos[0][1] - interval[0] - interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[3][0] + interval[0], squarePos[3][1] + interval[0] + interval[1], 9.0, 0.0, 0.0, 1.0, 0.8,
            squarePos[0][0] + interval[0], squarePos[0][1] - interval[0] - interval[1], 9.0, 0.0, 0.0, 1.0, 0.8            
            ]
        
        programInfoAreaIndicesData = [
            0, 1,
            2, 3,

            4, 5,
            6, 7,

            8, 9,
            10, 11,

            12, 13,
            14, 15
            ]

        self.programInfoAreaVertices = np.array(programInfoAreaVerticesData, dtype = np.float32)
        self.programInfoAreaIndices = np.array(programInfoAreaIndicesData, dtype = np.uint32)

        self.drawingStuffVerticesList.append(self.coordAxesVertices)
        self.drawingStuffVerticesList.append(self.programInfoAreaVertices)

        self.drawingStuffIndicesList.append(self.coordAxesIndices)
        self.drawingStuffIndicesList.append(self.programInfoAreaIndices)        

    def _InitializeColors(self):
        self.colors['DefaultColor_0'] = [1.0, 1.0, 1.0]
        self.colors['DefaultColor_1'] = [0.0, 0.0, 0.0]
        self.colors['DefaultColor_2'] = [1.0, 0.0, 0.0]
        self.colors['DefaultColor_3'] = [0.0, 1.0, 0.0]
        self.colors['DefaultColor_4'] = [0.0, 0.0, 1.0]
        self.colors['DefaultColor_5'] = [0.8, 0.3, 0.5]
        self.colors['DefaultColor_6'] = [0.3, 0.8, 0.5]
        self.colors['DefaultColor_7'] = [0.2, 0.3, 0.98]

        self.colors['ObjectColor_0'] = [1.0, 0.0, 0.0]
        self.colors['ObjectColor_1'] = [0.0, 0.76, 0.0]
        self.colors['ObjectColor_2'] = [0.15, 0.18, 0.85]
        self.colors['ObjectColor_3'] = [0.9, 0.73, 0.0]
        self.colors['ObjectColor_4'] = [0.95, 0.0, 0.89]
        self.colors['ObjectColor_5'] = [0.0, 0.9, 0.91]
        self.colors['ObjectColor_6'] = [1.0, 0.56, 0.0]

    def _InitializeLog(self):
        if self.logFile != None:
            return

        curPath = os.getcwd()
        curPath = curPath.replace('\\', '/')
        curPath += "/log.txt"

        self.logFile = open(curPath, 'w')

        self.WriteLog('LOG Start')
        self.startLog = True

    def _Initialize(self):
        self._InitializeDrawingStuff()

        self._InitializeColors()

    def _DrawCoordAxes(self):
        if self.view3D == False or self.drawAxes == False:
            return

        coordAxesViewportSize = [40, 40]

        glViewport(self.screenPos[1][0] - coordAxesViewportSize[0] - 10, self.screenPos[1][1] - coordAxesViewportSize[1] - 10, coordAxesViewportSize[0], coordAxesViewportSize[1])

        self.coordAxesViewMat[3].x = 0.0
        self.coordAxesViewMat[3].y = 0.0
        self.coordAxesViewMat[3].z = -2.0

        self.shaders[Index.SHADER_DEFAULT].Use()
        
        self.shaders[Index.SHADER_DEFAULT].SetMat4fv('prjMat', self.perspectivePrjMat)
        self.shaders[Index.SHADER_DEFAULT].SetMat4fv('viewMat', self.coordAxesViewMat)

        glLineWidth(2.0)

        glBindVertexArray(self.drawingStuffVAO[0])
        glDrawElements(GL_LINES, len(self.drawingStuffIndicesList[0]), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

        glViewport(0, 0, self.displaySize[0], self.displaySize[1])

    def _DrawObjects(self):
        numObjects = len(self.objects)

        if self.view3D == True:
            prjMat = self.perspectivePrjMat
            viewMat = self.view3DMat            
        else:
            prjMat = self.orthoPrjMat
            viewMat = self.view2DMat        

        for key, value in self.shaders.items():
            self.shaders[key].Use()
            self.shaders[key].SetMat4fv('prjMat', prjMat)
            self.shaders[key].SetMat4fv('viewMat', viewMat)            

        for i in range(numObjects):
            self.objects[i].Draw()

    def _DrawGUI(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_ENABLE_BIT | GL_LINE_BIT)

        glEnable(GL_BLEND)

        glDisable(GL_DEPTH_TEST)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shaders[Index.SHADER_DEFAULT].Use()

        self.shaders[Index.SHADER_DEFAULT].SetMat4fv('modelMat', self.modelMat)

        self._DrawCoordAxes()

        self._DrawProgramInfoArea()        

        glUseProgram(0)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        glOrtho(0, self.displaySize[0], 0, self.displaySize[1], -10.0, 10.0)        

        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_TEXTURE_2D)

        glDisable(GL_CULL_FACE)

        self._DrawProgramInfo()

        self._DrawSpecificProgramInfo()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glPopAttrib()
       
    def _DrawProgramInfoArea(self):
        if self.programInfo == False:
            return

        self.shaders[Index.SHADER_DEFAULT].Use()

        self.shaders[Index.SHADER_DEFAULT].SetMat4fv('prjMat', self.GUIPrjMat)
        self.shaders[Index.SHADER_DEFAULT].SetMat4fv('viewMat', self.view2DMat)       
        
        glLineWidth(1.0)
                
        glBindVertexArray(self.drawingStuffVAO[1])
        glDrawElements(GL_LINES, len(self.drawingStuffIndicesList[1]), GL_UNSIGNED_INT, None)        

        glBindVertexArray(0)        
       
    def _DrawProgramInfo(self):
        if self.programInfo == False:
            return

        glPushMatrix()
        glLoadIdentity()

        font = self.smallFont
        
        texId = font.GetTexId()

        glBindTexture(GL_TEXTURE_2D, texId)
        
        color = self.GetColor('DefaultColor_', 6)
        glColor(color[0], color[1], color[2], 1.0)

        infoText = []
        infoTextIndex = 0
        infoFPSText = ". FPS"

        if self.controlFPS == True:
            infoFPSText += ".On(8, 9; 0)"
        else:
            infoFPSText += ".Off(0)"

        infoText.append(infoFPSText + ' : {0: 0.2f}'.format(0.0))
        
        if self.controlFPS == True:
            if self.elapsedTime != 0.0:
                infoText[infoTextIndex] = infoFPSText + " : {0: 0.2f} ({1})".format(1.0 / self.elapsedTime, self.FPS)
                #print('.FPS: {0: 0.2f} ({1})'.format(1.0 / self.elapsedTime, self.FPS))
        else:
            if self.deltaTime != 0.0:
                infoText[infoTextIndex] = infoFPSText + " : {0: 0.2f}".format(1.0 / self.deltaTime)
                #print('.FPS: {0: 0.2f}'.format(1.0 / deltaTime))            

        infoText.append('. ViewMode(V) : ')
        infoTextIndex += 1

        if self.view3D == True:
            infoText[infoTextIndex] += "3D"
        else:
            infoText[infoTextIndex] += "2D"

        infoText.append('.    DrawAxes(X) : ')
        infoTextIndex += 1

        if self.drawAxes == True:
            infoText[infoTextIndex] += "On"
        else:
            infoText[infoTextIndex] += "Off"        

        infoText.append('. Pause(P) : ')
        infoTextIndex += 1
        
        if self.pause == True:
            infoText[infoTextIndex] += "On"
        else:
            infoText[infoTextIndex] += "Off"

        infoText.append('. CameraMove(M.R) : ')
        infoTextIndex += 1
        
        if self.enableCameraMove == True:
            infoText[infoTextIndex] += "On"
        else:
            infoText[infoTextIndex] += "Off"

        infoText.append('.    SailingDir')
        infoTextIndex += 1

        if self.enableCameraSailing == True:
            infoText[infoTextIndex] += "(5, 6; L) : On ({0: 0.1f})".format(self.cameraSailingSpeed)
        else:
            infoText[infoTextIndex] += "(L) : Off"        

        infoText.append('. Debug(B) : ')
        infoTextIndex += 1
        
        if self.debug == True:
            infoText[infoTextIndex] += "On"
        else:
            infoText[infoTextIndex] += "Off"

        textPosX = self.screenPos[0][0] + 20
        textPosY = self.screenPos[1][1] - 25

        for i in range(self.numProgramInfoElement):
            glTranslate(textPosX, textPosY, 0.0)

            glListBase(font.GetListOffset())
            glCallLists([ord(c) for c in infoText[i]])        

            glPopMatrix()
            glPushMatrix()
            glLoadIdentity()

            if i == self.numProgramInfoElement - 2:                
                textPosY -= 105.0
            else:
                textPosY -= 15.0

        glPopMatrix()

    def _DrawSpecificProgramInfo(self):
        if self.specificProgramInfo == False:
            return
        
        glPushMatrix()
        glLoadIdentity()        

        color = []
        textPos = [0.0, 0.0]
        textIntervalY = 0.0
        font = None
        infoText = []
        numInfoTexts = 0

        for i in range(len(self.specificProgramArgs)):
            args = self.specificProgramArgs[i]

            color = args[Index.SPECIFIC_PROGRAM_INFO_COLOR]
            glColor(color[0], color[1], color[2], 1.0)

            textPos[0] = args[Index.SPECIFIC_PROGRAM_INFO_TEXT_POS][0]
            textPos[1] = args[Index.SPECIFIC_PROGRAM_INFO_TEXT_POS][1]
            textIntervalY = args[Index.SPECIFIC_PROGRAM_INFO_TEXT_INTERVAL]
            numInfoTexts = args[Index.SPECIFIC_PROGRAM_INFO_NUM_TEXTS]

            infoText = args[Index.SPECIFIC_PROGRAM_INFO_TEXT_START : ]

            if 'Large' == args[Index.SPECIFIC_PROGRAM_INFO_FONT_SIZE]:
                font = self.largeFont
            elif 'Medium' == args[Index.SPECIFIC_PROGRAM_INFO_FONT_SIZE]:
                font = self.font

            texId = font.GetTexId()
            glBindTexture(GL_TEXTURE_2D, texId)

            for i in range(numInfoTexts):
                glTranslate(textPos[0], textPos[1], 0.0)               

                glListBase(font.GetListOffset())
                glCallLists([ord(c) for c in infoText[i]])        

                glPopMatrix()
                glPushMatrix()
                glLoadIdentity()
            
                textPos[1] -= textIntervalY        

        glPopMatrix()

class InputManager:
    def __init__(self):
        self.mouseEntered = False

        self.mouseButtonClick = [False, False, False]
        self.lastMousePos = [-1, -1]
        self.lastMousePosOnClick = [-1, -1]

        self.keys = {}

    def GetMouseEntered(self):
        return self.mouseEntered

    def SetMouseEntered(self, value):
        self.mouseEntered = value

    def GetMouseButtonClick(self, key):
        return self.mouseButtonClick[key]

    def SetMouseButtonClick(self, key, value):
        self.mouseButtonClick[key] = value

    def GetLastMousePos(self):
        return self.lastMousePos

    def SetLastMousePos(self, value):
        self.lastMousePos = value    

    def GetLastMousePosOnClick(self):
        return self.lastMousePosOnClick

    def SetLastMousePosOnClick(self, value):
        self.lastMousePosOnClick = value

    def GetKeyState(self, key):        
        if key in self.keys.keys():            
            return self.keys[key]

    def SetKeyState(self, key, value):
        self.keys[key] = value

class Camera:
    def __init__(self, cameraPos = None):
        if cameraPos == None:
            self.cameraPos = glm.vec3(0.0, 0.0, 10.0)
        else:
            self.cameraPos = cameraPos
            
        self.cameraFront = glm.vec3(0.0, 0.0, -1.0)
        self.cameraUp = glm.vec3(0.0, 1.0, 0.0)
        self.cameraRight = glm.vec3(1.0, 0.0, 0.0)
        self.cameraWorldUp = glm.vec3(0.0, 1.0, 0.0)

        self.pitch = 0.0
        self.yaw = 180.0

        self.mouseSensitivity = 0.1

        self.UpdateCameraVectors()

    def GetPos(self):
        return self.cameraPos

    def SetPos(self, cameraPos):
        self.cameraPos = cameraPos

    def GetViewMat(self):
        return glm.lookAt(self.cameraPos, self.cameraPos + self.cameraFront, self.cameraUp)    

    def ProcessMouseMovement(self, xOffset, yOffset, constrainPitch = True):
        xOffset *= self.mouseSensitivity
        yOffset *= self.mouseSensitivity

        self.yaw += xOffset
        self.pitch += yOffset

        if constrainPitch == True:
            if self.pitch > 89.0:
                self.pitch = 89.0
            elif self.pitch < -89.0:
                self.pitch = -89.0

        self.UpdateCameraVectors()

    def ProcessKeyboard(self, direction, velocity):
        if direction == "FORWARD":
            self.cameraPos += self.cameraFront * velocity
        elif direction == "BACKWARD":
            self.cameraPos -= self.cameraFront * velocity
        elif direction == "LEFT":
            self.cameraPos += self.cameraRight * velocity
        elif direction == "RIGHT":
            self.cameraPos -= self.cameraRight * velocity
        elif direction == "UPWARD":
            self.cameraPos += self.cameraUp * velocity
        elif direction == "DOWNWARD":
            self.cameraPos -= self.cameraUp * velocity

    def UpdateCameraVectors(self):
        self.cameraFront.x = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.cameraFront.y = math.sin(glm.radians(self.pitch))
        self.cameraFront.z = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))

        self.cameraFront = glm.normalize(self.cameraFront)

        self.cameraRight = glm.normalize(glm.cross(self.cameraWorldUp, self.cameraFront))
        self.cameraUp = glm.normalize(glm.cross(self.cameraFront, self.cameraRight))

class ShaderFactory:
    def __init__(self):
        self.vertexShaderCode = {}
        self.fragmentShaderCode = {}

        self._Initialize()

    def CreateShader(self, vertexShaderCodeIndex, fragmentShaderCodeIndex):
        return Shader(self.vertexShaderCode[vertexShaderCodeIndex], self.fragmentShaderCode[fragmentShaderCodeIndex])

    def _Initialize(self):
        defaultVertexShaderCode = """

        # version 330 core

        layout(location = 0) in vec3 aPos;
        layout(location = 1) in vec4 aColor;

        out vec4 color;

        uniform mat4 prjMat;
        uniform mat4 viewMat;
        uniform mat4 modelMat;


        void main()
        {
            gl_Position = prjMat * viewMat * modelMat * vec4(aPos, 1.0);

            color = aColor;
        }

        """


        defaultFragmentShaderCode = """

        # version 330 core

        in vec4 color;

        out vec4 fragColor;


        void main()
        {
            fragColor = color;            
        }

        """


        simpleUseUniformColorFragmentShaderCode = """

        # version 330 core

        in vec4 color;

        out vec4 fragColor;        

        uniform vec4 uniformColor;
        uniform bool useUniformColor;


        void main()
        {
            if (useUniformColor)
            {
                fragColor = uniformColor;
            }
            else
            {
                fragColor = color;
            }
        }

        """


        fragmentCoordinateFragmentShaderCode = """

        # version 330 core

        in vec4 color;

        out vec4 fragColor;

        uniform vec3 modifiedMouseCoord;
        uniform vec3 circleColor;
        uniform bvec3 circleAnimation;

        uniform vec2 circleArea;
        uniform ivec2 resolution;
        uniform ivec2 screenLBPos;

        uniform float globalTime;
        uniform bool colorFactorReversal;


        void main()
        {
            vec2 modifiedFragCoord = vec2(gl_FragCoord.xy - screenLBPos);
            vec2 p = modifiedFragCoord.xy / resolution.x;
            vec2 m = modifiedMouseCoord.xy / resolution.x;

            if (circleAnimation.y == true)
            {
                float moveCycle = 0.5 * sin(globalTime);
                p.x += moveCycle;
            }

            float dis = length(p - m);
            float radius = circleArea.x;
            float smoothThickness = circleArea.y;

            float colorFactor = 0.0;

            if (modifiedMouseCoord.z > 0.0)
            {
                colorFactor = smoothstep(radius - smoothThickness, radius, dis); 

                if (colorFactorReversal)
                {
                    colorFactor = 1.0 - colorFactor;
                }
            }

            vec3 modifiedCircleColor = circleColor;

            if (circleAnimation.z == true)
            {
                float redColorCycle = 0.5 + 0.5 * sin(0.25 * globalTime);
                float greenColorCycle = 0.5 + 0.5 * sin(0.5 * globalTime);
                float blueColorCycle = 0.5 + 0.5 * sin(globalTime);

                modifiedCircleColor.x = redColorCycle;
                modifiedCircleColor.y = greenColorCycle;
                modifiedCircleColor.z = blueColorCycle;
            }

            if (circleAnimation.x == true)
            {
                float fadeCycle = 0.5 + 0.5 * sin(globalTime);
                modifiedCircleColor *= fadeCycle;
            }

            fragColor = vec4(modifiedCircleColor * colorFactor, 1.0);
        }

        """
        

        self.vertexShaderCode[Index.SHADER_VERTEX_CODE_DEFAULT] = defaultVertexShaderCode
        
        self.fragmentShaderCode[Index.SHADER_FRAGMENT_CODE_DEFAULT] = defaultFragmentShaderCode
        self.fragmentShaderCode[Index.SHADER_FRAGMENT_CODE_SIMPLE_USE_UNIFORMCOLOR] = simpleUseUniformColorFragmentShaderCode
        self.fragmentShaderCode[Index.SHADER_FRAGMENT_CODE_FRAGMENT_COORDINATE] = fragmentCoordinateFragmentShaderCode

class Shader:
    def __init__(self, vertexShaderCode, fragmentShaderCode):
        self.program = None

        self._Initialize(vertexShaderCode, fragmentShaderCode)        

    def Use(self):
        glUseProgram(self.program)

    def SetBool(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform1i(loc, value)

    def SetFloat(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform1f(loc, value)

    def SetVec2i(self, name, x, y):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform2i(loc, x, y)

    def SetVec2f(self, name, x, y):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform2f(loc, x, y)

    def SetVec3i(self, name, x, y, z):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform3i(loc, x, y, z)

    def SetVec3f(self, name, x, y, z):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform3f(loc, x, y, z)

    def SetVec4f(self, name, x, y, z, w):
        loc = glGetUniformLocation(self.program, name)
        
        glUniform4f(loc, x, y, z, w)

    def SetMat4fv(self, name, value):
        loc = glGetUniformLocation(self.program, name)

        value = np.array(value, dtype = np.float32)
        glUniformMatrix4fv(loc, 1, GL_TRUE, value)

    def _Initialize(self, vertexShaderCode, fragmentShaderCode):
        vertexShader = compileShader(vertexShaderCode, GL_VERTEX_SHADER)
        fragmentShader = compileShader(fragmentShaderCode, GL_FRAGMENT_SHADER)

        self.program = compileProgram(vertexShader, fragmentShader)

class Font:
    def __init__(self, fontPath, size):
        self.face = ft.Face(fontPath)
        self.face.set_char_size(size << 6)

        self.charsSize = (6, 16)
        self.charsAdvanceX = []

        self.maxCharHeight = 0
        self.charStartOffset = 32
        self.listOffset = -1
        self.texId = -1

        numChars = self.charsSize[0] * self.charsSize[1]

        self.charsAdvanceX = [0 for i in range(numChars)]

        advanceX, ascender, descender = 0, 0, 0
        charEndIndex = self.charStartOffset + numChars

        for c in range(self.charStartOffset, charEndIndex):
            self.face.load_char(chr(c), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)

            self.charsAdvanceX[c - self.charStartOffset] = self.face.glyph.advance.x >> 6

            advanceX = max(advanceX, self.face.glyph.advance.x >> 6)
            ascender = max(ascender, self.face.glyph.metrics.horiBearingY >> 6)
            descender = max(descender, (self.face.glyph.metrics.height >> 6) - (self.face.glyph.metrics.horiBearingY >> 6))

        self.maxCharHeight = ascender + descender
        maxTotalAdvanceX = advanceX * self.charsSize[1]
        maxTotalHeight = self.maxCharHeight * self.charsSize[0]

        exponent = 0
        bitmapDataSize = [0, 0]

        while maxTotalAdvanceX > math.pow(2, exponent):
            exponent += 1
        bitmapDataSize[1] = int(math.pow(2, exponent))

        exponent = 0

        while maxTotalHeight > math.pow(2, exponent):
            exponent += 1
        bitmapDataSize[0] = int(math.pow(2, exponent))

        self.bitmapData = np.zeros((bitmapDataSize[0], bitmapDataSize[1]), dtype = np.ubyte)

        x, y, charIndex = 0, 0, 0

        for r in range(self.charsSize[0]):
            for c in range(self.charsSize[1]):
                self.face.load_char(chr(self.charStartOffset + r * self.charsSize[1] + c), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)

                charIndex = r * self.charsSize[1] + c

                bitmap = self.face.glyph.bitmap
                x += self.face.glyph.bitmap_left
                y = r * self.maxCharHeight + ascender - self.face.glyph.bitmap_top

                self.bitmapData[y : y + bitmap.rows, x : x + bitmap.width].flat = bitmap.buffer

                x += self.charsAdvanceX[charIndex] - self.face.glyph.bitmap_left

            x = 0

    def GetTexId(self):
        return self.texId

    def GetListOffset(self):
        return self.listOffset

    def MakeFontTextureWithGenList(self):
        self.texId = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, self.texId)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

        self.bitmapData = np.flipud(self.bitmapData)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.bitmapData.shape[1], self.bitmapData.shape[0], 0,
                     GL_ALPHA, GL_UNSIGNED_BYTE, self.bitmapData)

        dx = 0.0
        dy = self.maxCharHeight / float(self.bitmapData.shape[0])

        listStartIndex = glGenLists(self.charsSize[0] * self.charsSize[1])
        self.listOffset = listStartIndex - self.charStartOffset

        for r in range(self.charsSize[0]):
            for c in range(self.charsSize[1]):
                glNewList(listStartIndex + r * self.charsSize[1] + c, GL_COMPILE)

                charIndex = r * self.charsSize[1] + c

                advanceX = self.charsAdvanceX[charIndex]
                dAdvanceX = advanceX / float(self.bitmapData.shape[1])

                glBegin(GL_QUADS)
                glTexCoord2f(dx, 1.0 - r * dy), glVertex3f(0.0, 0.0, 0.0)
                glTexCoord2f(dx + dAdvanceX, 1.0 - r * dy), glVertex3f(advanceX, 0.0, 0.0)
                glTexCoord2f(dx + dAdvanceX, 1.0 - (r + 1) * dy), glVertex3f(advanceX, -self.maxCharHeight, 0.0)
                glTexCoord2f(dx, 1.0 - (r + 1) * dy), glVertex3f(0.0, -self.maxCharHeight, 0.0)
                glEnd()

                glTranslate(advanceX, 0.0, 0.0)

                glEndList()

                dx += dAdvanceX

            glTranslatef(0.0, -self.maxCharHeight, 0.0)
            dx = 0.0

class Model:
    def __init__(self, modelPath, normalLineScale):
        self.vertices = []
        self.indices = []
        self.verticesExceptNoUse = []

        self.normals = []
        self.normalLineVertices = []
        self.normalLineIndices = []

        self.normalLineScale = normalLineScale

        self.numVertices = 0
        self.numVerticesExceptNoUse = 0
        self.numFaces = 0

        self._Initialize(modelPath)

    def GetVertices(self):
        return self.vertices

    def GetVerticesExceptNoUse(self):
        return self.verticesExceptNoUse

    def GetIndices(self):
        return self.indices

    def GetNormalLineVertices(self):
        return self.normalLineVertices

    def GetNormalLineIndices(self):
        return self.normalLineIndices

    def GetNumVertices(self):
        return self.numVertices

    def GetNumVerticesExceptNoUse(self):
        return self.numVerticesExceptNoUse

    def _Initialize(self, modelPath):
        with open(modelPath, mode = 'r') as fin:
            for line in fin:
                sl = line.split()

                if len(sl) == 0:
                    continue
                elif sl[0] in ['#']:
                    continue
                elif sl[0] == 'v':
                    for v in sl[1 : len(sl)]:
                        self.vertices.append(float(v))
                elif sl[0] == 'f':
                    for s in sl[1 : len(sl)]:
                        il = s.split('/')
                        self.indices.append(int(il[0]) - 1)

        self.numVertices = int(len(self.vertices) / 3)
        self.numFaces = int(len(self.indices) / 3)

        self.normals = np.zeros(len(self.vertices), dtype = np.float32)

        for i in range(self.numFaces):
            vertexAIndex = self.indices[i * 3 + 0]
            vertexBIndex = self.indices[i * 3 + 1]
            vertexCIndex = self.indices[i * 3 + 2]

            vecA = glm.vec3(self.vertices[vertexAIndex * 3 + 0], self.vertices[vertexAIndex * 3 + 1], self.vertices[vertexAIndex * 3 + 2])
            vecB = glm.vec3(self.vertices[vertexBIndex * 3 + 0], self.vertices[vertexBIndex * 3 + 1], self.vertices[vertexBIndex * 3 + 2])
            vecC = glm.vec3(self.vertices[vertexCIndex * 3 + 0], self.vertices[vertexCIndex * 3 + 1], self.vertices[vertexCIndex * 3 + 2])

            vecAB = vecB - vecA
            vecAC = vecC - vecA

            faceNormal = glm.normalize(glm.cross(vecAB, vecAC))

            self.normals[vertexAIndex * 3 + 0] += faceNormal.x
            self.normals[vertexAIndex * 3 + 1] += faceNormal.y
            self.normals[vertexAIndex * 3 + 2] += faceNormal.z

            self.normals[vertexBIndex * 3 + 0] += faceNormal.x
            self.normals[vertexBIndex * 3 + 1] += faceNormal.y
            self.normals[vertexCIndex * 3 + 2] += faceNormal.z

            self.normals[vertexCIndex * 3 + 0] += faceNormal.x
            self.normals[vertexCIndex * 3 + 1] += faceNormal.y
            self.normals[vertexCIndex * 3 + 2] += faceNormal.z

        useVertices = np.zeros(self.numVertices, dtype = np.bool8)

        for i in range(len(self.indices)):
            index = self.indices[i]
            useVertices[index] = True

        for i in range(self.numVertices):
            if useVertices[i] == True:
                vertexNormal = glm.vec3(self.normals[i * 3 + 0], self.normals[i * 3 + 1], self.normals[i * 3 + 2])
                vertexNormal = glm.normalize(vertexNormal)

                self.normals[i * 3 + 0] = vertexNormal.x
                self.normals[i * 3 + 1] = vertexNormal.y
                self.normals[i * 3 + 2] = vertexNormal.z

        for i in range(self.numVertices):
            if useVertices[i] == True:
                self.verticesExceptNoUse.append(self.vertices[i * 3 + 0])
                self.verticesExceptNoUse.append(self.vertices[i * 3 + 1])
                self.verticesExceptNoUse.append(self.vertices[i * 3 + 2])
                
        self.numVerticesExceptNoUse = int(len(self.verticesExceptNoUse) / 3)

        for i in range(self.numVertices):
            if useVertices[i] == True:
                self.normalLineVertices.append(self.vertices[i * 3 + 0])
                self.normalLineVertices.append(self.vertices[i * 3 + 1])
                self.normalLineVertices.append(self.vertices[i * 3 + 2])

                self.normalLineVertices.append(self.vertices[i * 3 + 0] + self.normals[i * 3 + 0] * self.normalLineScale)
                self.normalLineVertices.append(self.vertices[i * 3 + 1] + self.normals[i * 3 + 1] * self.normalLineScale)
                self.normalLineVertices.append(self.vertices[i * 3 + 2] + self.normals[i * 3 + 2] * self.normalLineScale)
        
                self.normalLineIndices.append(i * 2 + 0)
                self.normalLineIndices.append(i * 2 + 1)
        

gSceneManager = SceneManager(True)
gInputManager = InputManager()

gShaderFactory = ShaderFactory()


class FragmentCoordinate:
    def __init__(self, programName, programNamePos):
        self.programName = programName
        self.programNamePos = programNamePos

        self.objectsVerticesList = []
        self.objectsIndicesList = []
        
        self.GUIObjectsVerticesList = []
        self.GUIObjectsIndicesList = []

        self.firstMouseClick = -1.0
        self.mouseData = []

        self.imguiInspector = {}

        self.imguiTabItemFlags = imgui.TAB_ITEM_SET_SELECTED        
        
        self.numVertexComponents = 7
        
        self.numObjects = 0

        self.objectsVAO = None
        self.objectsVBO = None
        self.objectsEBO = None       
        
        self.numGUIObjects = 0

        self.GUIObjectsVAO = None
        self.GUIObjectsVBO = None
        self.GUIObjectsEBO = None

        self._Initialize()

    def Restart(self):
        gSceneManager.SetCamera(Camera())        

        self._Initialize()        

    def UpdateAboutKeyInput(self, key, value = True):
        pass

    def UpdateAboutMouseInput(self, button, pos):
        if button == glfw.MOUSE_BUTTON_LEFT:
            displaySize = gSceneManager.GetDisplaySize()
            screenPos = gSceneManager.GetScreenPos()

            mousePos = gInputManager.GetLastMousePos()

            inverseMousePosY = displaySize[1] - mousePos[1]

            if gInputManager.GetMouseEntered() == True:
                if self.firstMouseClick < 0.0:
                    self.firstMouseClick *= -1.0

                modifiedMouseX = mousePos[0] - screenPos[0][0]
                modifiedMouseY = inverseMousePosY - screenPos[0][1]

                self.mouseData = [modifiedMouseX, modifiedMouseY, self.firstMouseClick]
            else:
                gInputManager.SetMouseButtonClick(glfw.MOUSE_BUTTON_LEFT, False)

    def Update(self, deltaTime):
        if gSceneManager.GetView3D() != True:
            return        
        
        self._UpdateNewFrameImgui(deltaTime)

    def Draw(self):
        if gSceneManager.GetView3D() != True:
            return

        self._DrawObjects()

        displaySize = gSceneManager.GetDisplaySize()                
            
        glViewport(0, 0, displaySize[0], displaySize[1])    
        
        shader = gSceneManager.GetShader(Index.SHADER_DEFAULT)
        
        shader.Use()
        shader.SetMat4fv('prjMat', gSceneManager.GetGUIPrjMat())
        shader.SetMat4fv('viewMat', gSceneManager.GetView2DMat())

        self._DrawGUI()    

    def _InitializeObjects(self):
        self.objectsVerticesList.clear()
        self.objectsIndicesList.clear()

        if self.numObjects > 0:
            glDeleteVertexArrays(self.numObjects, self.objectsVAO)
            glDeleteBuffers(self.numObjects, self.objectsVBO)
            glDeleteBuffers(self.numObjects, self.objectsEBO)

        self.numObjects = 0

        self.firstMouseClick = -1.0
        self.mouseData = [0.0, 0.0, 0.0]

        canvasVerticesData = [
            -1.0, -1.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            1.0, -1.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            -1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0
            ]

        canvasIndicesData = [
            0, 1, 2, 3
            ]

        self.objectsVerticesList.append(np.array(canvasVerticesData, dtype = np.float32))
        self.objectsIndicesList.append(np.array(canvasIndicesData, dtype = np.uint32))

        self.numObjects += 1

        self.objectsVerticesList.append(np.array(0.0, dtype = np.float32))
        self.objectsIndicesList.append(np.array(0, dtype = np.uint32))

        self.numObjects += 1

        self.objectsVAO = glGenVertexArrays(self.numObjects)
        self.objectsVBO = glGenBuffers(self.numObjects)
        self.objectsEBO = glGenBuffers(self.numObjects)

        for i in range(self.numObjects):
            glBindVertexArray(self.objectsVAO[i])

            glBindBuffer(GL_ARRAY_BUFFER, self.objectsVBO[i])
            glBufferData(GL_ARRAY_BUFFER, self.objectsVerticesList[i].nbytes, self.objectsVerticesList[i], GL_STATIC_DRAW)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.objectsEBO[i])
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.objectsIndicesList[i].nbytes, self.objectsIndicesList[i], GL_STATIC_DRAW)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.objectsVerticesList[i].itemsize * self.numVertexComponents, ctypes.c_void_p(0))

            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, self.objectsVerticesList[i].itemsize * self.numVertexComponents, ctypes.c_void_p(self.objectsVerticesList[i].itemsize * 3))

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    
    def _InitializeGUIObjects(self):
        gSceneManager.ClearSpecificProgramArgs()

        self.GUIObjectsVerticesList.clear()
        self.GUIObjectsVerticesList.clear()

        if self.numGUIObjects > 0:
            glDeleteVertexArrays(self.numGUIObjects, self.GUIObjectsVAO)
            glDeleteBuffers(self.numGUIObjects, self.GUIObjectsVBO)
            glDeleteBuffers(self.numGUIObjects, self.GUIObjectsEBO)

        self.numGUIObjects = 0

        self.imguiInspector = {
            'ControlColorFactorReversal' : True,
            'ControlCircleColor' : [1.0, 1.0, 1.0],
            'ControlCircleArea' : [0.1, 0.1],
            'ControlCircleAnimation' : {'Fade' : False, 'Move' : False, 'Color' : False}
            }

        self.imguiTabItemFlags = imgui.TAB_ITEM_SET_SELECTED

        displaySize = gSceneManager.GetDisplaySize()
        screenPos = gSceneManager.GetScreenPos()

        backgroundVerticesData = [
            0.0, 0.0, 5.0, 1.0, 0.0, 0.0, 0.5,
            screenPos[0][0], 0.0, 5.0, 1.0, 0.0, 0.0, 0.5,
            screenPos[0][0], displaySize[1], 5.0, 1.0, 0.0, 0.0, 0.5,
            0.0, displaySize[1], 5.0, 1.0, 0.0, 0.0, 0.5,

            screenPos[1][0], 0.0, 5.0, 1.0, 0.0, 0.0, 0.5,
            displaySize[0], 0.0, 5.0, 1.0, 0.0, 0.0, 0.5,
            displaySize[0], displaySize[1], 5.0, 1.0, 0.0, 0.0, 0.5,
            screenPos[1][0], displaySize[1], 5.0, 1.0, 0.0, 0.0, 0.5,

            0.0, 0.0, 5.0, 1.0, 0.0, 0.0, 0.5,
            displaySize[0], 0.0, 5.0, 1.0, 0.0, 0.0, 0.5,
            displaySize[0], screenPos[0][1], 5.0, 1.0, 0.0, 0.0, 0.5,
            0.0, screenPos[0][1], 5.0, 1.0, 0.0, 0.0, 0.5,

            0.0, screenPos[1][1], 5.0, 1.0, 0.0, 0.0, 0.5,
            displaySize[0], screenPos[1][1], 5.0, 1.0, 0.0, 0.0, 0.5,
            displaySize[0], displaySize[1], 5.0, 1.0, 0.0, 0.0, 0.5,
            0.0, displaySize[1], 5.0, 1.0, 0.0, 0.0, 0.5
            ]

        backgroundIndicesData = [
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4,
            8, 9, 10, 10, 11, 8,
            12, 13, 14, 14, 15, 12
            ]

        self.GUIObjectsVerticesList.append(np.array(backgroundVerticesData, dtype = np.float32))
        self.GUIObjectsIndicesList.append(np.array(backgroundIndicesData, dtype = np.uint32))

        self.numGUIObjects += 1

        backgroundLineVerticesData = [
            0.0, screenPos[0][1], 8.0, 1.0, 1.0, 1.0, 1.0,
            displaySize[0], screenPos[0][1], 8.0, 1.0, 1.0, 1.0, 1.0,

            0.0, screenPos[1][1], 8.0, 1.0, 1.0, 1.0, 1.0,
            displaySize[0], screenPos[1][1], 8.0, 1.0, 1.0, 1.0, 1.0,

            screenPos[0][0], 0.0, 8.0, 1.0, 1.0, 1.0, 1.0,
            screenPos[0][0], displaySize[1], 8.0, 1.0, 1.0, 1.0, 1.0,

            screenPos[1][0], 0.0, 8.0, 1.0, 1.0, 1.0, 1.0,
            screenPos[1][0], displaySize[1], 8.0, 1.0, 1.0, 1.0, 1.0
            ]

        backgroundLineIndicesData = [
            0, 1,
            2, 3,
            4, 5,
            6, 7
            ]

        self.GUIObjectsVerticesList.append(np.array(backgroundLineVerticesData, dtype = np.float32))
        self.GUIObjectsIndicesList.append(np.array(backgroundLineIndicesData, dtype = np.uint32))

        self.numGUIObjects += 1        
        
        self.GUIObjectsVAO = glGenVertexArrays(self.numGUIObjects)
        self.GUIObjectsVBO = glGenBuffers(self.numGUIObjects)
        self.GUIObjectsEBO = glGenBuffers(self.numGUIObjects)

        for i in range(self.numGUIObjects):
            glBindVertexArray(self.GUIObjectsVAO[i])

            glBindBuffer(GL_ARRAY_BUFFER, self.GUIObjectsVBO[i])
            glBufferData(GL_ARRAY_BUFFER, self.GUIObjectsVerticesList[i].nbytes, self.GUIObjectsVerticesList[i], GL_STATIC_DRAW)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.GUIObjectsEBO[i])
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.GUIObjectsIndicesList[i].nbytes, self.GUIObjectsIndicesList[i], GL_STATIC_DRAW)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.GUIObjectsVerticesList[i].itemsize * self.numVertexComponents, ctypes.c_void_p(0))

            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, self.GUIObjectsVerticesList[i].itemsize * self.numVertexComponents, ctypes.c_void_p(self.GUIObjectsVerticesList[i].itemsize * 3))

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        gSceneManager.AddSpecificProgramArgs(gSceneManager.GetColor('DefaultColor_', 7), self.programNamePos, 0, 1, 'Medium', '# ' + self.programName)

    def _Initialize(self):
        gSceneManager.SetView3D(True)        

        self._InitializeObjects()
        
        self._InitializeGUIObjects()    

    def _ImguiTextPreOrderRecursively(self, hierarchyDict, key, value, numSpace = 0):
        if isinstance(value, dict) == True:
            for sKey, sValue in hierarchyDict[key].items():
                if isinstance(sValue, dict) == True:
                    self._ImguiTextPreOrderRecursively(hierarchyDict[key], sKey, sValue, numSpace + 1)
                else:
                    sValueText = "".ljust(numSpace * 5) + str(sValue)
                    imgui.text(sValueText)
        else:
            valueText = "".ljust(numSpace * 5) + str(value)
            imgui.text(valueText)

    def _UpdateNewFrameImguiHierarchy(self, deletaTime):
        imguiSize = gSceneManager.GetImguiSize(Index.IMGUI_WINDOW_HIERARCHY)
        imguiPos = gSceneManager.GetImguiPos(Index.IMGUI_WINDOW_HIERARCHY)

        imguiFont = gSceneManager.GetImguiFont()

        imgui.set_window_position_labeled('Hierarchy', imguiPos[0], imguiPos[1], imgui.ONCE)
        imgui.set_window_size_named('Hierarchy', imguiSize[0], imguiSize[1], imgui.ONCE)

        imgui.push_font(imguiFont)

        with imgui.begin('Hierarchy', False, imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE):
            with imgui.begin_tab_bar('HierarchyTabBar'):
                if imgui.begin_tab_item('Hierarchy').selected:
                    imgui.text('Hierarchy Features')
                    imgui.end_tab_item()

        imgui.pop_font()
        
    def _UpdateNewFrameImguiInspector(self, deltaTime):
        imguiSize = gSceneManager.GetImguiSize(Index.IMGUI_WINDOW_INSPECTOR)
        imguiPos = gSceneManager.GetImguiPos(Index.IMGUI_WINDOW_INSPECTOR)

        imguiFont = gSceneManager.GetImguiFont()        

        imgui.set_window_position_labeled('Inspector', imguiPos[0], imguiPos[1], imgui.ONCE)
        imgui.set_window_size_named('Inspector', imguiSize[0], imguiSize[1], imgui.ONCE)

        imgui.push_font(imguiFont)

        with imgui.begin('Inspector', False, imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE):
            with imgui.begin_tab_bar('InspectorTabBar'):
                if imgui.begin_tab_item('Control').selected:
                    _, value = imgui.checkbox('Color Factor Reversal', self.imguiInspector['ControlColorFactorReversal'])
                    self.imguiInspector['ControlColorFactorReversal'] = value
                    imgui.text('Circle Color')
                    values = self.imguiInspector['ControlCircleColor']
                    _, values = imgui.slider_float3('RGB', *values, min_value = 0.0, max_value = 1.0, format = '%0.2f')
                    self.imguiInspector['ControlCircleColor'] = values
                    imgui.text('Circle Area')
                    values = self.imguiInspector['ControlCircleArea']
                    _, values = imgui.slider_float2('Radius, SmoothTN', *values, min_value = 0.0, max_value = 1.0, format = '%0.2f')
                    self.imguiInspector['ControlCircleArea'] = values
                    imgui.text('Circle Animation')
                    for key, value in self.imguiInspector['ControlCircleAnimation'].items():
                        _, value = imgui.checkbox(key, value)
                        self.imguiInspector['ControlCircleAnimation'][key] = value
                    imgui.separator()
                    imgui.text('Control Features')
                    imgui.end_tab_item()
                if imgui.begin_tab_item('Test').selected:
                    imgui.text('Test Features')
                    imgui.end_tab_item()                          
        
        imgui.pop_font()

    def _UpdateNewFrameImgui(self, deltaTime):
        imgui.new_frame()

        self._UpdateNewFrameImguiHierarchy(deltaTime)

        self._UpdateNewFrameImguiInspector(deltaTime)    

    def _DrawObjects(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_ENABLE_BIT)

        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        shader = gSceneManager.GetShader(Index.SHADER_FRAGMENT_COORDINATE)

        shader.Use()

        transMat = glm.mat4()
        rotMat = glm.mat4()

        scale = 6.0

        scaleMat = glm.scale(glm.vec3(scale, scale, 1.0))

        canvasModelMat = transMat * rotMat * scaleMat

        shader.SetMat4fv('modelMat', canvasModelMat)

        shader.SetVec3f('modifiedMouseCoord', self.mouseData[0], self.mouseData[1], self.mouseData[2])

        circleColor = self.imguiInspector['ControlCircleColor']
        shader.SetVec3f('circleColor', circleColor[0], circleColor[1], circleColor[2])

        circleAnimation = self.imguiInspector['ControlCircleAnimation']
        shader.SetVec3i('circleAnimation', circleAnimation['Fade'], circleAnimation['Move'], circleAnimation['Color'])

        circleArea = self.imguiInspector['ControlCircleArea']
        shader.SetVec2f('circleArea', circleArea[0], circleArea[1])

        shader.SetFloat('globalTime', glfw.get_time())
        shader.SetBool('colorFactorReversal', self.imguiInspector['ControlColorFactorReversal'])

        glBindVertexArray(self.objectsVAO[0])
        glDrawElements(GL_QUADS, len(self.objectsIndicesList[0]), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

        glPopAttrib()

    def _DrawGUI(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_ENABLE_BIT | GL_LINE_BIT)

        glDisable(GL_DEPTH_TEST)

        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ZERO)

        shader = gSceneManager.GetShader(Index.SHADER_DEFAULT)

        shader.Use()

        tempModelMat = glm.mat4()
        shader.SetMat4fv('modelMat', tempModelMat)

        shader.SetBool('useUniformColor', False)

        GUIObjectsIndex = 0
        
        glBindVertexArray(self.GUIObjectsVAO[GUIObjectsIndex])
        glDrawElements(GL_TRIANGLES, len(self.GUIObjectsIndicesList[GUIObjectsIndex]), GL_UNSIGNED_INT, None)        
        
        GUIObjectsIndex += 1

        glLineWidth(2.0)

        glBindVertexArray(self.GUIObjectsVAO[GUIObjectsIndex])
        glDrawElements(GL_LINES, len(self.GUIObjectsIndicesList[GUIObjectsIndex]), GL_UNSIGNED_INT, None)
        
        glBindVertexArray(0)

        glPopAttrib()


def HandleWindowSizeCallback(glfwWindow, width, height):
    glViewport(0, 0, width, height)    

def HandleKeyCallback(glfwWindow, key, scanCode, action, modes):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(glfwWindow, glfw.TRUE)
        elif key == glfw.KEY_SPACE:
            gInputManager.SetKeyState(glfw.KEY_SPACE, True)

        if key == glfw.KEY_1:
            gInputManager.SetKeyState(glfw.KEY_1, True)
        elif key == glfw.KEY_2:
            gInputManager.SetKeyState(glfw.KEY_2, True)
        elif key == glfw.KEY_3:
            gInputManager.SetKeyState(glfw.KEY_3, True)
        elif key == glfw.KEY_4:
            gInputManager.SetKeyState(glfw.KEY_4, True)
        elif key == glfw.KEY_5:
            gInputManager.SetKeyState(glfw.KEY_5, True)
        elif key == glfw.KEY_6:
            gInputManager.SetKeyState(glfw.KEY_6, True)
        elif key == glfw.KEY_8:
            gInputManager.SetKeyState(glfw.KEY_8, True)
        elif key == glfw.KEY_9:
            gInputManager.SetKeyState(glfw.KEY_9, True)
        elif key == glfw.KEY_0:
            gInputManager.SetKeyState(glfw.KEY_0, True)

        if key == glfw.KEY_B:
            gInputManager.SetKeyState(glfw.KEY_B, True)        
        elif key == glfw.KEY_F:
            gInputManager.SetKeyState(glfw.KEY_F, True)        
        elif key == glfw.KEY_I:
            gInputManager.SetKeyState(glfw.KEY_I, True) 
        elif key == glfw.KEY_L:
            gInputManager.SetKeyState(glfw.KEY_L, True)
        elif key == glfw.KEY_P:
            gInputManager.SetKeyState(glfw.KEY_P, True)            
        elif key == glfw.KEY_R:
            gInputManager.SetKeyState(glfw.KEY_R, True)        
        elif key == glfw.KEY_V:
            gInputManager.SetKeyState(glfw.KEY_V, True)
        elif key == glfw.KEY_X:
            gInputManager.SetKeyState(glfw.KEY_X, True)

        if key == glfw.KEY_W:
            gInputManager.SetKeyState(glfw.KEY_W, True)
        elif key == glfw.KEY_S:
            gInputManager.SetKeyState(glfw.KEY_S, True)
        elif key == glfw.KEY_A:
            gInputManager.SetKeyState(glfw.KEY_A, True)
        elif key == glfw.KEY_D:
            gInputManager.SetKeyState(glfw.KEY_D, True)
        elif key == glfw.KEY_Q:
            gInputManager.SetKeyState(glfw.KEY_Q, True)
        elif key == glfw.KEY_E:
            gInputManager.SetKeyState(glfw.KEY_E, True)

        if key == glfw.KEY_LEFT:
            gInputManager.SetKeyState(glfw.KEY_LEFT, True)
        elif key == glfw.KEY_RIGHT:
            gInputManager.SetKeyState(glfw.KEY_RIGHT, True)
        elif key == glfw.KEY_UP:
            gInputManager.SetKeyState(glfw.KEY_UP, True)
        elif key == glfw.KEY_DOWN:
            gInputManager.SetKeyState(glfw.KEY_DOWN, True)

    if action == glfw.RELEASE:
        if key == glfw.KEY_W:
            gInputManager.SetKeyState(glfw.KEY_W, False)
        elif key == glfw.KEY_S:
            gInputManager.SetKeyState(glfw.KEY_S, False)
        elif key == glfw.KEY_A:
            gInputManager.SetKeyState(glfw.KEY_A, False)
        elif key == glfw.KEY_D:
            gInputManager.SetKeyState(glfw.KEY_D, False)
        elif key == glfw.KEY_Q:
            gInputManager.SetKeyState(glfw.KEY_Q, False)
        elif key == glfw.KEY_E:
            gInputManager.SetKeyState(glfw.KEY_E, False)

        if key == glfw.KEY_LEFT:
            gInputManager.SetKeyState(glfw.KEY_LEFT, False)
        elif key == glfw.KEY_RIGHT:
            gInputManager.SetKeyState(glfw.KEY_RIGHT, False)
        elif key == glfw.KEY_UP:
            gInputManager.SetKeyState(glfw.KEY_UP, False)
        elif key == glfw.KEY_DOWN:
            gInputManager.SetKeyState(glfw.KEY_DOWN, False)

def HandleMouseButtonCallback(glfwWindow, button, action, mod):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:            
            gInputManager.SetMouseButtonClick(glfw.MOUSE_BUTTON_LEFT, True)
            gInputManager.SetLastMousePosOnClick(glfw.get_cursor_pos(glfwWindow))            
        elif action == glfw.RELEASE:
            gInputManager.SetMouseButtonClick(glfw.MOUSE_BUTTON_LEFT, False)

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            gInputManager.SetMouseButtonClick(glfw.MOUSE_BUTTON_RIGHT, True)            

            mousePos = glfw.get_cursor_pos(glfwWindow)
            
            gInputManager.SetLastMousePosOnClick(mousePos)

            if gSceneManager.GetView3D() == False:
                return

            if gInputManager.GetMouseEntered() == True:
                gSceneManager.SetEnableCameraMove(True)
                gInputManager.SetLastMousePos(mousePos)
            else:
                gSceneManager.SetEnableCameraMove(False)

        elif action == glfw.RELEASE:
            gSceneManager.SetEnableCameraMove(False)
            gInputManager.SetMouseButtonClick(glfw.MOUSE_BUTTON_RIGHT, False)            

def HandleCursorPosCallback(glfwWindow, xPos, yPos):
    screenPos = gSceneManager.GetScreenPos()
    
    displaySize = gSceneManager.GetDisplaySize()

    inversePosY = displaySize[1] - yPos

    if xPos < screenPos[0][0] or screenPos[1][0] < xPos:
        gInputManager.SetMouseEntered(False)
    elif inversePosY < screenPos[0][1] or screenPos[1][1] < inversePosY:
        gInputManager.SetMouseEntered(False)
    else:
        gInputManager.SetMouseEntered(True)

    if gSceneManager.GetEnableCameraMove() == True:
        lastPos = gInputManager.GetLastMousePos()
        xOffset = lastPos[0] - xPos
        yOffset = lastPos[1] - yPos

        gInputManager.SetLastMousePos([xPos, yPos])

        camera = gSceneManager.GetCamera()

        if gSceneManager.GetView3D() == True:
            camera.ProcessMouseMovement(xOffset, yOffset)        
    
        mouseCheckInterval = 20

        if xPos < 0:
            glfw.set_cursor_pos(glfwWindow, displaySize[0] - mouseCheckInterval, yPos)
            gInputManager.SetLastMousePos(glfw.get_cursor_pos(glfwWindow))
        elif xPos > displaySize[0]:
            glfw.set_cursor_pos(glfwWindow, mouseCheckInterval, yPos)
            gInputManager.SetLastMousePos(glfw.get_cursor_pos(glfwWindow))

        if yPos < 0:
            glfw.set_cursor_pos(glfwWindow, xPos, displaySize[1] - mouseCheckInterval)
            gInputManager.SetLastMousePos(glfw.get_cursor_pos(glfwWindow))
        elif yPos > displaySize[1]:
            glfw.set_cursor_pos(glfwWindow, xPos, mouseCheckInterval)
            gInputManager.SetLastMousePos(glfw.get_cursor_pos(glfwWindow))

        gSceneManager.SetDirty(True)

        if gSceneManager.GetDebug() == True:
            gSceneManager.WriteLog('MousePos : {0}'.format([xPos, yPos]))
            gSceneManager.WriteLog('LastMousePos : {0}'.format(gInputManager.GetLastMousePos()))
        
    else:
        gInputManager.SetLastMousePos([xPos, yPos])

    #print('LastMousePosOnClick : {0}'.format(gInputManager.GetLastMousePosOnClick()))
    #print('LastMousePos : {0}'.format(gInputManager.GetLastMousePos()))

def InitializeGLFW(projectName, sequence):
    displaySize = gSceneManager.GetDisplaySize()

    if not glfw.init():
        return

    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    windowTitle = projectName + '.' + sequence

    glfwWindow = glfw.create_window(displaySize[0], displaySize[1], windowTitle, None, None)

    if not glfwWindow:
        glfw.terminate()
        return

    videoMode = glfw.get_video_mode(glfw.get_primary_monitor())

    windowWidth = videoMode.size.width
    windowHeight = videoMode.size.height
    windowPosX = int(windowWidth / 2 - displaySize[0] / 2) - 267
    windowPosY = int(windowHeight / 2 - displaySize[1] / 2) - 60

    glfw.set_window_pos(glfwWindow, windowPosX, windowPosY)

    glfw.show_window(glfwWindow)    

    glfw.make_context_current(glfwWindow)

    glfw.set_window_size_callback(glfwWindow, HandleWindowSizeCallback)

    glfw.set_key_callback(glfwWindow, HandleKeyCallback) 

    glfw.set_mouse_button_callback(glfwWindow, HandleMouseButtonCallback)
    
    glfw.set_cursor_pos_callback(glfwWindow, HandleCursorPosCallback)

    return glfwWindow


def Main():    
    projectName = "Base"
    programName = "FragmentCoordinate"
    programNamePos = [1115, 17]

    glfwWindow = InitializeGLFW(projectName, 'E01')

    imgui.create_context()
    imguiRenderer = GlfwRenderer(glfwWindow, False)

    io = imgui.get_io()
    imguiNewFont = io.fonts.add_font_from_file_ttf(gSceneManager.GetResourcePath() + 'Font/comic.ttf', 14)
    imguiRenderer.refresh_font_texture()  
    
    shaders = {}

    shaders[Index.SHADER_DEFAULT] = gShaderFactory.CreateShader(Index.SHADER_VERTEX_CODE_DEFAULT, Index.SHADER_FRAGMENT_CODE_DEFAULT)
    shaders[Index.SHADER_SIMPLE_USE_UNIFORMCOLOR] = gShaderFactory.CreateShader(Index.SHADER_VERTEX_CODE_DEFAULT, Index.SHADER_FRAGMENT_CODE_SIMPLE_USE_UNIFORMCOLOR)    
    shaders[Index.SHADER_FRAGMENT_COORDINATE] = gShaderFactory.CreateShader(Index.SHADER_VERTEX_CODE_DEFAULT, Index.SHADER_FRAGMENT_CODE_FRAGMENT_COORDINATE)

    gSceneManager.InitializeOpenGL(shaders)
    gSceneManager.SetCamera(Camera())
    gSceneManager.MakeFont(imguiNewFont)
    gSceneManager.AddObject(FragmentCoordinate(programName, programNamePos))
    
    lastElapsedTime = glfw.get_time()
    deltaTime = 0.0

    while glfw.window_should_close(glfwWindow) == False:
        glfw.poll_events()        
        imguiRenderer.process_inputs()

        gSceneManager.Update(deltaTime)        

        gSceneManager.Draw()

        imgui.render()
        imguiRenderer.render(imgui.get_draw_data())

        glfw.swap_buffers(glfwWindow)

        gSceneManager.PostUpdate(deltaTime)        

        deltaTime = glfw.get_time() - lastElapsedTime
        lastElapsedTime = glfw.get_time()

    gSceneManager.Finish()

    imguiRenderer.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    Main()