# -*- coding: utf-8 -*-
"""
This class enables easy access to Koala TCP/IP remote interface
Prompt dialog for connection and login
Get functions return numpy Array
2023-03-30 Modified by TCO (all functions using Remote Manual orders)
2024.04.23 Add command to acquire a stack of data for different reconstruction distances
2024.06.20 Add comments to all functions, add new functions Koala 8.6, add function to see if commands exist in messages.xml
2024.06.21 Add new functions for sequence loading and reconstruct
2025.05.22 Force all parameters to be int if the remote want int32 type
2025.06.17 Add Photron camera functions
"""
#from pythonnet import get_runtime_info
#a = get_runtime_info()

#import python package
from pyKoalaRemote import remote_utils as ru
import numpy as np
import sys
import clr
import time
import os
import xml.etree.ElementTree as ET

#Add required dotNet reference
clr.AddReference("System")
import System
from System import Array

#Class pyRemote to manage dotNet dll in Python
class pyKoalaRemoteClient:
    
    def __init__(self, koala_8 = True, forceLogoutIfError = False):
        self.koala_8 = koala_8
        #create an instance to Koala remote Client. Version 8 and above has a new dll location
        error = False
        if koala_8 :
            #Add Koala remote librairies to Path
            remote_path = r'C:\Program Files\LynceeTec\Koala\Remote\Remote Libraries\x64'
            if not os.path.exists(remote_path):
                remote_path = r'C:\Program Files\LynceeTec\Koala Remote Test App\Libraries\x64'
                if not os.path.exists(remote_path):
                        print("User has to install Koala Remote Test App to be able to have necessary dll. Contact Lynceetec to obtain the installer")
                        error = True
            if not error:    
                sys.path.append(remote_path) #load x86 for 32 bits applications
                #Import KoalaRemoteClient
                clr.AddReference("LynceeTec.KoalaRemote.Client")
                from LynceeTec.KoalaRemote.Client import KoalaRemoteClient
                #Define KoalaRemoteClient host
                self.host = KoalaRemoteClient()
        
        else :
            #Add Koala remote librairies to Path
            sys.path.append(r'C:\Program Files\Koala\Remote Libraries\x64') #load x86 for 32 bits applications
            #Import KoalaRemoteClient
            clr.AddReference("TCPCLient")
            import KoalaClient
            #Define KoalaRemoteClient host
            self.host = KoalaClient.KoalaTCPClient()

        #init to None parameters:
        self.roiWidth = None
        self.roiHeight = None
        self.height = None
        self.width = None
        self.roiStride = None
        self.username = None
        self.totalNumberOfHologramsSequence = None
        self.configType = None #configType defined through OpenConfig, or by function SetConfigType
        
        #init state for disconnecting
        self.sampleWinState = False 
        self.connectionState = False #connect and logged
        self.forceLogoutIfError = forceLogoutIfError
        self.erroroccurs = False
        
        #check if host is properly initialized
        try :
            self.host
        except :
            print("class not initialized")
            return
        
    
    def SetforceLogoutIfError(self, state):
        '''
        Force Logout is an error occures if state is True

        Parameters
        ----------
        state : boolean
            state of force Logout of error

        Returns
        -------
        None.

        '''
        self.forceLogoutIfError = state
        
    def AvailablesFunctions(self):
        '''
        Determine available functions in messages.xml

        Returns
        -------
        None.
        '''
        error = False
        if self.koala_8:
            messages_path = r'C:\Program Files\LynceeTec\Koala\Remote\Remote Libraries\x64\messages.xml'
            if not os.path.exists(messages_path):
                messages_path = r'C:\Program Files\LynceeTec\Koala Remote Test App\Libraries\x64\messages.xml'
                if not os.path.exists(messages_path):
                    print("User has to install Koala Remote Test App to be able to have necessary dll. Contact Lynceetec to obtain the installer")
                    error = True
        else:
            messages_path = r'C:\Program Files\Koala\Remote Libraries\x64\messages.xml'
            if not os.path.exists(messages_path):
                error = True
        if not error:   
            tree = ET.parse(messages_path)
            root = tree.getroot()
            messages_list = []
            for KMess in root.findall('{http://www.lynceetec.com/KoalaMessageList}KMess'):
                name = KMess.find('{http://www.lynceetec.com/KoalaMessageList}Name')
                command_name = name.text
                command_name = command_name.replace("'",'')
                messages_list.append(name.text)
            #add commands not in Messages.xml
            messages_list.append("Login")
            messages_list.append("Logout")
            messages_list.append("Connect")
            self.Messages_list = messages_list
            
    def PrintAvailableFunctions(self):
        '''
        Print in console the available functions

        Returns
        -------
        None.
        
        '''
        self.AvailablesFunctions()
        print(self.Messages_list)
        
    def VerifyCommandExists(self, messageTxt):
        '''
        Verify tht command exists in messages.xml (Koala version dependent)


        Returns
        -------
        boolean
            true if the command exists.
        
        '''
        self.AvailablesFunctions()
        if messageTxt in self.Messages_list:
            print("Command: ", messageTxt, "exists")
            return True
        else:
            print("Command: ", messageTxt, "does not exist in messages.xml")
            return False
        
    def Error(self, err):
        '''
        Print error if the error is coming from Koala.
        
        Returns
        -------
        None.
        '''
        print("Function: "+str(err.FunctionName)+":("+str(err.ErrorCode)+")="+err.ErrorMessage)
        if self.forceLogoutIfError:
            self.__del__()
        self.erroroccurs = True
        return None
        
    def ConnectAndLoginDialog(self) :
        '''
        Dialog for connection and login to Koala

        Returns
        -------
        boolean
            true if the connection and login were successful.

        '''
        if not self.connectionState:
            #Ask for IP adress
            IP = ru.get_input('Enter host IP adress','localhost')
            #Connect to Koala
            if self.Connect(IP):
                print('connected to Koala as',self.username,'on ',IP)
            else:
                print('connection to Koala failed on :',IP)
                print('Check if Koala is started or if the production window is open or if the previous session was closed')
                return False
            
            #ask for username password
            password = ru.get_input('Enter password for '+self.username+' account', self.username)
            #Login with username password
            if self.Login(password) :
                print('Log as ',self.username,)
                self.connectionState = True
            else :
                print('Login failed for',self.username,)
                self.connectionState = False
        return self.connectionState
    
    def Connect(self, hostName, quiet=True):
        '''
        Connects the client remote application to the Koala remote server.

        Parameters
        ----------
        hostName : string
            The IP of the computer where Koala is running. Use localhost if running on the same computer
        quiet : boolean
            Deprecated parameter, will be removed in a later version. Set either to true or false

        Returns
        -------
        ret : boolean
            true if the connection was successful.

        '''
        self.username = ''
        ret, self.username = self.host.Connect(hostName,self.username,quiet)
        return ret
            
    def Login(self, password):
        '''
        Login for the remote client.

        Parameters
        ----------
        password : string
            The password for the current Koala user

        Returns
        -------
        true if the login was successful.

        '''
        if self.host.Login(password):
            self.connectionState = True
        else:
            self.connectionState = False
        return self.connectionState
    
    def ConnectAndLoging(self, password='admin', IP='localhost'):
        '''
        

        Parameters
        ----------
        password : string, optional
            Password for the Koala login. The default is 'admin' for the account admin.
        IP : Int, optional
            DHM computer IP. The default is 'localhost'.

        Returns
        -------
        true if connection and login was successful
    

        '''
        if self.Connect(IP):
            self.connectionState = self.host.Login(password)
            if not self.connectionState:
                print('Login failed for',self.username,)
                
        else:
            print('connection to Koala failed on :',IP)
            self.connectionState = False
        return self.connectionState
    
    def Logout(self,delete=False) :
        '''
        Logout for the remote client and disconnects the TCP client without waiting for an answer before returning.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            if self.connectionState:
                if self.sampleWinState:
                    #to avoid opening two sample windows is not close it before Logout
                    self.host.CloseSampleWin()
                try : 
                    self.host.Logout()
                    self.connectionState = False
                except : 
                    print("Logout failed")
                    return
                print("Logout succesfull")
            else:
                if delete is False:
                    print("Cannot Logout as the connection is False")
                return
        
    def __del__(self):
        self.Logout(True)
    
    def AccessAndReconstructHologramFromLoadedSequence(self, hologramNumber):
        '''
        Access and reconstruct the hologram "holograNumber" from previous loaded sequence(see LoadSequence)

        Parameters
        ----------
        hologramNumber : Int32
            Hologram number of the sequence to reconstruct.

        Returns
        -------
        void (nothing)
        
        Remark: the acquired holograms numbering is from 0 to N-1 but hologramNumber is defined between 1 and N.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            if self.totalNumberOfHologramsSequence is not None:
                hologramNumber = int(hologramNumber)
                if hologramNumber >0 and hologramNumber <= self.totalNumberOfHologramsSequence:
                    return self.host.AccessAndReconstructHologramFromLoadedSequence(hologramNumber)
                else:
                    print("hologramNumber ("+str(hologramNumber)+ ") is 0 or larger than maximal value ("+str(self.totalNumberOfHologramsSequence))
                    return
            else:
                print("No sequence is loaded, perform a LoadSequence(seqpath) first")
                return
    
    def OpenConfigDialog(self) :
        '''
        Open a dialog to enter a configuration ID number (Int32)
        
        Returns
        -------
        void (nothing) Koala version < 8.6.48015.0
        configType : Int32
            1 for single wavelength configuration, 2 for dual wavelength configuration, from Koala version >= 8.6.48015.0

        '''
        #get config Id
        configNumber = ru.get_input('Enter configuration number', default='137')
        configNumber = (int)(configNumber)
        #open config
        return self.OpenConfig(configNumber)

   
    def OpenConfig(self, configNumber) :
        '''
        Opens the selected configuration.
        
        Parameters
        ----------
        configNumber : Int32
            ID of the Measurement Configuration to open

        Returns
        -------
        void (nothing) Koala version < 8.6.48015.0
        configType : Int32
            1 for single wavelength configuration, 2 for dual wavelength configuration, from Koala version >= 8.6.48015.0

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try :
                configNumber = (int)(configNumber)
                self.configType = self.host.OpenConfig(configNumber)
                return self.configType
    
            except Exception as err:
                return self.Error(err)
            print("Configuration",configNumber,"open")
            #wait for older koala version
            if not self.koala_8 :
                time.sleep(2) # 2 seconds to wait for OPL to move if DHM was re-init
            return None
   
    def updateROI(self) :
        '''
        Update the ROI to be able to construct numpy array of float (intensity or phase ).

        Returns
        -------
        (int)(roiStride *roiHeight)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            self.roiWidth = self.GetPhaseWidth()
            self.roiHeight = self.GetPhaseHeight()
            if self.roiWidth is not None and self.roiHeight is not None:
                if self.roiWidth % 4 == 0:
                    self.roiStride = self.roiWidth
                else : 
                    self.roiStride = (int(self.roiWidth / 4) * 4) + 4;
                return int(self.roiStride * self.roiHeight)
            else:
                return
    
    def GetAxesPosMu(self) :
        '''
        Return current positions of the stage axes, in [um]
        
        Parameters
        ----------
        None 

        Returns
        -------
        AxesPos : numpy array
            numpy array of position of Axes (x,y,z, theta)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                #Define a dotNet (C#) Double Array
                buffer = Array.CreateInstance(System.Double,4)
                self.host.GetAxesPosMu(buffer)
                #copy and return buffer
                return ru.dn2np(buffer)
            except Exception as err:
                return self.Error(err)
    
    def GetHoloImage(self) :
        '''
        Copies the current hologram image
        
        Parameters
        ----------
        None 

        Returns
        -------
        HoloImage : numpy array
            numpy array of the hologram

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            #Define a dotNet (C#) Byte Array
            self.width = self.GetHoloWidth();
            self.height = self.GetHoloHeight();
            buffer = Array.CreateInstance(System.Byte,self.height*self.width)
            #Get holo from Koala
            try:
                self.host.GetHoloImage(buffer)
                #copy, reshape and return buffer
                return np.reshape(ru.dn2np(buffer),(self.height,self.width))
            except Exception as err:
                return self.Error(err)
    
    def GetIntensity32fImage(self) :
        '''
        Return the current intensity (amplitude), as a floating point numpy array.
        
        Parameters
        ----------
        None 

        Returns
        -------
        Intensity32Image : numpy array of float
            numpy array of the displayed intensity in Koala

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            self.updateROI()
            #Define a dotNet (C#) Single Array
            if self.roiHeight is not None and self.roiWidth is not None:
                buffer = Array.CreateInstance(System.Single,self.roiHeight*self.roiWidth)
                try:
                    self.host.GetIntensity32fImage(buffer)
                    #copy, reshape and return buffer
                    return np.reshape(ru.dn2np(buffer),(self.roiHeight,self.roiWidth))
                except Exception as err:
                    return self.Error(err)
            else:
                return
    
    def GetIntensityImage(self) :
        '''
        Return the current intensity (amplitude) image, as a grayscale numpy array (8 bits)
        
        Parameters
        ----------
        None 

        Returns
        -------
        Intensity Image : numpy array of Intf32
            numpy array of the displayed image intensity in Koala

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            size = self.updateROI()
            if size is not None:
                #Define a dotNet (C#) Byte Array
                buffer = Array.CreateInstance(System.Byte,size)
                try:
                    self.host.GetIntensityImage(buffer)
                    #copy, reshape and return buffer
                    return np.reshape(ru.dn2np(buffer),(self.roiHeight,self.roiStride))[:,0:self.roiWidth]
                except Exception as err:
                    return self.Error(err)
            else:
                return

    def GetIntensityProfile(self):
        '''
        Return  the current intensity (amplitude) profile data
        
        Parameters
        ----------
        None 

        Returns
        -------
        Intensity Profile line : numpy array of float
            numpy array of the Intensity profile

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            # Define a dotNet (C#) Double Array
            buffer = Array.CreateInstance(System.Double, self.GetIntensityProfileLength())
            try:
                self.host.GetIntensityProfile(buffer)
                # copy and return buffer
                return ru.dn2np(buffer)
            except Exception as err:
                return self.Error(err)

    def GetPhase32fImage(self) :
        '''
        Return the current phase image, as a floating point numpy array (32 bits)
        
        Note:
        ----------
            Contrary to the GetIntensity32fImage function, if a mask is active, the returned image contains the mask information (masked pixels are set to NaN).


        Parameters
        ----------
        None 

        Returns
        -------
        Phase32Image : numpy array of float (radian)
            numpy array of the displayed phase in Koala

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            self.updateROI()
            if self.roiHeight is not None and self.roiWidth is not None:
                #Define a dotNet (C#) Single Array
                buffer = Array.CreateInstance(System.Single,self.roiHeight*self.roiWidth)
                try:
                    self.host.GetPhase32fImage(buffer)
                    #copy, reshape and return buffer
                    return np.reshape(ru.dn2np(buffer),(self.roiHeight,self.roiWidth))
                except Exception as err:
                    return self.Error(err)
            else:
                return
    
    def GetPhaseImage(self) :
        '''
        Return the current phase image, as a grayscale numpy array (8 bits)
        
        Parameters
        ----------
        None 

        Returns
        -------
        Phase Image : numpy array of Intf32
            numpy array of the displayed image phase in Koala

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            #Define a dotNet (C#) Byte Array
            size = self.updateROI()
            if size is not None:
                buffer = Array.CreateInstance(System.Byte,size)
                try:
                    self.host.GetPhaseImage(buffer)
                    #copy, reshape and return buffer
                    return np.reshape(ru.dn2np(buffer),(self.roiHeight,self.roiStride))[:,0:self.roiWidth]
                except Exception as err:
                    return self.Error(err)
            else:
                return
    
    def GetPhaseProfile(self) :
        '''
        Return  the current phase profile data
        
        Parameters
        ----------
        None 

        Returns
        -------
        Phase Profile line : numpy array of float
            numpy array of the Phase profile

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            #Define a dotNet (C#) Double Array
            buffer = Array.CreateInstance(System.Double,self.GetPhaseProfileLength())
            try:
                self.host.GetPhaseProfile(buffer)
                #copy and return buffer
                return ru.dn2np(buffer)
            except Exception as err:
                return self.Error(err)
    
    def GetPhaseProfileAxis(self):
        '''
        Return  the current phase profile x axis
        
        Parameters
        ----------
        None 

        Returns
        -------
        x Axis value of Profile : numpy array of float
            numpy array of the x Axis that depends on pixel size

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            return np.arange(self.GetPhaseProfileLength()) * self.GetPxSizeUm()
    
    #wrapper for remote function, direct call
    def AccWDSearch(self, distUM, stepUM) :
        '''
        Performs an accurate working distance search.
        
        Note that this function is blocking, like all remote functions, and might take several minutes, depending on the chosen parameters.


        Parameters
        ----------
        distUM : float
            distance in um to perform accurate Working Distance Search
        stepUM: float
            step to perform accurate Working Distance Search

        Returns
        -------
        void (nothing)

        '''
        distUM = (float)(distUM)
        stepUM = (float)(stepUM)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.AccWDSearch(distUM,stepUM)
            except Exception as err:
                return self.Error(err)
    
    def Acquisition2L(self):
        '''
        Acquires an image (or several if temporal averaging is on) and reconstruct it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.Acquisition2L()
            except Exception as err:
                return self.Error(err)
    
    def AddCorrSegment(self, top, left, length, orientation):
        """
        Add Correction segments
        
        Parameters
        ----------
        top : Int32
            Y coordinate of the top left point of the segment, in pixel
        left: Int32
            X coordinate of the top left point of the segment, in pixel
        length : Int32
            Length of the segment, in pixel
        orientation : Int32
            Orientation of the segment: 0 = horizontal, 1 = vertical
        
        Returns
        -------
        void (nothing)
        """
        top = (int)(top)
        left = (int)(left)
        length = (int)(length)
        orientation = (int)(orientation)
        #left+length cannot be larger than width
        #top+length cannot be larger than height
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            if self.roiWidth is None or self.roiHeight is None:
                self.updateROI()
            if self.roiWidth is not None and self.roiHeight is not None:
                if orientation == 0:
                    if left+length > self.roiWidth:
                        length = self.roiWidth-left
                if orientation == 1:
                    if top+length > self.roiHeight:
                        length = self.roiHeight-top 
                try:
                    return self.host.AddCorrSegment(top,left,length,orientation)
                except Exception as err:
                    return self.Error(err)
            else:
                return
    
    def AddCorrZone(self, top, left, width, height):
        """
        Adds a phase correction zone (for 2D tilt correction)
        
        Parameters
        ----------
        top : Int32
            Y coordinate of the top left point of the segment, in pixel
        left: Int32
            X coordinate of the top left point of the segment, in pixel
        width : Int32
            Width of the zone, in pixel
        height : Int32
            Height of the zone, in pixel
        
        Returns
        -------
        void (nothing)
        """
        top = (int)(top)
        left = (int)(left)
        width = (int)(width)
        height = (int)(height)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            if self.roiWidth is None or self.roiHeight is None:
                self.updateROI()
            if self.roiWidth is not None and self.roiHeight is not None:
                if left+width > self.roiWidth:
                    width = self.roiWidth-left
                if top+height > self.roiHeight:
                    height= self.roiHeight-top
         
                try:
                    return self.host.AddCorrZone(top, left, width, height)
                except Exception as err:
                    return self.Error(err)
            else:
                return


    def AddPhaseOffsetAdjustmentZone(self, top, left, width, height):
        """
        Adds a phase offset adjustment zone
        
        Parameters
        ----------
        top : Int32
            Y coordinate of the top left point of the segment, in pixel
        left: Int32
            X coordinate of the top left point of the segment, in pixel
        width : Int32
            Width of the zone, in pixel
        height : Int32
            Height of the zone, in pixel
        
        Returns
        -------
        void (nothing)
        """
        top = (int)(top)
        left = (int)(left)
        width = (int)(width)
        height = (int)(height)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.AddPhaseOffsetAdjustmentZone(top, left, width, height)
            except Exception as err:
                return self.Error(err)

    def AlgoResetPhaseMask(self):
        """
        Resets the current user mask for the phase tilt correction to the values saved in the database.

        Returns
        -------
        void (nothing)
        """
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.AlgoResetPhaseMask()
            except Exception as err:
                return self.Error(err)

    def AxisInstalled(self, axisId):
        '''
        Gets a value indicating if an axis is installed for the current stage.
        
        Parameters
        ----------
        axisId : Int32
            0: X axis
            1: Y axis
            2: Z axis
            3: Theta axis (rotation, system-dependent)
            4: Phi axis (rotation, system-dependent)
            5: Psi axis (rotation, system-dependent)
        Returns
        -------
        axis installed : boolean
            return if the axis is installed
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.AxisInstalled(axisId)
            except Exception as err:
                return self.Error(err)

    def ComputePhaseCorrection(self, fitMethod, degree):
        """
        Computes the 1D phase correction using a specific method.
        
        Parameters
        ----------
        fitMethod : Int32
            0 : Tilt. In this case, degree is forced to 1
            1: Polynomial
            4: Polynomial 2D
        degree : Int32
            Degree of the correction. Value must be a positive non-zero integer, forced to be 1 if fitMethod=0
        """
        fitMethod = (int)(fitMethod)
        degree = (int)(degree)
        if fitMethod == 0:
            degree = 1 #cannot use other order for fitMethod = 1
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ComputePhaseCorrection(fitMethod, degree)
            except Exception as err:
                return self.Error(err)
    
    def CloseFourierWin(self):
        '''
        Close the Fourier window.

        Returns
        -------
        void (nothing)
        
        Remark: exist only from Koala version >= 8.6.48015.0

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseFourierWin()
            except Exception as err:
                return self.Error(err)
            
    def CloseHoloWin(self):
        '''
        Close the hologram window.

        Returns
        -------
        void (nothing)
        
        Remark: exist only from Koala version >= 8.6.48015.0

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseHoloWin()
            except Exception as err:
                return self.Error(err)
        
    def CloseIntensityWin(self):
        '''
        Close the intensity (amplitude) window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseIntensityWin()
            except Exception as err:
                return self.Error(err)


    def ClosePhaseWin(self):
        '''
        Close the phase window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ClosePhaseWin()
            except Exception as err:
                return self.Error(err)

    def CloseAllWin(self):
        '''
        Close Hologram, Intensity and phase windows.
        
        Returns
        -------
        void (nothing)
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        self.CloseHoloWin()
        self.CloseIntensityWin()
        self.ClosePhaseWin()
        
    def CloseReconstructionSettingsWin(self):
        '''
        Close the Reconstruction Settings window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseReconstructionSettingsWin()
            except Exception as err:
                return self.Error(err)
    
    def DigitizerAcquiring(self):
        '''
        Gets a value indicating if the camera is currently in continuous grab mode or not.

        Returns
        -------
        Boolean: true if the camera is in continuous grab mode

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.DigitizerAcquiring()
            except Exception as err:
                return self.Error(err)

    def ExtractIntensityProfile(self, startX, startY, endX, endY):
        '''
        Extracts a profile from the intensity image and plots it in the intensity profile window.

        Parameters
        ----------
        startX : Int32
            X coordinate of the starting point of the profile in the intensity ROI
        startY : Int32
            Y coordinate of the starting point of the profile in the intensity ROI
        endX : Int32
            X coordinate of the ending point of the profile in the intensity ROI
        endY : Int32
            Y coordinate of the ending point of the profile in the intensity ROI

        Returns
        -------
        void (nothing)

        '''
        startX =(int)(startX)
        startY = (int)(startY)
        endX = (int)(endX)
        endY = (int)(endY)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ExtractIntensityProfile(startX, startY, endX, endY)
            except Exception as err:
                return self.Error(err)

    def ExtractPhaseProfile(self, startX, startY, endX, endY):
        '''
        Extracts a profile from the phase image and plots it in the phase profile window.

        Parameters
        ----------
        startX : Int32
            X coordinate of the starting point of the profile in the phase ROI
        startY : Int32
            Y coordinate of the starting point of the profile in the phase ROI
        endX : Int32
            X coordinate of the ending point of the profile in the phase ROI
        endY : Int32
            Y coordinate of the ending point of the profile in the phase ROI

        Returns
        -------
        void (nothing)

        '''
        startX =(int)(startX)
        startY = (int)(startY)
        endX = (int)(endX)
        endY = (int)(endY)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ExtractPhaseProfile(startX, startY, endX, endY)
            except Exception as err:
                return self.Error(err)
    
    def FastWDSearch(self):
        '''
        Performs a fast working distance search.
        
        Note that this function is blocking, like all remote functions, and might take several seconds.


        Returns
        -------
        void (noting)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.FastWDSearch()
            except Exception as err:
                return self.Error(err)
    
    def GetCameraPixelSizeUm(self):
        '''
        Get the value of the camera pixel size, in [um].
        
        Returns
        -------
        
        Double:
            The camera pixel size, in [um] with 3 digits
            
        Remark: only available from Koala version >= 8.6.48015.0
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                ccd_px_size = (int)(self.host.GetCameraPixelSizeUm()*1000)/1000
                return ccd_px_size
            except Exception as err:
                return self.Error(err)
    
    def GetCameraShutterUs(self):
        '''
        Get the value of the camera shutter parameter, in [us].
        
        Returns
        -------
        
        Int32:
            The shutter value, in [us]
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetCameraShutterUs()
            except Exception as err:
                return self.Error(err)

    def GetChosenOPLPosition(self, oplId):
        '''
        Gets the non-corrected position of the OPL1 or OPL2 motor in [qc], depending on oplId (1 or 2).
        
        Parameters
        ----------
        oplId : Int32
            The OPL ID (1 or 2)

        Returns
        -------
        Int32
            The position of the OPL1 or OPL2 motor, in [qc]
        '''
        oplId = (int)(oplId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetChosenOPLPosition(oplId)
            except Exception as err:
                return self.Error(err)

    def GetDHMSerial(self):
        '''
        Gets the numerical part of the serial number of the DHM device.

        Returns
        -------
        Int32
            Serial number of the DHM device

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetDHMSerial()
            except Exception as err:
                return self.Error(err)
    
    def GetHoloContrast(self):
        '''
        Gets a value representing the contrast of the last hologram (either last one grabbed or last loaded from disk, whichever occurred last) in an area half the size of the hologram, centered in the middle of the image.

        Returns
        -------
        Double
            Value representing hologram contrast

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetHoloContrast()
            except Exception as err:
                return self.Error(err)
    
    def GetHoloHeight(self):
        '''
        Gets the height of the hologram image, according to the current configuration.

        Returns
        -------
        Int32
            Hologram Height

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetHoloHeight()
            except Exception as err:
                return self.Error(err)
    
    def GetHoloWidth(self):
        '''
        Gets the width of the hologram image, according to the current configuration.

        Returns
        -------
        Int32
            Hologram Width

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetHoloWidth()
            except Exception as err:
                return self.Error(err)

    def GetIntensityProfileLength(self):
        '''
        Gets the length of the current intensity profile array.

        Returns
        -------
        Int32
            length of the current intensity profile

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetIntensityProfileLength()
            except Exception as err:
                return self.Error(err)

    def GetKoalaVersion(self):
        '''
        Gets the current Koala version number.

        Returns
        -------
        string
            The version number as a string value.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetKoalaVersion()
            except Exception as err:
                return self.Error(err)

    def GetLambdaNm(self, srcId, useLogicalId=True):
        '''
        Gets the wavelength of a laser source, in [nm].

        Parameters
        ----------
        srcId : Int32
            The id of the source (logical or physical according to useLogicalId)
        useLogicalId : Boolean, optional
            Set to true to use logical id, to false to use physical id.  The default is True.

        Returns
        -------
        Single
            The wavelength of the source, in [nm]

        '''
        srcId = (int)(srcId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetLambdaNm(srcId, useLogicalId)
            except Exception as err:
                return self.Error(err)

    def GetMeasurementInformation(self, path, filename):
        '''
        Saves the current measurement information.

        Parameters
        ----------
        path : string
            path to save the data.
        filename : string
            filename to save the content of the measurement information.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetMeasurementInformation(path, filename)
            except Exception as err:
                return self.Error(err)

    def GetNumericalApertureFromCurrentObjective(self):
        '''
        Get the numerical aperture of the objective's current configuration.
        
        Returns
        -------
        
        Double:
            NA of the objective's current configuration. (None if NA is not defined)
            
        Remark: only available from Koala version >= 8.6.48015.0. If numerical aperture is not 
        defined in the database (NA=-1), generates an error and function return None
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                NA = self.host.GetNumericalApertureFromCurrentObjective()
                if NA == -1:
                    NA = None
                return NA
            except Exception as err:
                return self.Error(err)
    def GetOPLPos(self):
        '''
        Gets the non-corrected position of the OPL1 motor in [qc].

        Returns
        -------
        Int32
            The position of the OPL1 motor, in [qc]

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetOPLPos()
            except Exception as err:
                return self.Error(err)
    
    def GetPhaseHeight(self):
        '''
        Gets the height of the phase image ROI, according to the current configuration.
        
        Note that the intensity (amplitude) image has the same dimensions.


        Returns
        -------
        Int32
            Phase Height

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetPhaseHeight()
            except Exception as err:
                return self.Error(err)
    
    def GetPhaseWidth(self):
        '''
        Gets the width of the phase image ROI, according to the current configuration.
        
        Note that the intensity (amplitude) image has the same dimensions.


        Returns
        -------
        Int32
            Phase Width

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetPhaseWidth()
            except Exception as err:
                return self.Error(err)
    
    def GetPhaseProfileLength(self):
        '''
        Gets the length of the current phase profile array.

        Returns
        -------
        Int32
            Length of the current phase profile

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetPhaseProfileLength()
            except Exception as err:
                return self.Error(err)
    
    def GetPxSizeUm(self):
        '''
        Returns the calibrated size, in [um], represented by a pixel in the image.

        Note that this value is calibrated and configuration-dependent, because it depends on the objective used for this configuration.


        Returns
        -------
        single
            the calibrated size of a pixel, averaged between X and Y, in [um]

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetPxSizeUm()
            except Exception as err:
                return self.Error(err)
    
    def GetRecDistCM(self):
        '''
        Gets the current reconstruction distance, in [cm], of the active user processing configuration.

        Returns
        -------
        single
            The reconstruction distance, in [cm]

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetRecDistCM()
            except Exception as err:
                return self.Error(err)
    
    def GetReconstructionRoiLeft(self):
        '''
        Gets the left coordinate of the reconstruction ROI, according to the current configuration.

        Returns
        -------
        Int32
            The left coordinates of the ROI

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetReconstructionRoiLeft()
            except Exception as err:
                return self.Error(err)
    
    def GetReconstructionRoiTop(self):
        '''
        Gets the top coordinate of the reconstruction ROI, according to the current configuration.

        Returns
        -------
        Int32
            The top coordinates of the ROI

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetReconstructionRoiTop()
            except Exception as err:
                return self.Error(err)
    
    def GetReconstructionRoiWidth(self):
        '''
        Gets the width of the reconstruction ROI, according to the current configuration.

        Returns
        -------
        Int32
            The width the ROI

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetReconstructionRoiWidth()
            except Exception as err:
                return self.Error(err)
    
    def GetReconstructionRoiHeight(self):
        '''
        Gets the height of the reconstruction ROI, according to the current configuration.

        Returns
        -------
        Int32
            The height the ROI

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetReconstructionRoiHeight()
            except Exception as err:
                return self.Error(err)
    
    def GetReconstructionRoi(self):
        '''
        Gets the top, left, coordinates and width, height of the reconstruction
        ROI, according to the current configuration.

        Returns
        -------
        Int32, Int32, Int32, Int32
            Left, top, width, height of the reconstruction ROI
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            top = self.GetReconstructionRoiTop()
            left = self.GetReconstructionRoiLeft()
            height = self.GetReconstructionRoiHeight()
            width = self.GetReconstructionRoiWidth()
            return left, top, width, height
    
    def GetTotalNumberOfHologramsFromSequence(self, seqpath):
        '''
        Get total number of hologram in a sequence. 

        Parameters
        ----------
        seqpath : string
            sequence path of the sequence

        Returns
        -------
        Int32
            Total number of holograms in the sequence.
        
        Remark: Holograms numbering is from 0 to N-1 but to reconstruct the first hologram is 1 and the last N.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                self.totalNumberOfHologramsSequence = self.host.GetTotalNumberOfHologramsFromSequence(seqpath)
                return self.totalNumberOfHologramsSequence
            except Exception as err:
                return self.Error(err)
        
    def GetUnwrap2DState(self):
        '''
        Gets a value indicating if the unwrapping of the phase image is enabled or not.

        Returns
        -------
        Boolean

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.GetUnwrap2DState()
            except Exception as err:
                return self.Error(err)

    def InitXYZStage(self, withProgressBar=False, moveToCenter=False):
        '''
        Moves the axes of the XYZ stage to their minimal position. 
        Please use with caution as moving to the minimal positions (X=0, Y=0, Z=0)
        may damage your stage if it is not correctly calibrated.


        Parameters
        ----------
        withProgressBar : Boolean, optional
            If set to true, the progress bar will be displayed. (Note that progress
            tracking might not be implemented depending of your type of stage. In this case
            the progress bar will simply remain on 0.) Optional, default value is False.
        moveToCenter : Boolean, optional
            If set to true, will move the stage to the center of each axis range afterwards.
            Optional, default value is False.

        Returns
        -------
        Boolean
            returns true if the operation was successful.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.InitXYZStage(withProgressBar, moveToCenter)
            except Exception as err:
                return self.Error(err)
    
    def KoalaShutDown(self, confirm=False):
        '''
        Closes Koala. This function is not blocking and will return before execution is finished.

        Parameters
        ----------
        confirm : Boolean, optional
            True to display the dialog to ask for confirmation, False to close without the need for user input.
            Optional, default value is False.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.KoalaShutDown(confirm)
            except Exception as err:
                return self.Error(err)
    
    def LoadAndReconstructHologramFromSequence(self, seqpath, hologramNumber):
        '''
        Load and reconstruct hologram from a sequence. The sequence is not loaded, 
        so it could be more time consuming for a large sequence. See LoadSequence and 
        AccessAndReconstructHologramFromLoadedSequence to avoir reloading sequence.

        Parameters
        ----------
        seqpath : string
            Sequence path
        hologramNumber : Int32
            Hologram number to load and reconstruct. 

        Returns
        -------
        void (nothing).
        
        Remark: hologram acquisition numbering is from 0 to N-1 but hologramNumber is defined between 1 and N.

        '''
        hologramNumber = (int)(hologramNumber)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                N = self.GetTotalNumberOfHologramsFromSequence(seqpath)
                self.totalNumberOfHologramsSequence = N
                hologramNumber = int(hologramNumber)
                if self.totalNumberOfHologramsSequence is not None:
                    if hologramNumber > 0 and hologramNumber <= self.totalNumberOfHologramsSequence:
                        return self.host.LoadAndReconstructHologramFromSequence(seqpath, hologramNumber)
                    else:
                        print("Error : hologramNumber has to be larger than 0 and smaller than total number of holograms ("+str(self.totalNumberOfHologramsSequence)+")")
                else:
                    print("Error with GetTotalNumberOfHolograms, return None")
            except Exception as err:
                return self.Error(err)
        
    def LoadHolo(self, path, numLambda=None):
        '''
        Loads an hologram from the disk. In order to get a correct phase and intensity
        reconstruction of the hologram, it should be loaded with the configuration
        that was used to record it [by default numLambda is None -> use configType defined manually or automatically (Koala version >= 8.6.48015.0)].
        If the hologram window is not opened yet, it will be opened automatically.

        Parameters
        ----------
        path : string
            Full path of the hologram file. It is recommended to only work with files in .tif format.
        numLambda : Int32
            The number of wavelengths of the configuration with which the hologram was taken (1 or 2). Default is None (use self.configType defined manually or automatically from Koala Version >= 8.6.48015.0)

        Returns
        -------
        void (nothing)

        '''
        if numLambda is None:
            numLambda = self.configType
        if numLambda is not None:
            if self.erroroccurs and self.forceLogoutIfError:
                return
            else:
                try:
                    return self.host.LoadHolo(path, numLambda)
                except Exception as err:
                    return self.Error(err)
        else:
            print("numLambda is not defined. Set the configType or defined numLamdbda in the function ")
            
    def LoadHologram(self, path):
        '''
        Loads an hologram from the disk. In order to get a correct phase and intensity
        reconstruction of the hologram. If the hologram window is not opened yet, it will
        be opened automatically.

        Parameters
        ----------
        path : string
            Full path of the hologram file. It is recommended to only work with files in .tif format.

        Returns
        -------
        void (nothing)
        
        Remark: Only available from Koala version >= 8.6.48015.0. For previous version uses "LoadHolo(path, numLambda)"

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.LoadHologram(path)
            except Exception as err:
                return self.Error(err)
        
    def LoadSequence(self, seqpath):
        '''
        Load a sequence from a path.

        Parameters
        ----------
        seqpath : string
            Sequence path.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.LoadSequence(seqpath)
            except Exception as err:
                return self.Error(err)
            
    def LoadSequenceWithTotalNumberOfHolograms(self, seqpath):
        '''
        Load sequence and define total number of holograms of the sequence

        Parameters
        ----------
        seqpath : string
            Sequence path

        Returns
        -------
        None.

        '''
        N = self.GetTotalNumberOfHologramsFromSequence(seqpath)
        self.LoadSequence(seqpath)
        return N
        
    def ModifyFilterSwitchStatus(self, state):
        '''
        Enables/Disables the optical filter switch motor, accessible in the Motors control panel from the Tools menu.
        
        Parameters
        ----------
        state : boolean
            true to enable the filter switch motor, false to disable it
            
        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ModifyFilterSwitchStatus(state)
            except Exception as err:
                return self.Error(err)

    def MoveAxes(self, absMove, mvX, mvY, mvZ, mvTh, distX, distY, distZ, distTh, accX, accY, accZ, accTh, waitEnd=True):
        '''
        Moves several axes of the stage simultaneously.

        Parameters
        ----------
        absMove : boolean
            Set to true for an absolute move, set to false for a relative move.
        mvX : boolean
            Set to true to move the X axis.
        mvY : boolean
            Set to true to move the Y axis.
        mvZ : boolean
            Set to true to move the Z axis.
        mvTh : boolean
            Set to true to move the Theta axis.
        distX : float (double)
            Absolute position or distance to move for the X axis. In [um].
        distY : float (double)
            Absolute position or distance to move for the Y axis. In [um].
        distZ : float (double)
            Absolute position or distance to move for the Z axis. In [um].
        distTh : float (double)
            Absolute position or distance to move for the Theta axis. In [um].
        accX : float (double)
            Accuracy of the move for the X axis, in [um]. 
        accY : float (double)
            Accuracy of the move for the Y axis, in [um]. 
        accZ : float (double)
            Accuracy of the move for the Z axis, in [um]. 
        accTh : float (double)
            Accuracy of the move for the Theta axis, in [um]. 
        waitEnd : boolean, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        boolean
            True if the operation completed successfully.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.MoveAxes(absMove, mvX, mvY, mvZ, mvTh, distX, distY, distZ, distTh, accX, accY, accZ, accTh, waitEnd)
            except Exception as err:
                return self.Error(err)
        
    def MoveAxesArr(self, axes, absMove, dist, acc, waitEnd=True):
        '''
        Moves several axes of the stage simultaneously.

        Parameters
        ----------
        axes : boolean[]
            Array of 4 booleans for the X, Y, Z and Theta axes respectively, to indicate if the axis must be moved or not (set to true to move).
        absMove : boolean
            Set to true for an absolute move, set to false for a relative move.
        dist : Double[]
            Array of 4 double for the X, Y, Z and Theta axes respectively, for the absolute position or distance to move for each axis. In [um]
        acc : Double[]
            Array of 4 double for the X, Y, Z and Theta axes respectively, for the accuracy of the move for each axis. In [um].
        waitEnd : boolean, optional
            If set to true, the function will only return after the move is completed. Optional, default value is true.

        Returns
        -------
        boolean
            True if the operation completed successfully.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.MoveAxesArr(axes, absMove, dist, acc, waitEnd)
            except Exception as err:
                return self.Error(err)
    
    def MoveAxis(self, axisId, absMove, distUm, accuracyUM, waitEnd=True):
        '''
        Moves a single axis of the stage.

        Parameters
        ----------
        axisId : Int32
            0: X axis
            1: Y axis
            2: Z axis
            3: Theta axis (rotation, system-dependent)

        absMove : boolean
            Set to true for an absolute move, set to false for a relative move.
        distUm : float (Double)
            Absolute position or distance to move. In [um].
        accuracyUM : float (Double)
            Accuracy of the move, in [um]. This parameter is ignored and will be removed in a future version.
        waitEnd : boolean, optional
            If set to true, the function will only return after the move is completed. Optional, default is True.

        Returns
        -------
        boolean
            True if the operation completed successfully.

        '''
        axisId = (int)(axisId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.MoveAxis(axisId, absMove, distUm, accuracyUM, waitEnd)
            except Exception as err:
                return self.Error(err)

    def MoveChosenOPLToPosition(self, posQc, oplId):
        '''
        Moves the OPL1 or OPL2 motor (depending on the OPL ID) to a specific position in [qc].
        Note that this function does not require a configuration to be loaded, but it doesn’t make much sense to move the OPL before loading a configuration.


        Parameters
        ----------
        posQc : Int32
            The position in qc where to move the OPL1 or OPL2 . This position corresponds to the position returned by the GetChosenOPLPosition function. The OPL will move to the absolute position posQc while taking into account the OPL compensation (factor in database, weighted by the difference between maximum position and minimum position, then divided by physical dimensions of the OPL)
        oplId : Int32
            The OPL ID (1 or 2).

        Returns
        -------
        void (nothing)

        '''
        posQc = (int)(posQc)
        oplId = (int)(oplId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.MoveChosenOPLToPosition(posQc, oplId)
            except Exception as err:
                return self.Error(err)

    def MoveOPL(self, position):
        '''
        Moves the OPL1 motor to a specific position, in [qc].
        Note that this function does not require a configuration to be loaded, but it doesn’t make much sense to move the OPL1 before loading a configuration.


        Parameters
        ----------
        position : Int32
            The position in qc where to move the OPL1. This position corresponds to the position returned by the GetOPLPos function.

        Returns
        -------
        void (nothing)

        '''
        position = (int)(position)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.MoveOPL(position)
            except Exception as err:
                return self.Error(err)
        
    def OnDistanceChange(self):
        '''
        Applies the last modification of the reconstruction distance, which will result in the recomputation of the intensity and phase images if they are available.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OnDistanceChange()
            except Exception as err:
                return self.Error(err)

    def OpenFourierWin(self):
        '''
        Opens the Fourier window

        Returns
        -------
        void (nothing)
        
        Remark: only from Koala version >= 8.6.48015.0.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenFourierWin()
            except Exception as err:
                return self.Error(err)
                
    def OpenFrmTopography(self):
        '''
        Opens the topography (roughness) window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenFrmTopography()
            except Exception as err:
                return self.Error(err)
        
    def OpenHoloWin(self):
        '''
        Opens the hologram window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenHoloWin()
            except Exception as err:
                return self.Error(err)
    
    def OpenIntensityWin(self, updateXYScale=True):
        '''
        Opens the intensity (amplitude) window

        Parameters
        ----------
        updateXYScale : boolean, optional
            If set to true, the scale displayed in the Intensity Image window will be updated. Optional, default value is True.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenIntensityWin(updateXYScale)
            except Exception as err:
                return self.Error(err)
    
    def OpenPhaseWin(self, withoutColorbar=False, doReconstruction=True, updateXYScale=True):
        '''
        Opens the phase window

        Parameters
        ----------
        withoutColorbar : boolean, optional
            If set to true, the phase window will not have a color bar. Optional, default value is False.
        doReconstruction :boolean, optional
            If set to true, a full reconstruction will be performed after the phase image is opened, which will update its content. Optional, default value is True (recommended).
        updateXYScale : boolean, optional
            If set to true, the scale displayed in the Phase Image window will be updated. Optional, default value is True.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenPhaseWin(withoutColorbar, doReconstruction, updateXYScale)
            except Exception as err:
                return self.Error(err)
    

    def OpenAllWindows(self, withoutColorbar=False, doReconstruction=True, updateXYScale=True):
        '''
        Open all windows (hologram, intensity and phase)
    
        Parameters
        ----------
        withoutColorbar : boolean, optional
            If set to true, the phase window will not have a color bar. Optional, default value is False.
        doReconstruction :boolean, optional
            If set to true, a full reconstruction will be performed after the phase image is opened, which will update its content. Optional, default value is True (recommended).
        updateXYScale : boolean, optional
            If set to true, the scale displayed in the Phase Image window will be updated. Optional, default value is True.
    
        Returns
        -------
        None.
    
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            self.OpenHoloWin()
            self.OpenIntensityWin(updateXYScale)
            self.OpenPhaseWin(withoutColorbar, doReconstruction, updateXYScale)
    
    def OpenReconstructionSettingsWin(self):
            '''
            Opens the reconstruction settings window
    
            Returns
            -------
            void (nothing)
    
            '''
            if self.erroroccurs and self.forceLogoutIfError:
                return
            else:
                try:
                    return self.host.OpenReconstructionSettingsWin()
                except Exception as err:
                    return self.Error(err)
    
    def ResetReconstructionRoi(self):
        '''
        Removes the ROI on the reconstruction (Phase and Intensity). The phase and intensity size corresponds to the whole hologram image size.

        ! IMPORTANT ! Do not save the configuration in this state, as Koala will not be able to reload it.

        ! IMPORTANT ! Do not call this function twice in a row: Koala forbids it.


        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ResetReconstructionRoi() 
            except Exception as err:
                return self.Error(err)
    
    def ResetCorrSegment(self):
        '''
        Reset the phase correction segments.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ResetCorrSegment()
            except Exception as err:
                return self.Error(err)

    def ResetCorrZone(self):
        '''
        Reset the phase correction zones.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ResetCorrZone()
            except Exception as err:
                return self.Error(err)

    def ResetGrab(self):
        '''
        Stops the continuous acquisition of the camera if it was ON.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ResetGrab()
            except Exception as err:
                return self.Error(err)

    def ResetPhaseOffsetAdjustmentZone(self):
        '''
        Reset the phase offset adjustment zones.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ResetPhaseOffsetAdjustmentZone()
            except Exception as err:
                return self.Error(err)

    def ResetUserDefinedMaskZone(self):
        '''
        Remove all user defined mask zones on the Phase.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ResetUserDefinedMaskZone()
            except Exception as err:
                return self.Error(err)

    def SaveImageFloatToFile(self, winId, fileName, useBinFormat=False):
        '''
        Saves a 32 bits image on the disk, as .bin or .txt.
        Note that the function does not return an error if the low-level saving operation failed.

        Parameters
        ----------
        winId : Int32
            1: hologram
            2: amplitude image
            4: phase image
            8: Fourier image
            For amplitude, phase and Fourier images, what exact type of image is saved (Lambda 1 only, Lambda 2 only, short or long synthetic wavelength or wavelength mapping) depends on the selected image in the corresponding window.
            Values cannot be combined. To save several images, call the function several times.

        fileName : string
            Full path of the destination file. The extension has no influence on the file format, which is determined by the useBinFormat parameter. However it is recommended to use the correct extension to avoid confusion when working with the file later on.        
        useBinFormat: boolean
            Set to true to save as .bin file, false to save as .txt. Optional, default value is False.
            
        Returns
        -------
        void (nothing)
        
        '''
        winId = (int)(winId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SaveImageFloatToFile(winId, fileName, useBinFormat)
            except Exception as err:
                return self.Error(err)
    
    def SaveImageToFile(self, winId, fileName):
        '''
        Saves an 8 bits image on the disk, as tiff, png or jpeg. If the directory does not exist, it will be created.
        Note that the function does not return an error if the low-level saving operation failed


        Parameters
        ----------
        winId : Int32
            1: hologram
            2 : amplitude image
            4 : phase image
            8 : Fourier image
            For amplitude, phase and Fourier images, what exact type of image is saved (Lambda 1 only, Lambda 2 only, short or long synthetic wavelength or wavelength mapping) depends on the selected image in the corresponding window.
            Values cannot be combined. To save several images, call the function several times.

        fileName : string
            Full path of the destination file. The file format will be defined according to the extension. If no extension is given, the file will be recorded in tiff format. It is recommended to save holograms as .tif if you intend to load them again for further processing.
            Possible extension values are
                .png 
                .jpg
                .tiff or .tif


        Returns
        -------
        void (nothing)

        '''
        winId = (int)(winId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SaveImageToFile(winId, fileName)
            except Exception as err:
                return self.Error(err)

    def SaveReconstructionSettings(self):
        '''
        Save the reconstruction settings window

        Returns
        -------
        void (nothing).

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SaveReconstructionSettings()
            except Exception as err:
                return self.Error(err)

    def SelectDisplayWL(self, winId):
        '''
        Select the specific type of wavelength (WL) to display in the phase, amplitude or Fourier window.
        
        Parameters
        ----------
        winId : Int32
            8192: phase lambda 1 image
            16384: phase lambda 2 image
            32768: phase long synthetic wavelength image
            65536: phase short synthetic wavelength image
            2048: amplitude (intensity) lambda 1 image
            4096: amplitude (intensity) lambda 2 image
            512: Fourier lambda 1 image
            1024: Fourier lambda 2 image
            Values cannot be combined.To display several images, call the function several times.
            
        Returns
        -------
        void (nothing)
        
        '''
        winId = (int)(winId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SelectDisplayWL(winId)
            except Exception as err:
                return self.Error(err)
    
    def SelectTopoZone(self, top, left, width, height):
        '''
        Selects an area for topographic (roughness) measurement.

        Parameters
        ----------
        top : Int32
            Y coordinate of the top left point of the zone, in pixel
        left : Int32
            X coordinate of the top left point of the zone, in pixel
        width : Int32
            width of the zone, in pixel
        height : Int32
            height of the zone, in pixel

        Returns
        -------
        void (nothing)

        '''
        top = (int)(top)
        left = (int)(left)
        width = (int)(width)
        height = (int)(height)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SelectTopoZone(top, left, width, height)
            except Exception as err:
                return self.Error(err)

    def SetCameraShutterUs(self, shutterUs):
        '''
        Sets the shutter value of the camera, in [us].
        Note that this function does not require a configuration to be loaded, but it doesn’t make much sense to set the shutter value before loading a configuration.


        Parameters
        ----------
        shutterUs : Int32
            The shutter value for the camera, in [us]

        Returns
        -------
        void (nothing)

        '''
        shutterUs = (int)(shutterUs)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetCameraShutterUs(shutterUs)
            except Exception as err:
                return self.Error(err)
    

    def SetConfigType(self, configType):
        '''
        Set manually the configuration type (single wavelength (configType =1 ) or dual wavelength configuratinon (configType=2))

        Parameters
        ----------
        configType : Int32
            configType of the configuration. Defined automatically with OpenConfig from Koala version >= 8.6.48015.0

        Returns
        -------
        None.

        '''
        configType = (int)(configType)
        self.configType = configType
        
    def SetIntensityProfileState(self, state=False):
        '''
        Opens or closes the intensity profile window. The profile window must be opened to be able to extract the intensity profile.

        Parameters
        ----------
        state : boolean, optional
            True to open the intensity profile window, False to close it.Optional, default value is False.

        Returns
        -------
        void (nothing).

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetIntensityProfileState(state)
            except Exception as err:
                return self.Error(err)


    def SetPhaseProfileState(self, state=False):
        '''
        Opens or closes the phase profile window. The profile window must be opened to be able to extract the phase profile.

        Parameters
        ----------
        state : boolean, optional
            True to open the phase profile window, False to close it. Optional, default value is False.

        Returns
        -------
        void (nothing).

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetPhaseProfileState(state)
            except Exception as err:
                return self.Error(err)
    
    def SetRecDistCM(self, distCM):
        '''
        Sets the reconstruction distance, in [cm], for the active user processing configuration. 
        Note that the value is not saved in the database, the database value will be loaded again the next time the configuration is loaded.


        Parameters
        ----------
        distCM : float (Single)
            The reconstruction distance, in [cm]

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetRecDistCM(distCM)
            except Exception as err:
                return self.Error(err)
    
    def SetReconstructionRoi(self, left, top, width, height):
        '''
        Set the ROI of the reconstruction.

        Parameters
        ----------
        left : Int32
            The left coordinate of the ROI, in [px], in the hologram image.
        top : Int32
            The top coordinate of the ROI, in [px], in the hologram image.
        width : Int32
            The width of the ROI, in [px] (Left+Width < Width(hologram))
        height : Int32
            The height of the ROI, in [px] (Top+Height < Height(hologram))

        Returns
        -------
        void (nothing)

        '''
        top = (int)(top)
        left = (int)(left)
        width = (int)(width)
        height = (int)(height)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetReconstructionRoi(left,top, width, height)
            except Exception as err:
                return self.Error(err)

    def SetSourceState(self, srcId, state, useLogicalId=True):
        '''
        Sets a source ON or OFF.

        Parameters
        ----------
        srcId : Int32
            The id of the source (logical or physical according to useLogicalId)
        state : boolean
            Set to true to switch the source ON, false to switch it OFF
        useLogicalId : boolean, optional
            Set to true to use logical id, to false to use physical id. Optional, default value is True.

        Returns
        -------
        void (nothing)
        '''
        srcId = (int)(srcId)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetSourceState(srcId, state, useLogicalId)
            except Exception as err:
                return self.Error(err)
    
    def SetUnwrap2DMethod(self, method):
        '''
        Sets the method used for unwrapping. 
        Note that unwrapping will not take place until it has been enabled with SetUnwrap2DState.
        method
        Parameters
        ----------
        method : Int32
            0: Discrete Cosine Transform (DCT)
            1: Path-following (also known as Quality Path)
            2: Preconditioned Conjugate Gradient (PCG). Do not use, deprecated
        
        Returns
        -------
        void (nothing)
        
        '''
        method = (int)(method)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetUnwrap2DMethod(method)
            except Exception as err:
                return self.Error(err)
    
    def SetUnwrap2DState(self, state=False):
        '''
        Enables or disables the unwrapping of the phase.

        Parameters
        ----------
        state : boolean, optional
            True to enable the unwrapping, false to disable it. Optional, default value is False.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetUnwrap2DState(state)
            except Exception as err:
                return self.Error(err)


    def SingleReconstruction(self):
        '''
        Acquires an image (or several if temporal averaging is on) and reconstruct it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SingleReconstruction()
            except Exception as err:
                return self.Error(err)
    
    def StartLateralScanning(self,startPositionX_um, startPositionY_um,
                             startPositionZ_um, numberOfPositionsX, numberOfPositionsY,
                             numberOfPositionsZ, stepSizeX_um, stepSizeY_um,
                             stepSizeZ_um, saveHolograms, saveIntensity, 
                             savePhase, saveAsBin, saveAsTxt, saveAsTif,
                             saveLambda1, saveLambda2, saveLambda3, 
                             isLambda1LaserUsed, isLambda2LaserUsed, 
                             isLambda3LaserUsed, centerScanOnStartPosition, 
                             savePath, numberOfAcquisitionsPerPosition, 
                             isAcquisitionAlternate):
        """
        Starts a recording of data to do a lateral scanning acquisition. 

        The acquisition is stopped before starting the recording. 

        The user describes a displacement grid for the stage using all the parameters for positions and step size in the X,Y and Z directions. The minimal number of positions in each direction is 1, i.e if you only move in X and Y direction, the number of positions in the Z direction must be set to 1.
        The stage goes back to its starting position at the end of the scan.

        Parameters
        ----------
        startPositionX_um : float (Double)
            absolute starting position for X axis in [um] as shown in the XYZ stage window.
        startPositionY_um : float (Double)
            absolute starting position for Y axis in [um] as shown in the XYZ stage window.
        startPositionZ_um : float (Double)
            absolute starting position for Z axis in [um] as shown in the XYZ stage window.
        numberOfPositionsX : Int32
            number of positions in the grid in the X axis direction. The minimum number of positions is 1.
        numberOfPositionsY : Int32
            number of positions in the grid in the Y axis direction. The minimum number of positions is 1.
        numberOfPositionsZ : Int32
            number of positions in the grid in the Z axis direction. The minimum number of positions is 1.
        stepSizeX_um : float (Double)
            size of one step in the X axis direction in [um].
        stepSizeY_um : float (Double)
            size of one step in the Y axis direction in [um].
        stepSizeZ_um : float (Double)
            size of one step in the Z axis direction in [um].
        saveHolograms : boolean
            if True save holograms during acquisition.
        saveIntensity : boolean
            if True save intensity during acquisition.
        savePhase : boolean
            if True save phase during acquisition.
        saveAsBin : boolean
            if True save phase and intensity in .bin format during acquisition.
        saveAsTxt : boolean
            if True save phase and intensity in .txt format during acquisition.
        saveAsTif : boolean
            if True save phase and intensity in .tif format during acquisition.
        saveLambda1 : boolean
            if True save phase and intensity for laser source lambda 1 separately.
            save data for lambda 1 (configuration lambda 1, 12 or 13)
        saveLambda2 : boolean
            if True save phase and intensity for laser source lambda 2 separately.
            save data for lambda 2 (configuration lambda 2 or 12)
        saveLambda3 : boolean
            if True save phase and intensity for laser source lambda 3 separately.
            save data for lambda 3 (configuration lambda 3 or 13)
        isLambda1LaserUsed : boolean
            if True use laser source lambda 1 for acquisition (configuration 1, 12, 13)
        isLambda2LaserUsed : boolean
            if True use laser source lambda 2 for acquisition  (configuration 2 or 12)
        isLambda3LaserUsed : boolean
            if True use laser source lambda 3 for acquisition (configuration 3 or 13)
        centerScanOnStartPosition : boolean
            if True, the displacement grid is centered on the current starting position. If false, the starting position is the top left corner of the grid.
        savePath : string
            absolute path where the data will be saved. If left empty, the data will be saved in a subfolder with its current date and time in the My Documents folder.
        numberOfAcquisitionsPerPosition : Int32
            number of acquisitions to be done at each position.
        isAcquisitionAlternate : boolean
           if True, the hologram acquisition is done alternately for 2-wavelengths configuration, so we obtain a hologram for lambda 1 (folder HologramsLambda1) and a hologram for lambda 2 (folder HologramsLambda2). If False, we obtain only one hologram for lambda 1-2 (folder Holograms).
        """
        numberOfPositionsX = (int)(numberOfPositionsX)
        numberOfPositionsY = (int)(numberOfPositionsY)
        numberOfPositionsZ = (int)(numberOfPositionsZ)
        numberOfAcquisitionsPerPosition = (int)(numberOfAcquisitionsPerPosition)
        self.ResetGrab() #force the reset to avoid error
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartLateralScanning(startPositionX_um, startPositionY_um,
                                     startPositionZ_um, numberOfPositionsX, numberOfPositionsY,
                                     numberOfPositionsZ, stepSizeX_um, stepSizeY_um,
                                     stepSizeZ_um, saveHolograms, saveIntensity, 
                                     savePhase, saveAsBin, saveAsTxt, saveAsTif,
                                     saveLambda1, saveLambda2, saveLambda3, 
                                     isLambda1LaserUsed, isLambda2LaserUsed, 
                                     isLambda3LaserUsed, centerScanOnStartPosition, 
                                     savePath, numberOfAcquisitionsPerPosition, 
                                     isAcquisitionAlternate)
            except Exception as err:
                return self.Error(err)
        
    def StartSpiralScanning(self,startPositionX_um, startPositionY_um, 
                             startPositionZ_um, totalNumberOfPositions,
                             useInternalBasisAngle, basisAngle_degrees,
                             constantRadius_px, saveHolograms, saveIntensity, 
                             savePhase, saveAsBin, saveAsTxt, saveAsTif,
                             saveLambda1, saveLambda2, saveLambda3,
                             isLambda1LaserUsed, isLambda2LaserUsed,
                             isLambda3LaserUsed, savePath, 
                             numberOfAcquisitionsPerPosition,
                             isAcquisitionAlternate):
        """
        Starts a recording of data to do a scanning acquisition following a Fermat spiral (see https://en.wikipedia.org/wiki/Fermat%27s_spiral for more details and https://www.flyingpudding.com/projects/florets/applet/ for an example to see the stage positions calculated). 
        The acquisition is stopped before starting the recording.
        
        Parameters
        ----------
        
        startPositionX_um : float (Double)
            absolute starting position for X axis in [um] as shown in the XYZ stage window.
        startPositionY_um : float (Double)
            absolute starting position for Y axis in [um] as shown in the XYZ stage window.
        startPositionZ_um : float (Double)
            absolute starting position for Z axis in [um] as shown in the XYZ stage window.
        totalNumberOfPositions : Int32
            number of positions in the grid in the X axis direction. The minimum number of positions is 1.
        useInternalBasisAngle : boolean
            if True, uses the golden angle to calculate the stage positions, if False, uses the basisAngle_deg parameter.
        basisAngle_degrees : float (Double)
            angle in degrees used to calculate the spiral positions if the useInternalBasisAngle is set to False.
        constantRadius_px : float (Double)
            factor used between consecutive points, in pixels.
        saveHolograms : boolean
            if True save holograms during acquisition.
        saveIntensity : boolean
            if True save intensity during acquisition.
        savePhase : boolean
            if True save phase during acquisition.
        saveAsBin : boolean
            if True save phase and intensity in .bin format during acquisition.
        saveAsTxt : boolean
            if True save phase and intensity in .txt format during acquisition.
        saveAsTif : boolean
            if True save phase and intensity in .tif format during acquisition.
        saveLambda1 : boolean
            if True save phase and intensity for laser source lambda 1 separately.
            save data for lambda 1 (configuration lambda 1, 12 or 13)
        saveLambda2 : boolean
            if True save phase and intensity for laser source lambda 2 separately.
            save data for lambda 2 (configuration lambda 2 or 12)
        saveLambda3 : boolean
            if True save phase and intensity for laser source lambda 3 separately.
            save data for lambda 3 (configuration lambda 3 or 13)
        isLambda1LaserUsed : boolean
            if True use laser source lambda 1 for acquisition (configuration 1, 12, 13)
        isLambda2LaserUsed : boolean
            if True use laser source lambda 2 for acquisition  (configuration 2 or 12)
        isLambda3LaserUsed : boolean
            if True use laser source lambda 3 for acquisition (configuration 3 or 13)
        centerScanOnStartPosition : boolean
            if True, the displacement grid is centered on the current starting position. If false, the starting position is the top left corner of the grid.
        savePath : string
            absolute path where the data will be saved. If left empty, the data will be saved in a subfolder with its current date and time in the My Documents folder.
        numberOfAcquisitionsPerPosition : Int32
            number of acquisitions to be done at each position.
        isAcquisitionAlternate : boolean
           if True, the hologram acquisition is done alternately for 2-wavelengths configuration, so we obtain a hologram for lambda 1 (folder HologramsLambda1) and a hologram for lambda 2 (folder HologramsLambda2). If False, we obtain only one hologram for lambda 1-2 (folder Holograms).
        
        Returns
        -------
        void (nothing)
        
        """
        totalNumberOfPositions = (int)(totalNumberOfPositions)
        numberOfAcquisitionsPerPosition = (int)(numberOfAcquisitionsPerPosition)
        
        self.ResetGrab() #force the reset to avoid error
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                self.host.StartSpiralScanning(startPositionX_um, startPositionY_um, 
                                     startPositionZ_um, totalNumberOfPositions,
                                     useInternalBasisAngle, basisAngle_degrees,
                                     constantRadius_px, saveHolograms, saveIntensity, 
                                     savePhase, saveAsBin, saveAsTxt, saveAsTif,
                                     saveLambda1, saveLambda2, saveLambda3,
                                     isLambda1LaserUsed, isLambda2LaserUsed,
                                     isLambda3LaserUsed, savePath, 
                                     numberOfAcquisitionsPerPosition,
                                     isAcquisitionAlternate)
            except Exception as err:
                return self.Error(err)

    def StartScanningFromPoints(self,startPostartPositionX_um, startPositionY_um,
                             startPositionZ_um, totalNumberOfPositions,
                             relativePositionsXList_um, relativePositionsYList_um,
                             relativePositionsZList_um, saveHolograms, saveIntensity,
                             savePhase, saveAsBin, saveAsTxt, saveAsTif, saveLambda1,
                             saveLambda2, saveLambda3, isLambda1LaserUsed, 
                             isLambda2LaserUsed, isLambda3LaserUsed, savePath,
                             numberOfAcquisitionsPerPosition,
                             isAcquisitionAlternate):
        """
        Starts a recording of data to do a scanning acquisition from points coordinates. The coordinates are given in pixels relative to the starting position.
        The acquisition is stopped before starting the recording.
        
        Parameters
        ----------
        
        startPositionX_um : float (Double)
            absolute starting position for X axis in [um] as shown in the XYZ stage window.
        startPositionY_um : float (Double)
            absolute starting position for Y axis in [um] as shown in the XYZ stage window.
        startPositionZ_um : float (Double)
            absolute starting position for Z axis in [um] as shown in the XYZ stage window.
        totalNumberOfPositions : Int32
            total number of positions. The minimum number of positions is 1. The total number of positions must correspond to the number of relative positions indicated hereafter, when the corresponding relativePositions fields are parsed.
        relativePositionsXList_um : string
            list of coordinates in the X axis direction in [um], relative to the starting position. Example: "[0, 1, 2]"  or "0, 1, 2" for a total number of positions set to 3.
        relativePositionsYList_um : string
            list of coordinates in the Y axis direction in [um], relative to the starting position. Example: "[0, 1, 2]"  or "0, 1, 2" for a total number of positions set to 3.
        relativePositionsZList_um : string
            list of coordinates in the Z axis direction in [um], relative to the starting position. Example: "[0, 1, 2]"  or "0, 1, 2" for a total number of positions set to 3.
        saveHolograms : boolean
            if True save holograms during acquisition.
        saveIntensity : boolean
            if True save intensity during acquisition.
        savePhase : boolean
            if True save phase during acquisition.
        saveAsBin : boolean
            if True save phase and intensity in .bin format during acquisition.
        saveAsTxt : boolean
            if True save phase and intensity in .txt format during acquisition.
        saveAsTif : boolean
            if True save phase and intensity in .tif format during acquisition.
        saveLambda1 : boolean
            if True save phase and intensity for laser source lambda 1 separately.
            save data for lambda 1 (configuration lambda 1, 12 or 13)
        saveLambda2 : boolean
            if True save phase and intensity for laser source lambda 2 separately.
            save data for lambda 2 (configuration lambda 2 or 12)
        saveLambda3 : boolean
            if True save phase and intensity for laser source lambda 3 separately.
            save data for lambda 3 (configuration lambda 3 or 13)
        isLambda1LaserUsed : boolean
            if True use laser source lambda 1 for acquisition (configuration 1, 12, 13)
        isLambda2LaserUsed : boolean
            if True use laser source lambda 2 for acquisition  (configuration 2 or 12)
        isLambda3LaserUsed : boolean
            if True use laser source lambda 3 for acquisition (configuration 3 or 13)
        centerScanOnStartPosition : boolean
            if True, the displacement grid is centered on the current starting position. If false, the starting position is the top left corner of the grid.
        savePath : string
            absolute path where the data will be saved. If left empty, the data will be saved in a subfolder with its current date and time in the My Documents folder.
        numberOfAcquisitionsPerPosition : Int32
            number of acquisitions to be done at each position.
        isAcquisitionAlternate : boolean
           if True, the hologram acquisition is done alternately for 2-wavelengths configuration, so we obtain a hologram for lambda 1 (folder HologramsLambda1) and a hologram for lambda 2 (folder HologramsLambda2). If False, we obtain only one hologram for lambda 1-2 (folder Holograms).
        
        Returns
        -------
        void (nothing)
        """
        totalNumberOfPositions = (int)(totalNumberOfPositions)
        numberOfAcquisitionsPerPosition = (int)(numberOfAcquisitionsPerPosition)
        self.ResetGrab() #force the reset to avoid error
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartScanningFromPoints(startPostartPositionX_um, startPositionY_um,
                                     startPositionZ_um, totalNumberOfPositions,
                                     relativePositionsXList_um, relativePositionsYList_um,
                                     relativePositionsZList_um, saveHolograms, saveIntensity,
                                     savePhase, saveAsBin, saveAsTxt, saveAsTif, saveLambda1,
                                     saveLambda2, saveLambda3, isLambda1LaserUsed, 
                                     isLambda2LaserUsed, isLambda3LaserUsed, savePath,
                                     numberOfAcquisitionsPerPosition,
                                     isAcquisitionAlternate)
            except Exception as err:
                return self.Error(err)

    def StartLiveWithReconstruction(self):
        '''
        Start Live with Reconstruction. 
        Only with online DHM

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartLiveWithReconstruction()
            except Exception as err:
                return self.Error(err)
    
    def StartLiveWithoutReconstruction(self):
        '''
        Start Live without Reconstruction. 
        Only with online DHM

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartLiveWithoutReconstruction()
            except Exception as err:
                return self.Error(err)
    
    def StopLive(self):
        '''
        Stop Live acquisition

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StopLive()
            except Exception as err:
                return self.Error(err)
    
## Sample remote functions

    def OpenSampleWin(self):
        '''
        Open the Sample window.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                self.sampleWinState = True
                return self.host.OpenSampleWin()
            except Exception as err:
                return self.Error(err)
        
    def CloseSampleWin(self):
        '''
        Close Sample Window.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            if self.sampleWinState:
                try:
                    self.host.CloseSampleWin()
                except Exception as err:
                    return self.Error(err)
            self.sampleWinState = False
        
        
    def SelectSampleByIndex(self, index):
        '''
        Select Sample by the index.

        Parameters
        ----------
        index : int
            Index of the sample

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            index = int(index)
            try:
                return self.host.SelectSampleByIndex(index)
            except Exception as err:
                return self.Error(err)
##The mask remote function
        
    def OpenMaskSettingsWin(self):
        '''
        Opens the mask settings window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenMaskSettingsWin()
            except Exception as err:
                return self.Error(err)
        
    def CloseMaskSettingsWin(self):
        '''
        Close the Mask Settings window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseMaskSettingsWin()
            except Exception as err:
                return self.Error(err)
    
    def SetAutomaticIntensityThresholdFilterToEnabledState(self):
        '''
        Enables the intensity threshold filter on the intensity, and sets the intensity threshold filter value automatically.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetAutomaticIntensityThresholdFilterToEnabledState()
            except Exception as err:
                return self.Error(err)
        
    def SetIntensityThresholdFilterState(self, state):
        '''
        Enables or disables the intensity threshold filter on the intensity.

        Parameters
        ----------
        state : boolean
            True to enable the intensity threshold filter, false to disable it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetIntensityThresholdFilterState(state)
            except Exception as err:
                return self.Error(err)

    def SetIntensityThresholdFilterValueInPercent(self, valueInPercent):
        '''
        Sets the intensity threshold filter value in percent.

        Parameters
        ----------
        valueInPercent : float
            value of the intensity filter in percent (use 30 for 30%).

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetIntensityThresholdFilterValueInPercent(valueInPercent)
            except Exception as err:
                return self.Error(err)
    
    def SetAutomaticPhaseGradientThresholdFilterToEnabledState(self):
        '''
        Enables the phase gradient threshold filter on the phase, and sets the phase gradient threshold filter value automatically.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetAutomaticPhaseGradientThresholdFilterToEnabledState()
            except Exception as err:
                return self.Error(err)
    
    def SetPhaseGradientThresholdFilterState(self, state):
        '''
        Enables or disables the phase gradient threshold filter on the phase.

        Parameters
        ----------
        state : boolean
            true to enable the intensity threshold filter, false to disable it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetPhaseGradientThresholdFilterState(state)
            except Exception as err:
                return self.Error(err)

    def SetPhaseGradientThresholdFilterValueInPercent(self, valueInPercent):
        '''
        Sets the phase gradient threshold filter value in percent.

        Parameters
        ----------
        valueInPercent : float
            value of the phase gradient filter in percent (use 30 for 30%)

        Returns
        -------
        void (nothing)

        '''
        #example if 30%, enter 30 as value
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetPhaseGradientThresholdFilterValueInPercent(valueInPercent)
            except Exception as err:
                return self.Error(err)
    
    def AddEllipticalUserDefinedMaskZoneToPhase(self, centerX, centerY, radiusX, radiusY):
        '''
        Adds an elliptical user defined mask zone on the Phase.

        Parameters
        ----------
        centerX : Int32
            X coordinate in the phase image of the center point of the zone, in pixel
        centerY : Int32
            Y coordinate in the phase image of the center point of the zone, in pixel
        radiusX : Int32
            Radius in the X-direction of the zone, in pixel
        radiusY : Int32
            Radius in the Y-direction of the zone, in pixel

        Returns
        -------
        void (nothing)

        '''
        centerX = (int)(centerX)
        centerY = (int)(centerY)
        radiusX = (int)(radiusX)
        radiusY = (int)(radiusY)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.AddEllipticalUserDefinedMaskZoneToPhase(centerX, centerY, radiusX, radiusY)
            except Exception as err:
                return self.Error(err)

    def AddRectangularUserDefinedMaskZoneToPhase(self, top, left, width, height):
        '''
        Adds a rectangular user defined mask zone on the Phase.

        Parameters
        ----------
        top : Int32
            Y coordinate in the phase image of the top left point of the zone, in pixel
        left : Int32
            X coordinate in the phase image of the top left point of the zone, in pixel
        width : Int32
            Width of the zone, in pixel
        height : Int32
            Height of the zone, in pixel

        Returns
        -------
        void (nothing)

        '''
        top = (int)(top)
        left = (int)(left)
        width = (int)(width)
        height = (int)(height)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.AddRectangularUserDefinedMaskZoneToPhase(top, left, width, height)
            except Exception as err:
                return self.Error(err)
    
    def SetInteractionModeWhenAddingMaskZone(self, mode):
        '''
        Set the interaction mode between user defined zones when adding a new mask zone on the Phase.

        Parameters
        ----------
        mode : Int32
            1: keep inside intersection	
            2: cut inside intersection	
            3: keep inside union		
            4: cut inside union


        Returns
        -------
        void (nothing)

        '''
        #mode is chosen between [1,2,3,4]
        mode = (int)(mode)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetInteractionModeWhenAddingMaskZone(mode)
            except Exception as err:
                return self.Error(err)

    
    def SetUserDefinedMaskState(self, state):
        '''
        Enables or disables the user defined mask filter on the phase.

        Parameters
        ----------
        state : boolean
            True to enable the user defined mask filter, false to disable it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetUserDefinedMaskState(state)
            except Exception as err:
                return self.Error(err)

    def SetWavelengthFilterMinimalCutOffValue(self, minimalCutoffValue):
        '''
        Sets the wavelength filter minimal cutoff value. The minimum cutoff value depends on the pixel size: it is 2 pixels (Nyquist).

        Parameters
        ----------
        minimalCutoffValue : float
            value of the minimal cutoff in um.

        Returns
        -------
       void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetWavelengthFilterMinimalCutOffValue(minimalCutoffValue)
            except Exception as err:
                return self.Error(err)

    def SetWavelengthFilterMaximalCutOffValue(self, maximalCutoffValue):
        '''
        Sets the wavelength filter maximal cutoff value. The maximum cutoff value depends on the image size.

        Parameters
        ----------
        maximalCutoffValue : float
            value of the maximal cutoff in um.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetWavelengthFilterMaximalCutOffValue(maximalCutoffValue)
            except Exception as err:
                return self.Error(err)

    def SetWavelengthFilterState(self, state):
        '''
        Enables or disables the wavelength filter on the phase.

        Parameters
        ----------
        state : boolean
            True to enable the wavelength filter, false to disable it. Optional, default value is false.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetWavelengthFilterState(state)
            except Exception as err:
                return self.Error(err)

    def SetWavelengthFilterType(self, filterType):
        """
        Set the type of wavelength filter on the phase.
        Parameters
        ----------
        filterType : Int32
            1 for Long-pass type filter
            2 for Short-pass type filter
            3 for Band-pass type filter
            4 for Band-stop type filter
        
        Returns
        -------
        void (nothing)
        
        """
        filterType = (int)(filterType)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetWavelengthFilterType(filterType)
            except Exception as err:
                return self.Error(err)

##The sequence remote functions
        
    ### Fast Holograms Record
        
    def CloseFastHologramsRecordWin(self):
        '''
        Close the Fast record holograms sequence window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseFastHologramsRecordWin()
            except Exception as err:
                return self.Error(err)
    
    def OpenFastHologramsRecordWin(self):
        '''
        Opens the fast holograms acquisition window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenFastHologramsRecordWin()
            except Exception as err:
                return self.Error(err)
    
    def SetFastHologramsSequenceRecordNumberOfHolograms(self, numberOfHolograms):
        '''
        Set the number of holograms to be recorded using the Fast record holograms sequence window.

        Parameters
        ----------
        numberOfHolograms : Int32
            number of holograms to be recorded in the Hologram.raw sequence.

        Returns
        -------
        void (nothing)

        '''
        numberOfHolograms = (int)(numberOfHolograms)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetFastHologramsSequenceRecordNumberOfHolograms(numberOfHolograms)
            except Exception as err:
                return self.Error(err)
    
    def SetFastHologramsSequenceRecordingModeBuffer(self, state):
        '''
        Enables or disables the buffer mode using the Fast record holograms sequence window.

        Parameters
        ----------
        state : boolean
            True to enable the intensity threshold filter, false to disable it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetFastHologramsSequenceRecordingModeBuffer(state)
            except Exception as err:
                return self.Error(err)
    
    def SetFastHologramsSequenceRecordPath(self, path):
        '''
        Set the path to record the hologram sequence using the Fast record holograms sequence window.

        Parameters
        ----------
        path : string
            Full path to the folder where to store Hologram.raw sequence.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetFastHologramsSequenceRecordPath(path)
            except Exception as err:
                return self.Error(err)
        
    def StartFastHologramsSequenceRecord(self):
        '''
        Start the sequence recording using the Fast record holograms sequence window.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartFastHologramsSequenceRecord()
            except Exception as err:
                return self.Error(err)
    
    def StopFastHologramsSequenceRecord(self):
        '''
        Stop the sequence recording using the Fast record holograms sequence window. It should not be used in conjunction with a given number of holograms to record, as the recording session will automatically stop when a number or holograms is given.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StopFastHologramsSequenceRecord()
            except Exception as err:
                return self.Error(err)
    
    ### Reconstruction to disk

    def CloseReconstructionToDiskSequenceWin(self):
        '''
        Closes the reconstruction settings window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseReconstructionToDiskSequenceWin()
            except Exception as err:
                return self.Error(err)

    def OpenReconstructionToDiskSequenceWin(self):
        '''
        Opens the reconstruction to disk settings window

        Returns
        -------
        void (nothing)


        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenReconstructionToDiskSequenceWin()
            except Exception as err:
                return self.Error(err)
    
    def SetReconstructionToDiskDataType(self, recordPhaseAsBin, recordPhaseAsText, recordPhaseAsTiff, recordIntensityAsBin, recordIntensityAsText, recordIntensityAsTiff):
        '''
        Choose what kind of files are reconstructed and saved  or not using the Sequence: Reconstruction to disk window. If the path is valid (contains a Holograms folder and a timestamp file), the phase and intensity buttons will be enabled.

        Parameters
        ----------
        recordPhaseAsBin : boolean
            True to start the phase reconstruction in .bin format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Phase\Float\Bin, False otherwise.
        recordPhaseAsText : boolean
            True to start the phase reconstruction in .txt format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Phase\Float\Txt, False otherwise
        recordPhaseAsTiff : boolean
            True to start the phase reconstruction in .tiff format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Phase\Image, False otherwise.
        recordIntensityAsBin : boolean
            True to start the intensity reconstruction in .bin format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Intensity\Float\Bin, False otherwise.
        recordIntensityAsText : boolean
            True to start the intensity reconstruction in .txt format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Intensity\Float\Txt, False otherwise.
        recordIntensityAsTiff : boolean
            True to start the intensity reconstruction in .tiff format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Intensity\Image, False otherwise.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetReconstructionToDiskDataType(recordPhaseAsBin, recordPhaseAsText, recordPhaseAsTiff, recordIntensityAsBin, recordIntensityAsText, recordIntensityAsTiff)
            except Exception as err:
                return self.Error(err)

    def SetReconstructionToDiskSequencePath(self, path):
        '''
        Set the path to the sequence to be reconstructed using the Sequence: Reconstruction to disk window. If the path is valid (contains a Holograms folder and a timestamp file), the phase and intensity buttons will be enabled.

        Parameters
        ----------
        path : string
            Full path to the folder where to read the holograms sequence.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetReconstructionToDiskSequencePath(path)
            except Exception as err:
                return self.Error(err)
    
    def StartReconstructionToDisk(self):
        '''
        Start the sequence reconstruction using the Sequence: Reconstruction to disk window.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartReconstructionToDisk()
            except Exception as err:
                return self.Error(err)



## The stroboscope remote functions
        
    def ApplyNewDutyCycleInLiveMode(self):
        '''
        Apply the modified laser duty cycle when the stroboscope is already started, i.e. in Live mode.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ApplyNewDutyCycleInLiveMode()
            except Exception as err:
                return self.Error(err)
    
    def ApplyNewVoltageAndOffsetInLiveModeForChannelNumber(self, channelNumber):
        '''
        Apply the modified voltage, offset and offset type, for a given channel number when the stroboscope is already started, i.e. in Live mode.

        Parameters
        ----------
        channelNumber : Int32
            gives the channel number in the range [1,2,3,4].

        Returns
        -------
        void (nothing)
        '''
        channelNumber = (int)(channelNumber)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.ApplyNewVoltageAndOffsetInLiveModeForChannelNumber(channelNumber)
            except Exception as err:
                return self.Error(err)
    
    def CloseStroboWin(self):
        '''
        Closes the stroboscope window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.CloseStroboWin()
            except Exception as err:
                return self.Error(err)
    
    def DecreaseStroboscopeAngleStep(self):
        '''
        Modify the current frequency operational range (indicated in green on the frequency slider) by moving it to lower frequencies. Reducing the angle step can lead to having more samples per period available.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.DecreaseStroboscopeAngleStep()
            except Exception as err:
                return self.Error(err)
    
    def IncreaseStroboscopeAngleStep(self):
        '''
        Modify the current frequency operational range (indicated in green on the frequency slider) by moving it to higher frequencies.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.IncreaseStroboscopeAngleStep()
            except Exception as err:
                return self.Error(err)
    
    def MaximizeStroboscopeNumberOfSamples(self):
        '''
        Calculate and set the actual maximal number of samples for the current frequency range. 

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.MaximizeStroboscopeNumberOfSamples()
            except Exception as err:
                return self.Error(err)
    
    def OpenStroboWin(self):
        '''
        Opens the stroboscope window

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.OpenStroboWin()
            except Exception as err:
                return self.Error(err)
        
    def RecordStroboscopeFixedFrequency(self, numberOfPeriods):
        '''
        Starts a fixed frequency recording with the stroboscopic tool, for a given number of periods.
        A classic stroboscope fixed frequency sequence where recording is not done can be started with StartStroboscopeFixedFrequency.
        The stroboscopic tool must have been previously configured by hand in Koala, or using remote commands. The stroboscopic window must be opened on the Main tab, and all options except the number of periods must have been set manually.

        Parameters
        ----------
        numberOfPeriods : Int32
            The number of periods of the signal generated by the stroboscopic tool to record

        Returns
        -------
        string
            the path where the result has been saved

        '''
        numberOfPeriods = (int)(numberOfPeriods)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.RecordStroboscopeFixedFrequency(numberOfPeriods)
            except Exception as err:
                return self.Error(err)
        
    def RecordStroboscopeFrequencyScan(self):
        '''
        Starts a frequency scan recording with the stroboscopic tool. The stroboscopic tool must have been previously configured by hand in Koala , or using remote commands. The stroboscopic window must be opened on the Scanning tab, the Frequency scan option must have been selected and the desired options (minimal and maximal frequency, step size, number of periods per frequency, etc…) must have been set before starting the recording).

        Returns
        -------
        string
            the path where the result has been saved

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.RecordStroboscopeFrequencyScan()
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeChannelParameters(self, channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType, chanelID=1):
        '''
        Set the stroboscopic tool parameters for given channel

        Parameters
        ----------
        channelEnabled : boolean
            true to enable the channel, false to disable it.
        chosenWaveform : Int32
            waveform chosen in the array [1,2,3,4]
        voltage_mV : Int32
            Voltage value in [mV] in the range [0,10000]
        offset_mV :  Int32
            Offset value in [mV] in the range [-10000,10000]
        phaseDelay_deg : Int32
            Phase in [degrees] in the range [0,360]
        offsetType : Int32
            Offset type [0 for "Manual", 1 for "0", 2 for "V<0", 3 for "V>0"]
        chanelID : Int32, optional
            Channel 1, 2,4 or 4. The default is 1.

        Returns
        -------
        void (nothing)

        '''
        chosenWaveform = (int)(chosenWaveform)
        voltage_mV = (int)(voltage_mV)
        offset_mV = (int)(offset_mV)
        phaseDelay_deg = (int)(phaseDelay_deg)
        offsetType = (int)(offsetType)
        chanelID = (int)(chanelID)
        if chanelID == 1:
            return self.SetStroboscopeChannel1Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
        if chanelID == 2:
            return self.SetStroboscopeChannel2Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
        if chanelID == 3:
            return self.SetStroboscopeChannel3Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
        if chanelID == 4:
            return self.SetStroboscopeChannel4Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
    
    def SetStroboscopeChannel1Parameters(self, channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType):
        '''
        Set the stroboscopic tool parameters for channel 1.

        Parameters
        ----------
        channelEnabled : boolean
            true to enable the channel, false to disable it.
        chosenWaveform : Int32
            waveform chosen in the array [1,2,3,4]
        voltage_mV : Int32
            Voltage value in [mV] in the range [0,10000]
        offset_mV :  Int32
            Offset value in [mV] in the range [-10000,10000]
        phaseDelay_deg : Int32
            Phase in [degrees] in the range [0,360]
        offsetType : Int32
            Offset type [0 for "Manual", 1 for "0", 2 for "V<0", 3 for "V>0"]

        Returns
        -------
        void (nothing)

        '''
        chosenWaveform = (int)(chosenWaveform)
        voltage_mV = (int)(voltage_mV)
        offset_mV = (int)(offset_mV)
        phaseDelay_deg = (int)(phaseDelay_deg)
        offsetType = (int)(offsetType)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeChannel1Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
            except Exception as err:
                return self.Error(err)

    def SetStroboscopeChannel2Parameters(self, channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType):
        '''
        Set the stroboscopic tool parameters for channel 2.

        Parameters
        ----------
        channelEnabled : boolean
            true to enable the channel, false to disable it.
        chosenWaveform : Int32
            waveform chosen in the array [1,2,3,4]
        voltage_mV : Int32
            Voltage value in [mV] in the range [0,10000]
        offset_mV :  Int32
            Offset value in [mV] in the range [-10000,10000]
        phaseDelay_deg : Int32
            Phase in [degrees] in the range [0,360]
        offsetType : Int32
            Offset type [0 for "Manual", 1 for "0", 2 for "V<0", 3 for "V>0"]

        Returns
        -------
        void (nothing)

        '''
        chosenWaveform = (int)(chosenWaveform)
        voltage_mV = (int)(voltage_mV)
        offset_mV = (int)(offset_mV)
        phaseDelay_deg = (int)(phaseDelay_deg)
        offsetType = (int)(offsetType)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeChannel2Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
            except Exception as err:
                return self.Error(err)

    def SetStroboscopeChannel3Parameters(self, channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType):
        '''
        Set the stroboscopic tool parameters for channel 3.

        Parameters
        ----------
        channelEnabled : boolean
            true to enable the channel, false to disable it.
        chosenWaveform : Int32
            waveform chosen in the array [1,2,3,4]
        voltage_mV : Int32
            Voltage value in [mV] in the range [0,10000]
        offset_mV :  Int32
            Offset value in [mV] in the range [-10000,10000]
        phaseDelay_deg : Int32
            Phase in [degrees] in the range [0,360]
        offsetType : Int32
            Offset type [0 for "Manual", 1 for "0", 2 for "V<0", 3 for "V>0"]

        Returns
        -------
        void (nothing)

        '''
        chosenWaveform = (int)(chosenWaveform)
        voltage_mV = (int)(voltage_mV)
        offset_mV = (int)(offset_mV)
        phaseDelay_deg = (int)(phaseDelay_deg)
        offsetType = (int)(offsetType)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeChannel3Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeChannel4Parameters(self, channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType):
        '''
        Set the stroboscopic tool parameters for channel 4.

        Parameters
        ----------
        channelEnabled : boolean
            true to enable the channel, false to disable it.
        chosenWaveform : Int32
            waveform chosen in the array [1,2,3,4]
        voltage_mV : Int32
            Voltage value in [mV] in the range [0,10000]
        offset_mV :  Int32
            Offset value in [mV] in the range [-10000,10000]
        phaseDelay_deg : Int32
            Phase in [degrees] in the range [0,360]
        offsetType : Int32
            Offset type [0 for "Manual", 1 for "0", 2 for "V<0", 3 for "V>0"]

        Returns
        -------
        void (nothing)

        '''
        chosenWaveform = (int)(chosenWaveform)
        voltage_mV = (int)(voltage_mV)
        offset_mV = (int)(offset_mV)
        phaseDelay_deg = (int)(phaseDelay_deg)
        offsetType = (int)(offsetType)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:    
                return self.host.SetStroboscopeChannel4Parameters(channelEnabled, chosenWaveform, voltage_mV, offset_mV, phaseDelay_deg, offsetType)
            except Exception as err:
                return self.Error(err)

    def SetStroboscopeFixedFrequency(self, frequency):
        '''
        Set the stroboscopic tool Fixed Frequency mode.

        Parameters
        ----------
        frequency : float (Double)
            The frequency must be between 1[Hz] and 25[MHz].

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeFixedFrequency(frequency)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeFrequencyScanEnabled(self, status=False):
        '''
        Enable/Disable the stroboscopic tool frequency scan. The main panel will have its input for fixed frequency blocked when the frequency scan is selected, as shown below.

        Parameters
        ----------
        status : boolean, optional
            True to enable the frequency scan, False to disable it.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeFrequencyScanEnabled(status)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeFrequencyScanParameters(self, minimumFrequency_Hz, maximumFrequency_Hz, stepSize_Hz, numberOfPeriodsPerFrequency, isDecreasing=False):
        '''
        Set the stroboscopic tool frequency scan parameters. The iterations of the frequency scan are applied between the minimum and maximum frequencies, with each time a frequency difference indicated by the step size. We apply the iterations until the current frequency added to the step size reaches the maximal frequency. If the step applied produces a frequency value greater than the maximal frequency chosen, the scan stops.

        Parameters
        ----------
        minimumFrequency_Hz : float (Double)
            minimal frequency in [Hz] for the frequency scan.
        maximumFrequency_Hz : float (Double)
            maximal frequency in [Hz] for the frequency scan.
        stepSize_Hz : float (Double)
            frequency difference in [Hz] between 2 iterations (e.g with a frequency start at 1[kHz], and a step size of 200[Hz], the next frequency will be at 1.2[kHz], if we are increasing the frequency.
        numberOfPeriodsPerFrequency : Int32
            number of periods applied on each frequency iteration.
        isDecreasing : boolean, optional
            True to decrease frequencies during the frequency scan (the scan will start at maximumFrequency_Hz and end at minimumFrequency_Hz while taking into account the stepSize_Hz), 
            False to increase frequencies during the frequency scan (the scan will start at minimumFrequency_Hz and end at maximumFrequency_Hz while taking into account the stepSize_Hz). Default is False

        Returns
        -------
        void (nothing)

        '''
        numberOfPeriodsPerFrequency = (int)(numberOfPeriodsPerFrequency )
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeFrequencyScanParameters(minimumFrequency_Hz, maximumFrequency_Hz, stepSize_Hz, numberOfPeriodsPerFrequency, isDecreasing=False)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeLaserPulseDutyCycle(self, dutyCycle):
        '''
        Set a value for the laser duty cycle when using the stroboscope.

        Parameters
        ----------
        dutyCycle : float (Double)
            gives the laser duty cycle value in percent between 0.01% and 100% .

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeLaserPulseDutyCycle(dutyCycle)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeNumberOfSamplesPerPeriod(self, samplesPerPeriod):
        '''
        Set the number of samples used for one period when using the stroboscope.

        Parameters
        ----------
        samplesPerPeriod : Int32
            gives the number of samples per period.

        Returns
        -------
        void (nothing)

        '''
        samplesPerPeriod = (int)(samplesPerPeriod)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeNumberOfSamplesPerPeriod(samplesPerPeriod)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeRecordAtStartStatus(self, status=False):
        '''
        Choose if we record or not when we begin a stroboscopic sequence.

        Parameters
        ----------
        status : boolean, optional
            to start the recording when we start the stroboscope sequence, false will not trigger any recording session. The default is False.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeRecordAtStartStatus(status)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeRecordDataType(self, recordPhaseAsBin, recordPhaseAsTiff, recordIntensityAsBin, recordIntensityAsTiff):
        '''
        Choose what kind of files are recorded or not when we begin a stroboscopic sequence.

        Parameters
        ----------
        recordPhaseAsBin : boolean
            true to start recording phase in .bin format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Phase\Float\Bin, false otherwise.
        recordPhaseAsTiff : boolean
            true to start recording phase in .tiff format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Phase\Image, false otherwise.
        recordIntensityAsBin : boolean
            true to start recording intensity in .bin format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Intensity\Float\Bin, false otherwise.
        recordIntensityAsTiff : boolean
            true to start recording intensity in .tiff format in the folder RECORD_PATH\YYYY.MM.dd hh-mm-ss\Intensity\Image, false otherwise.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeRecordDataType(recordPhaseAsBin, recordPhaseAsTiff, recordIntensityAsBin, recordIntensityAsTiff)
            except Exception as err:
                return self.Error(err)
    
    def SetStroboscopeRecordPath(self, path):
        '''
        Choose the path where saved data is stored.

        Parameters
        ----------
        path : string
            set the folder path RECORD_PATH.

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SetStroboscopeRecordPath(path)
            except Exception as err:
                return self.Error(err)
    
    def StartStroboscopeFixedFrequency(self, cycleMode, numberOfPeriods):
        '''
        Start the stroboscopic sequence with the given cycle mode (continuous or number of periods).
        A stroboscope fixed frequency sequence recording can be started with RecordStroboscopeFixedFrequency.

        Parameters
        ----------
        cycleMode : Int32
            choose the mode to do the stroboscope sequence [0 for continuous, 1 for number of periods].
        numberOfPeriods : Int32
            sets the number of periods when the mode chosen before is set to 1.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        cycleMode = (int)(cycleMode)
        numberOfPeriods = (int)(numberOfPeriods)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StartStroboscopeFixedFrequency(cycleMode, numberOfPeriods)
            except Exception as err:
                return self.Error(err)
    
    def StopStroboscope(self):
        '''
        Stop the current stroboscopic sequence (fixed frequency or frequency scan).

        Returns
        -------
        void (nothing)

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.StopStroboscope()
            except Exception as err:
                return self.Error(err)

#specific codes
    def CreateDirectory(self, directoryPath):
        '''
        Create a directory with the diretoryPath if the directory does not exist.

        Parameters
        ----------
        directoryPath : string
            directory to create

        Returns
        -------
        None.

        '''
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)   
    
    def SaveStackRecDistCM(self, distCM_Min, distCM_Max, distCM_step, savePath, saveIntensity=True,
                             savePhase=True, saveAsBin=True, saveAsTxt=False, saveAsTif=False, saveLambda1=True,
                             saveLambda2=False, saveLambdaSynthLong=False,
                             saveLambdaSynthShort=False, totalNumberOfDistances=None, singleWavelengthConfig=True):
        
        '''
        Save stacks for different reconstruction distances.
        
        Note, by default singleWavelengthConfig = True because SelectDisplayWL works only for dual wavelengths
        
        
        Parameters
        ----------
        distCM_Min : float
            minimal reconstruction distance in cm
        distCM_max : float
            maximal reconstruction distance in cm
        distCM_step : float
            step in cm for the stack, defined automatically if totalNumberOfDistances is not None
        savePath : string path
            path to save the data
        saveIntensity : boolean
            save Amplitude, default is True.
        savePhase : boolean
            save Phase, default is True.
        saveAsBin : boolean
            save as .bin format, default is True.
        saveAsTxt : boolean
            save as .txt format, default if False.
        saveAsTif : boolean
            save as .tif format, default if False.
        saveLambda1 : boolean
            save data for lambda 1 (configuration lambda 1, 12 or 13), default if True.
        saveLambda2 : boolean
            save data for second lambda  (configuration lambda 12 or 13), default if False.
        saveLambdaSynthLong : boolean
            save data for long synthetic (configuration lambda 12 or 13), default if False.
        saveLambdaSynthShort : boolean
            save data for short synthetic (configuration lambda 12 or 13), default if False.
        totalNumberOfDistances : Int32
            if not None, compute the distCM_step according to this value, default is None
        singeWavelengthDHM : boolean
            by default=True, to avoid SelectDisplayWL if single wavelength->error, default is True.
            
        Returns
        -------
        d_stack : 1D numpy array
            numpy array of effective reconstructed distances applied
            
        Remark: from Koala version >= 8.6.48015.0, singleWavelengthConfig is defined automatically when a configuration is open (self.configType=1,2)
            
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            if self.configType is not None:
                if self.configType == 1:
                    singleWavelengthConfig = True
                if self.configType == 2:
                    singleWavelengthConfig = False
                    
            if totalNumberOfDistances is None:
                totalNumberOfDistances = (int)((distCM_Max-distCM_Min)/distCM_step)+1
            else:
                totalNumberOfDistances = (int)(totalNumberOfDistances)
                distCM_step = (distCM_Max-distCM_Min)/(totalNumberOfDistances-1)
                
            if singleWavelengthConfig :
                saveLambda1 = True
                saveLambda2=False
                saveLambdaSynthLong=False
                saveLambdaSynthShort=False
                
            d_stack = []
            if totalNumberOfDistances >= 1:
                for k in range(totalNumberOfDistances):
                    d = distCM_Min+k*distCM_step
                    d_stack.append(d)
                    self.SetRecDistCM(d)
                    self.OnDistanceChange()
                    if saveLambda1:
                        if saveIntensity:
                            if not singleWavelengthConfig:
                                self.SelectDisplayWL(2048)
                            directory_amp = os.path.join(savePath,"Lambda1","Intensity","Float")
                            if saveAsBin:
                                directory = os.path.join(directory_amp,"Bin")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_intensity.bin")
                                self.SaveImageFloatToFile(2, fname, True)
                            if saveAsTxt:
                                directory = os.path.join(directory_amp,"Txt")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_intensity.txt")
                                self.SaveImageFloatToFile(2, fname, False)
                            if saveAsTif:
                                directory = os.path.join(savePath,"Lambda1","Intensity","Image")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_intensity.jpg")
                                self.SaveImageToFile(2, fname)
                        if savePhase:
                            if not singleWavelengthConfig:
                                self.SelectDisplayWL(8192)
                            directory_amp = os.path.join(savePath,"Lambda1","Phase","Float")
                            if saveAsBin:
                                directory = os.path.join(directory_amp,"Bin")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.bin")
                                self.SaveImageFloatToFile(4, fname, True)
                            if saveAsTxt:
                                directory = os.path.join(directory_amp,"Txt")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.txt")
                                self.SaveImageFloatToFile(4, fname, False)
                            if saveAsTif:
                                directory = os.path.join(savePath,"Lambda1","Phase","Image")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.jpg")
                                self.SaveImageToFile(4, fname)
                                
                    if saveLambda2:
                        if saveIntensity:
                            self.SelectDisplayWL(4096)
                            directory_amp = os.path.join(savePath,"Lambda2","Intensity","Float")
                            if saveAsBin:
                                directory = os.path.join(directory_amp,"Bin")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_intensity.bin")
                                self.SaveImageFloatToFile(2, fname, True)
                            if saveAsTxt:
                                directory = os.path.join(directory_amp,"Txt")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_intensity.txt")
                                self.SaveImageFloatToFile(2, fname, False)
                            if saveAsTif:
                                directory = os.path.join(savePath,"Lambda2","Intensity","Image")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_intensity.jpg")
                                self.SaveImageToFile(2, fname)
                        if savePhase:
                            self.SelectDisplayWL(16384)
                            directory_amp = os.path.join(savePath,"Lambda2","Phase","Float")
                            if saveAsBin:
                                directory = os.path.join(directory_amp,"Bin")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.bin")
                                self.SaveImageFloatToFile(4, fname, True)
                            if saveAsTxt:
                                directory = os.path.join(directory_amp,"Txt")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.txt")
                                self.SaveImageFloatToFile(4, fname, False)
                            if saveAsTif:
                                directory = os.path.join(savePath,"Lambda2","Phase","Image")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.jpg")
                                self.SaveImageToFile(4, fname)
                                
                    if saveLambdaSynthLong:
                        if savePhase:
                            self.SelectDisplayWL(32768)
                            directory_amp = os.path.join(savePath,"LambdaSynthLong","Phase","Float")
                            if saveAsBin:
                                directory = os.path.join(directory_amp,"Bin")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.bin")
                                self.SaveImageFloatToFile(4, fname, True)
                            if saveAsTxt:
                                directory = os.path.join(directory_amp,"Txt")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.txt")
                                self.SaveImageFloatToFile(4, fname, False)
                            if saveAsTif:
                                directory = os.path.join(savePath,"LambdaSynthLong","Phase","Image")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"_phase.jpg")
                                self.SaveImageToFile(4, fname)
                            
                    if saveLambdaSynthShort:
                        if savePhase:
                            self.SelectDisplayWL(65536)
                            directory_amp = os.path.join(savePath,"LambdaSynthSort","Phase","Float")
                            if saveAsBin:
                                directory = os.path.join(directory_amp,"Bin")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"phase.bin")
                                self.SaveImageFloatToFile(4, fname, True)
                            if saveAsTxt:
                                directory = os.path.join(directory_amp,"Txt")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"phase.txt")
                                self.SaveImageFloatToFile(4, fname, False)
                            if saveAsTif:
                                directory = os.path.join(savePath,"LambdaSynthShort","Phase","Image")
                                self.CreateDirectory(directory)
                                fname = os.path.join(directory,str(k).zfill(5)+"phase.jpg")
                                self.SaveImageToFile(4, fname)
            else:
                print("Number of steps are smaller than one. Verify that minimal distance is smaller than maximal one and that the step is correct")
            return np.array(d_stack)
    
    def GetStackRecDistCM(self, distCM_Min, distCM_Max, distCM_step, GetIntensity=True,
                             GetPhase=True, GetLambda1=True,
                             GetLambda2=False, GetLambdaSynthLong=False,
                             GetLambdaSynthShort=False, totalNumberOfDistances=None,
                             singleWavelengthConfig = True):
        
        '''
        Create numpy stacks for different reconstruction distances.
        
        Note, by default singleWavelengthConfig = True because SelectDisplayWL works only for dual wavelengths
        
        Parameters
        ----------
        distCM_Min : float
            minimal reconstruction distance in cm
        distCM_max : float
            maximal reconstruction distance in cm
        distCm_step : float
            step in cm for the stack, defined automatically if totalNumberOfDistances is not None
        GetIntensity : boolean
            get Amplitude Stack, default is True.
        GetPhase : boolean
            get Phase Stack, default is True.
        GetLambda1 : boolean
            save data for lambda 1 (configuration lambda 1, 12 or 13), default is True.
        GetLambda2 : boolean
            save data for second lambda  (configuration lambda 12 or 13), default is False.
        GetLambdaSynthLong : boolean
            save data for long synthetic (configuration lambda 12 or 13), default is False.
        GetLambdaSynthShort : boolean
            save data for short synthetic (configuration lambda 12 or 13), default is False.
        totalNumberOfDistances : Int32
            if not None, compute the distCM_step according to this value, default is None.
        singeWavelengthDHM : boolean
            by default=True, to avoid SelectDisplayWL if single wavelength->error, default is True
        
        Returns
        -------
        IntensityLambda1Stack : 3D numpy array (height, width, totalNumberOfDistances)
            Stack of amplitudes for lambda 1 of the configuration
        PhaseLambda1Stack : 3D numpy array (height, width, totalNumberOfDistances)
            Stack of Phase for lambda 1 of the configuration
        IntensityLambda2Stack : 3D numpy array (height, width, totalNumberOfDistances)
            Stack of amplitudes for lambda 2 of the configuration (could be lambda 2 or lambda 3!)
        PhaseLambda2Stack : 3D numpy array (height, width, totalNumberOfDistances)
            Stack of Phase for lambda 2 of the configuration (could be lambda 2 or lambda 3!)
        PhaseLambdaSynthLongStack : 3D numpy array (height, width, totalNumberOfDistances)
            Stack of Long Synthetic of the configuration (only for dual wavelelenght configurations)
        PhaseLambdaSynthShortStack : 3D numpy array (height, width, totalNumberOfDistances)
            Stack of Short Synthetic of the configuration (only for dual wavelelenght configurations)
        d_stack : 1D numpy array
            numpy array of effective reconstructed distances applied
            
        Remark: from Koala version >= 8.6.48015.0, singleWavelengthConfig is defined automatically when a configuration is open (self.configType=1,2)
        '''
        IntensityLambda1Stack = None
        IntensityLambda2Stack = None
        PhaseLambda1Stack = None
        PhaseLambda2Stack = None
        PhaseLambdaSynthLongStack = None
        PhaseLambdaSynthShortStack = None
        d_stack = None
        
        if self.erroroccurs and self.forceLogoutIfError:
            return IntensityLambda1Stack,PhaseLambda1Stack, IntensityLambda2Stack,PhaseLambda2Stack,PhaseLambdaSynthLongStack,PhaseLambdaSynthShortStack, d_stack
        else:
            if self.configType is not None:
                if self.configType == 1:
                    singleWavelengthConfig = True
                if self.configType == 2:
                    singleWavelengthConfig = False
                    
            if totalNumberOfDistances is None:
                totalNumberOfDistances = (int)((distCM_Max-distCM_Min)/distCM_step)+1
            else:
                totalNumberOfDistances = (int)(totalNumberOfDistances)
                distCM_step = (distCM_Max-distCM_Min)/(totalNumberOfDistances-1)
                
            if singleWavelengthConfig :
                GetLambda1 = True
                GetLambda2=False
                GetLambdaSynthLong=False
                GetLambdaSynthShort=False
                
            w = self.GetPhaseWidth()
            h = self.GetPhaseHeight()
            if w is not None and h is not None:
                d_stack = []
                if totalNumberOfDistances >= 1:
                    for k in range(totalNumberOfDistances):
                        d = distCM_Min+k*distCM_step
                        d_stack.append(d)
                        self.SetRecDistCM(d)
                        self.OnDistanceChange()
                        if GetLambda1:
                            if GetIntensity:
                                if not singleWavelengthConfig:
                                    self.SelectDisplayWL(2048)
                                if k == 0 :
                                    IntensityLambda1Stack = np.ones((h, w, totalNumberOfDistances))*np.nan
                                IntensityLambda1Stack[:,:,k]= self.GetIntensity32fImage()
                            if GetPhase:
                                if not singleWavelengthConfig:
                                    self.SelectDisplayWL(8192)
                                if k == 0 :
                                    PhaseLambda1Stack = np.ones((h, w, totalNumberOfDistances))*np.nan
                                PhaseLambda1Stack[:,:,k]= self.GetPhase32fImage()
                                    
                        if GetLambda2:
                            if GetIntensity:
                                self.SelectDisplayWL(4096)
                                if k == 0 :
                                    IntensityLambda2Stack = np.ones((h, w, totalNumberOfDistances))*np.nan
                                IntensityLambda2Stack[:,:,k]= self.GetIntensity32fImage()
                            if GetPhase:
                                self.SelectDisplayWL(16384)
                                if k == 0 :
                                    PhaseLambda2Stack = np.ones((h, w, totalNumberOfDistances))*np.nan
                                PhaseLambda2Stack[:,:,k]= self.GetPhase32fImage()
                                    
                        if GetLambdaSynthLong:
                            if GetPhase:
                                self.SelectDisplayWL(32768)
                                if k == 0 :
                                    PhaseLambdaSynthLongStack = np.ones((h, w, totalNumberOfDistances))*np.nan
                                PhaseLambdaSynthLongStack[:,:,k]= self.GetPhase32fImage()
                                
                        if GetLambdaSynthShort:
                            if GetPhase:
                                self.SelectDisplayWL(65536)
                                if k == 0 :
                                    PhaseLambdaSynthShortStack = np.ones((h, w, totalNumberOfDistances))*np.nan
                                PhaseLambdaSynthShortStack[:,:,k]= self.GetPhase32fImage()
                else:
                    print("Number of steps are smaller than one. Verify that minimal distance is smaller than maximal one and that the step is correct")
        
            return IntensityLambda1Stack,PhaseLambda1Stack, IntensityLambda2Stack,PhaseLambda2Stack,PhaseLambdaSynthLongStack,PhaseLambdaSynthShortStack, np.array(d_stack)

## Photron camera functions


##Mode Selection
    def SelectClassicWorkspace(self):
        '''
        Select classic workspace for photron camera.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SelectClassicWorkspace()
            except Exception as err:
                return self.Error(err)
        
    def SelectHighSpeedSequenceWorkspace(self):
        '''
        Select high speed sequence workspace for photron camera.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.SelectHighSpeedSequenceWorkspace()
            except Exception as err:
                return self.Error(err)
        
    def SelectPhotronCameraWorkspace(self, workspace):
        '''
        Select workspace for photron camera: "Classic" or "HighSpeed".

        Parameters
        ----------
        workspace : string
            Choose workspace of Photron camera, "Classic" or "HighSpeed"

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if workspace == "Classic":
                    return self.SelectClassicWorkspace()
                    
                elif workspace == "HighSpeed":
                    return self.SelectHighSpeedSequenceWorkspace()
                else:
                    raise TypeError("The workspace does not exists, use 'Classic' or 'HighSpeed'")
                    return 
            except Exception as err:
                return self.Error(err)
            
            
#Tabs
    def HighSpeedSequenceWorkspace_SelectLiveTab(self):
        '''
        Select Live Tab for in the high speed sequence workspace.
        The high speed sequence workspace should be selected first.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsLiveTabSelected():
                    return self.host.HighSpeedSequenceWorkspace_SelectLiveTab()
            except Exception as err:
                return self.Error(err)


    def HighSpeedSequenceWorkspace_IsLiveTabSelected(self):
        '''
        Get the status of the HighSpeedSequence workspace live tab selection.

        Returns
        -------
        bool
            Return true if the LiveTab is selected

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.HighSpeedSequenceWorkspace_IsLiveTabSelected()
            except Exception as err:
                return self.Error(err)

    def HighSpeedSequenceWorkspace_SelectRecordSequenceTab(self):
        '''
        Select the Record Sequence tab in the high speed sequence workspace.
        The high speed sequence workspace has to be selected first.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected():
                    return self.host.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
            except Exception as err:
                return self.Error(err)


    def HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected(self):
        '''
        Get status of the high speed sequence workspace recorded sequence tab selection

        Returns
        -------
        bool
            Return true if the recorded sequence tab is selected.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected()
            except Exception as err:
                return self.Error(err)
        
        
    def HighSpeedSequenceWorkspace_SelectReplaySequenceTab(self):
        '''
        Select the Replay Sequence tab in the high speed sequence workspace.
        The high speed sequence workspace has to be selected first.

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    return self.host.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
            except Exception as err:
                return self.Error(err)
        
    def HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected(self):
        '''
        Get status of the high speed sequence workspace replay sequence tab selection

        Returns
        -------
        bool
            Return true if the recorded sequence tab is selected.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected()
            except Exception as err:
                return self.Error(err)

    def HighSpeedSequenceWorkspace_SelectExportSequenceTab(self):
        '''
        Select the Replay Sequence tab in the high speed sequence workspace.
        The high speed sequence workspace has to be selected first.
    
        Returns
        -------
        None.
    
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    return self.host.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
            except Exception as err:
                return self.Error(err)
              
        
    def HighSpeedSequenceWorkspace_IsExportSequenceTabSelected(self):
        '''
        Get statuS of the high speed sequence workspace export sequence tab selection

        Returns
        -------
        bool
            Return true if the export sequence tab is selected.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected()
            except Exception as err:
                return self.Error(err)

    def HighSpeedSequenceWorkspace_SelectCameraTab(self):
        '''
        Select the Camera tab in the high speed sequence workspace.
        The high speed sequence workspace has to be selected first.
    
        Returns
        -------
        None.
    
        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    return self.host.HighSpeedSequenceWorkspace_SelectCameraTab()
            except Exception as err:
                return self.Error(err)
        
    def HighSpeedSequenceWorkspace_IsCameraTabSelected(self):
        '''
        Get status of the high speed sequence workspace camera tab selection

        Returns
        -------
        bool
            Return true if the camera tab is selected.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.HighSpeedSequenceWorkspace_IsCameraTabSelected()
            except Exception as err:
                return self.Error(err)
    
    
    def HighSpeedSequenceWorkspace_SelectTab(self, tab):
        '''
        Select the tab of high speed sequence workspace from tab.

        Parameters
        ----------
        tab : string
            selected tab: Live, RecordSeq, ReplaySeq, ExportSeq, or Camera

        Returns
        -------
        None.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if tab == "Live":
                    return self.HighSpeedSequenceWorkspace_SelectLiveTab()
                elif tab == "RecordSeq":
                    return self.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
                elif tab == "ReplaySeq":
                    return self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                elif tab == "ExportSeq":
                    return self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                elif tab == "Camera":
                    return self.HighSpeedSequenceWorkspace_SelectCameraTab()
                else:
                    raise TypeError("Tab does not exist, do nothing")
                    return
            except Exception as err:
                return self.Error(err)

            
    def HighSpeedSequenceWorkspace_IsTabSelected(self, tab):
        '''
        Get the state of the tab of high speed sequence workspace from tab.

        Parameters
        ----------
        tab : string
            Get state of the tab of high speed workspace of: Live, RecordSeq, ReplaySeq, ExportSeq, or Camera

        Returns
        -------
        bool
            Return true if the selected tab is selected.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if tab == "Live":
                    return self.HighSpeedSequenceWorkspace_IsLiveTabSelected()
                elif tab == "RecordSeq":
                    return self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected()
                elif tab == "ReplaySeq":
                    return self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected()
                elif tab == "ExportSeq":
                    return self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected()
                elif tab == "Camera":
                    return self.HighSpeedSequenceWorkspace_IsCameraTabSelected()
                else:
                    raise TypeError("Tab does not exist, do nothing")
                    return False
            except Exception as err:
                return self.Error(err)
        
#Record sequence tab

    def HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtBeginning(self):
        '''
        Set the Trigger buffer at the beginning.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtBeginning()
            except Exception as err:
                return self.Error(err)
        
    def HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtCenter(self):
        '''
        Set the Trigger buffer at the center.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtCenter()
            except Exception as err:
                return self.Error(err)
        
        
    def HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtEnd(self):
        '''
        Set the Trigger buffer at the end.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtEnd()
            except Exception as err:
                return self.Error(err)
            
    def HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtPosition(self, position):
        '''
        Set the Trigger buffer position.

        Parameters
        ----------
        position : string
            Position of the Trigger buffer: Beginning, Center or End

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if position == "Beginning":
                    return self.HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtBeginning()
                elif position == "Center":
                    return self.HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtCenter
                elif position == "End":
                    return self.HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtEnd
                else:
                    raise TypeError("Position for HighSpeedSequenceWorkspace_RecordSequenceTab_SetTriggerBufferAtPosition does not exist")
            except Exception as err:
                return self.Error(err)
        
        
    def HighSpeedSequenceWorkspace_RecordSequenceTab_StartRecordingWithPhotronCamera(self):
        '''
        Start Recording with Photron camera.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_RecordSequenceTab_StartRecordingWithPhotronCamera()
            except Exception as err:
                return self.Error(err)
        
        
    def HighSpeedSequenceWorkspace_RecordSequenceTab_StopRecordingWithPhotronCamera(self):
        '''
        Stop Recording with Photron camera.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsRecordSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectRecordSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_RecordSequenceTab_StopRecordingWithPhotronCamera()
            except Exception as err:
                return self.Error(err)


#Camera Photron General properties
    def HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings(self):
        '''
        Open Camera Settings.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
            except Exception as err:
                return self.Error(err)
            
    def HighSpeedSequenceWorkspace_PhotronCamera_CloseCameraSettings(self):
        '''
        Close Camera Settings.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_CloseCameraSettings()
            except Exception as err:
                return self.Error(err)
        
        
        
    def HighSpeedSequenceWorkspace_PhotronCamera_Calibrate(self):
        '''
        Calibrate the Photron Camera.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                self.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_Calibrate()
            except Exception as err:
                return self.Error(err)
                
        
    def HighSpeedSequenceWorkspace_PhotronCamera_SetFanStatus(self, status):
        '''
        Set the Photron camera fan status.

        Parameters
        ----------
        status : bool
            Status of the Photron camera Fan

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                self.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_SetFanStatus(status)
            except Exception as err:
                return self.Error(err)
            

    def HighSpeedSequenceWorkspace_PhotronCamera_SetCameraFrameRate(self, framerate):
        '''
        Setting the frame rate at (framerate) fps to record sequences in the photron camera.

        Parameters
        ----------
        framerate : int
            Frame rate of the record sequence.

        Returns
        -------
        None

        '''
        framerate = (int)(framerate)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                self.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_SetCameraFrameRate(framerate)
            except Exception as err:
                return self.Error(err)
        
        

    def HighSpeedSequenceWorkspace_PhotronCamera_SetCameraShutterSpeed(self, shutterSpeed):
        '''
        Setting the shutter speed at (1/shutterSpeed) [s] in the photron camera.

        Parameters
        ----------
        shutterSpeed : int
            Shutter speed defined as (1/shutterSpeed)

        Returns
        -------
        None

        '''
        shutterSpeed = (int)(shutterSpeed)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                self.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_SetCameraShutterSpeed(shutterSpeed)
            except Exception as err:
                return self.Error(err)



    def HighSpeedSequenceWorkspace_PhotronCamera_SetCameraResolution(self, resolution):
            '''
            Setting the resolution at (resolution) in the photron camera. Valid resolutions values are "1024x1024", "512x512", "256x256", "128x128" (not tested).
    
            Parameters
            ----------
            resolution: string or int
                Defined camera resolution: "1024x1024", "512x512", "256x256", "128x128" or int 1024, 512, 256, 128
    
            Returns
            -------
            None
    
            '''
            if isinstance(resolution, int):
                res = str(resolution)+"x"+str(resolution)
            elif isinstance(resolution, str):
                res = resolution
            else:
                raise TypeError("Expected input to be either int or str.")
            
            if self.erroroccurs and self.forceLogoutIfError:
                return
            else:
                try:
                    if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                        self.HighSpeedSequenceWorkspace_SelectCameraTab()
                    self.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
                    return self.host.HighSpeedSequenceWorkspace_PhotronCamera_SetCameraResolution(res)
                except Exception as err:
                    return self.Error(err)
            
    
    def HighSpeedSequenceWorkspace_PhotronCamera_SaveCameraShutterSpeed(self):
        '''
        Save Camera Shutter Speed.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsCameraTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectCameraTab()
                self.HighSpeedSequenceWorkspace_PhotronCamera_OpenCameraSettings()
                return self.host.HighSpeedSequenceWorkspace_PhotronCamera_SaveCameraShutterSpeed()
            except Exception as err:
                return self.Error(err)
        
#Replay sequence tab
    def HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameStartNumber(self, frameStart):
        '''
        Set the hologram index of the start of the sequence to be exported

        Parameters
        ----------
        frameStart : int
            frameStart: hologram index of the start of the sequence to be exported.

        Returns
        -------
        None

        '''
        frameStart = (int)(frameStart)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameStartNumber(frameStart)
            except Exception as err:
                return self.Error(err)
        

    def HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameEndNumber(self, frameEnd):
        '''
        Set the hologram index of the end of the sequence to be exported

        Parameters
        ----------
        frameEnd : int
            frameStart: hologram index of the end of the sequence to be exported.

        Returns
        -------
        None

        '''
        frameEnd = (int)(frameEnd)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameEndNumber(frameEnd)
            except Exception as err:
                return self.Error(err)
            
    def HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameStartAndEndNumber(self, frameStart, frameEnd):
        '''
        Set the hologram index of the start and end of the sequence to be exported

        Parameters
        ----------
        frameEnd : int
            frameStart: hologram index of the start of the sequence to be exported.
        frameEnd : int
            frameStart: hologram index of the end of the sequence to be exported.

        Returns
        -------
        None

        '''
        frameStart = (int)(frameStart)
        frameEnd = (int)(frameEnd)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameStartNumber(frameStart)
                self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_SetFrameEndNumber(frameEnd)
            except Exception as err:
                return self.Error(err)
        
        
    

    def HighSpeedSequenceWorkspace_ReplaySequenceTab_SetCurrentFrameNumber(self, currentFrame):
        '''
        Set the current frame number.

        Parameters
        ----------
        currentFrame : int
            current frame number, currentFrame must be between frameStart and frameEnd.

        Returns
        -------
        None

        '''
        currentFrame= (int)(currentFrame)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_SetCurrentFrameNumber(currentFrame)
            except Exception as err:
                return self.Error(err)
        

    def HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayForward(self):
        '''
        Play Sequence Forward

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayForward()
            except Exception as err:
                return self.Error(err)
        
        
        
    def HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayBackward(self):
        '''
        Play Sequence Backward

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayBackward()
            except Exception as err:
                return self.Error(err)
            
    def HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayDirection(self, direction):
        '''
        Set direction of the sequence play

        Parameters
        ----------
        direction : string
            direction of the sequence play: "Forward" or "Backward"

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                if direction == "Backward":
                    return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayBackward()
                if direction == "Forward":
                    return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_PlayForward()
            except Exception as err:
                return self.Error(err)     
    
        
    def HighSpeedSequenceWorkspace_ReplaySequenceTab_Pause(self):
        '''
        Pause the replay sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_Pause()
            except Exception as err:
                return self.Error(err)
        
    def HighSpeedSequenceWorkspace_ReplaySequenceTab_SetReplayFrameRate(self, framerate):
        '''
        Setting the frame rate at (framerate) fps to replay the current sequence stored in the photron camera. 

        Parameters
        ----------
        framerate : int
            Frame rate to replay the current sequence

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        framerate = (int)(framerate)
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsReplaySequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectReplaySequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ReplaySequenceTab_SetReplayFrameRate(framerate)
            except Exception as err:
                return self.Error(err)
     
#Export Sequence Tab
    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectHologramsForExport(self, status):
        '''
        Set status of hologram selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the holograms of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectHologramsForExport(status)
            except Exception as err:
                return self.Error(err)
        

    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsBinForExport(self, status):
        '''
        Set status of phase as bin selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the phase as bin of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsBinForExport(status)
            except Exception as err:
                return self.Error(err)
        
        
    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsTxtForExport(self, status):
        '''
        Set status of phase as txt selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the phase as txt of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsTxtForExport(status)
            except Exception as err:
                return self.Error(err)
        
            
    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsTifForExport(self, status):
        '''
        Set status of phase as tif selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the phase as tif of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsTifForExport(status)
            except Exception as err:
                return self.Error(err)

    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsBinForExport(self, status):
        '''
        Set status of intensity as bin selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the intensity as bin of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsBinForExport(status)
            except Exception as err:
                return self.Error(err)
        
        
    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsTxtForExport(self, status):
        '''
        Set status of intensity as txt selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the intensity as txt of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsTxtForExport(status)
            except Exception as err:
                return self.Error(err)
            
            
    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsTifForExport(self, status):
        '''
        Set status of intensity as tif selection for the exportation.

        Parameters
        ----------
        status : bool
            if true export the intensity as tif of the sequence

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsTifForExport(status)
            except Exception as err:
                return self.Error(err)
            
    def HighSpeedSequenceWorkspace_ExportSequenceTab_SelectionToExport(self, holos=True, phasebin=True, intbin=True, phasetxt=False, phasetif=False, inttxt=False, inttif=False):
        '''
        Set the selection of what to save for the sequence exportation. By defaut, only  holograms, phase.bin and intensity as bin are saved.

        Parameters
        ----------
        holos : bool
            Save Holograms for the sequence. The default is True.
        phasebin : bool
            Save phase as bin for the sequence. The default is True.
        intbin : bool
            Save intensity as bin for the sequence. The default is True.
        phasetxt : bool, optional 
            Save phase as txt for the sequence. The default is False.
        phasetif : bool, optional
            Save phase as tif for the sequence. The default is False.
        inttxt : bool, optional
            Save intensity as txt for the sequence. The default is False.
        inttif : bool, optional
            Save intensity as tif for the sequence. The default is False.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectHologramsForExport(holos)
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsBinForExport(phasebin)
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsBinForExport(intbin)
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsTxtForExport(phasetxt)
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectPhaseAsTifForExport(phasetif)
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsTxtForExport(inttxt)
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SelectIntensityAsTifForExport(inttif)

            except Exception as err:
                return self.Error(err)


    def HighSpeedSequenceWorkspace_ExportSequenceTab_SaveSequence(self, path, overwrite):
        '''
        Save the sequence.

        Parameters
        ----------
        path : string
            Path to save the sequence.
        overwrite : bool
            if true overwrite the existing sequence.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SaveSequence(path, overwrite)
            except Exception as err:
                return self.Error(err)
                if not self.HighSpeedSequenceWorkspace_IsExportSequenceTabSelected():
                    self.HighSpeedSequenceWorkspace_SelectExportSequenceTab()
                return self.host.HighSpeedSequenceWorkspace_ExportSequenceTab_SaveSequence(path, overwrite)
        

#Turret management
    def Turret_SetConfirmationBeforeChangingConfigurationFromRemote(self, status):
        '''
        Set status of the Turret confirmation before changing configuration from remote.

        Parameters
        ----------
        status : bool
            Satus for the confirmation.

        Returns
        -------
        None

        '''
        if self.erroroccurs and self.forceLogoutIfError:
            return
        else:
            try:
                return self.host.Turret_SetConfirmationBeforeChangingConfigurationFromRemote(status)
            except Exception as err:
                return self.Error(err)
        

#test the class when running this file directly
if __name__ == '__main__' :
    pathHere = os.getcwd()
    path_holo = os.path.join(os.path.abspath(os.path.join(pathHere, os.pardir)),"example","data","holo.tif")
    remote = pyKoalaRemoteClient()
#    remote.SetforceLogoutIfError(True)
    seqpath = r'Z:\Reference Measurement\exemple_tracking\Sperm'
    if remote.ConnectAndLoging():
        px_size = remote.GetCameraPixelSizeUm()
        print(px_size)
        # configType = remote.OpenConfig(127)
        # remote.LoadHologram(path_holo)
        # #        remote.OpenSampleWin()
        # remote.SelectSampleByIndex(32)
        # remote.OpenAllWindows()
        # remote.SelectDisplayWL(8192)
        # remote.OpenReconstructionSettingsWin()
        # remote.AddCorrSegment(50,10,800,0)
        
        # remote.AddCorrSegment(50,50,200,1)
        # remote.ComputePhaseCorrection(0,1)
        # remote.ComputePhaseCorrection(1,2)
        # remote.ResetCorrSegment()
        # remote.SetUnwrap2DState(True)
        # remote.AddCorrZone(100,100,900,900)
        # remote.ComputePhaseCorrection(4,2)
        # remote.ResetCorrZone()
        # remote.SetUnwrap2DState(False)
        # remote.ResetPhaseOffsetAdjustmentZone()
        # remote.AddPhaseOffsetAdjustmentZone(50,50, 200,200)
        # #         distCM_Min = 0
        # #         distCM_Max = 9.81
        # #         distCM_step = 0.5
        # #         savePath = r'C:\tmp_remote_test'
        # #         d_stack = remote.SaveStackRecDistCM(distCM_Min, distCM_Max, distCM_step, savePath,totalNumberOfDistances=50)
        # #        
        # #         # print(d_stack)
        # #         IntensityLambda1Stack,PhaseLambda1Stack, IntensityLambda2Stack,PhaseLambda2Stack,PhaseLambdaSynthLongStack,PhaseLambdaSynthShortStack, d_stack = remote.GetStackRecDistCM(distCM_Min, distCM_Max, distCM_step,GetLambda1=True, GetLambda2=True, totalNumberOfDistances=50)         
        # #         # print(d_stack)
        remote.Logout()