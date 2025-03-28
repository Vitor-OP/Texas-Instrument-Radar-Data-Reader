class ConfigurationParser:
    C = 3e2 # m/us
    """
    Class to parse the radar configuration parameters from a cfg file
    This are the commands described in the docummentation from texas instrument mmwave mcuplus sdk 04.07.00.01. The commands are subjected to differences between versions so be aware!
    
    MMWAVE MCUPLUS SDK 04.07.00.01 CONFIGURATION PARSER
    
    """
    def __init__(self, cfg_file_path: str):
        # ALL INSTANCES VARIABLES MUST BE DECLARED AFTER THE DECLARATION OF dictionaries_list ---------------------------------------------------------------------------------------------------        
        
        # dfeDataOutputMode dictionary
        self.dfeDataOutputMode = {
            "modeType": None  # Configures the Data Flow Engine (DFE) output mode.
        }
        """
            1 - Frame-based chirps
            2 - Continuous chirping (not supported in the demo)
            3 - Advanced frame configuration
            4 - Advanced chirp with legacy frame configuration
            5 - Advanced chirp with advanced frame configuration

            Notes:
                - TDM and DDM modes only support options 1, 3, 4, and 5.
                - Only option 1 is valid for AWR2544, AWR2x44P, and AWR2944LC.
        """

        # channelCfg dictionary
        self.channelCfg = {
            "rxChannelEn": None,  # Receive antenna mask (e.g., for 4 antennas: 0x1111b = 15)
            "txChannelEn": None,  # Transmit antenna mask (bitmask varies per device, e.g., AWR294X supports up to 4 antennas with 0xF)
            "miscCtrl": None  # SoC cascading (always set to 0, not applicable)
        }

        # adcCfg dictionary
        self.adcCfg = {
            "numADCBits": None,  # Number of ADC bits (0 = 12-bit, 1 = 14-bit, 2 = 16-bit)
            "adcOutputFmt": None  # ADC output format.
        }
        """
        0 - Real
        1 - Complex 1x (image band filtered output)
        2 - Complex 2x (image band visible)

        Notes:
            - AWR294X: Only real mode is supported.
            - AWR2544: Only real mode is supported.
        """
        
        # adcbufCfg dictionary
        self.adcbufCfg = {
            "subFrameIdx": None,  # Subframe index (-1 for legacy mode, specific values for advanced mode)
            "adcOutputFmt": None,  # ADCBUF output format (0 = Complex, 1 = Real)
            "SampleSwap": None,  # IQ swap selection (0 = I in LSB, Q in MSB; 1 = Q in LSB, I in MSB)
            "ChanInterleave": None,  # ADCBUF channel interleave mode (0 = Interleaved, 1 = Non-interleaved)
            "ChirpThreshold": None  # Chirp threshold configuration used for ADCBUF buffer to trigger ping/pong buffer switch.
        }

        """
        Valid values:
            - 0-8 for demos that use DSP for 1D FFT and LVDS streaming is disabled
            - Only 1 for demos that use HWA for 1D FFT

        Notes:
            - Only value 1 is supported since demos use HWA for 1D FFT.
        """

        # lowPower dictionary
        self.lowPower = {
            "dont_care": None,  # Reserved, always set to 0
            "ADC_mode": None  # ADC mode selection (0 = Regular mode, 1 = Low power mode)
        }

        """
        Configures ADC power mode:

            0x00 - Regular ADC mode
            0x01 - Low power ADC mode
        """

        # profileCfg dictionary
        self.profileCfg = {
            "profileId": None,  # Unique identifier for the profile
            "startFreq": None,  # Start frequency in GHz (e.g., 77 or 61.38 GHz)
            "idleTime": None,  # Idle time between chirps in microseconds
            "adcStartTime": None,  # ADC valid start time in microseconds
            "rampEndTime": None,  # Ramp end time in microseconds
            "txOutPower": None,  # Transmitter output power back-off code (Only '0' tested)
            "txPhaseShifter": None,  # TX phase shifter (Only '0' tested)
            "freqSlopeConst": None,  # Frequency slope for chirp in MHz/usec
            "txStartTime": None,  # TX start time in microseconds
            "numAdcSamples": None,  # Number of ADC samples per chirp
            "digOutSampleRate": None,  # ADC sampling frequency in ksps
            "hpfCornerFreq1": None,  # High Pass Filter (HPF) corner frequency 1 (0: 175 kHz, 1: 235 kHz, 2: 350 kHz, 3: 700 kHz)
            "hpfCornerFreq2": None,  # High Pass Filter (HPF) corner frequency 2 (0: 350 kHz, 1: 700 kHz, 2: 1.4 MHz, 3: 2.8 MHz)
            "rxGain": None  # Receiver gain configuration
        }

        """
        Receiver gain configuration:

        - Bit 5:0  RX_GAIN (Receiver gain in dB)
        - Bit 7:6  RF_GAIN_TARGET (RF gain target)

        Notes:
            - AWR294X/AWR2544 require that hpfCornerFreq1 and hpfCornerFreq2 have the same value.
        """

        # CHIRP CONFIGURATION FUNCTIONS...........................................................................................

        # IF dfeDataOutputMode.modeType == 0:
        self.chirpCfg = {
            "startIdx": None,  # Chirp start index (any value as per mmwavelink doxygen)
            "endIdx": None,  # Chirp end index (any value as per mmwavelink doxygen)
            "profileId": None,  # Must match the `profileCfg.profileId`
            "startFreqVar": None,  # Start frequency variation in Hz (only 0 tested in demo)
            "freqSlopeVar": None,  # Frequency slope variation in kHz/us (only 0 tested in demo)
            "idleTimeVar": None,  # Idle time variation in μs (only 0 tested in demo)
            "adcStartTimeVar": None,  # ADC start time variation in μs (only 0 tested in demo)
            "txEnable": None  # Tx antenna enable mask (e.g., 0b10 = Tx2 enabled, Tx1 disabled)
        }

        """
        Chirp configuration message to RadarSS and datapath.

        This configuration is mandatory when `dfeDataOutputMode` is set to 1 or 3.
        It defines the chirp parameters such as start and end indices, frequency,
        slope, and transmission settings.
        """

        # IF dfeDataOutputMode.modeType == 3 or == 4: -------------------------------------------------------------------

        self.advChirpCfg = {
            "chirpParamIdx": None,  # Index of the chirp parameter to configure
            "resetMode": None,  # Reset mode (0 = End of Frame, 1 = End of Sub-frame, 2 = End of Burst)
            "deltaResetPeriod": None,  # Number of chirps before resetting delta dither accumulation
            "deltaParamUpdatePeriod": None,  # Period (N) for updating delta dither
            "sf0ChirpParamDelta": None,  # Delta dither for sub-frame 0
            "sf1ChirpParamDelta": None,  # Delta dither for sub-frame 1 (not used in legacy mode)
            "sf2ChirpParamDelta": None,  # Delta dither for sub-frame 2 (not used in legacy mode)
            "sf3ChirpParamDelta": None,  # Delta dither for sub-frame 3 (not used in legacy mode)
            "lutResetPeriod": None,  # Number of chirps before resetting LUT sequence
            "lutParamUpdatePeriod": None,  # Period (K) for updating LUT values
            "lutPatternAddressOffset": None,  # Offset for LUT pattern storage
            "numOfPatterns": None,  # Number of unique LUT patterns
            "lutSfIndexOffset": None  # LUT sub-frame index offset (valid only for advanced frame mode)
        }

        """
        Advanced chirp configuration message to RadarSS and datapath.

        This configuration is mandatory when `dfeDataOutputMode` is set to 4 or 5.
        It allows configuring dynamic chirp parameters that can change per chirp.
        """

        self.LUTDataCfg = {
            "chirpParamIdx": None,  # Index of the chirp parameter being programmed
            "lutData": []  # List of LUT values for dither patterns
        }

        """
        LUT Data configuration message for RadarSS and datapath.

        This configuration is mandatory when `dfeDataOutputMode` is set to 4 or 5.
        It stores the programmed patterns of a chirp parameter in a LUT.
        """

        # Rest of the configuration commands -------------------------------------------------------------------------------------------

        self.frameCfg = {
            "chirpStartIdx": None,  # Start index of chirp (0-511, must match chirpCfg)
            "chirpEndIdx": None,  # End index of chirp (chirpStartIdx - 511, must match chirpCfg)
            "numLoops": None,  # Number of loops per frame
            "numFrames": None,  # Number of frames to transmit (0 means infinite)
            "numAdcSamples": None, # number of ADC samples collected during "ADC Sampling Time"
            "framePeriodicity": None,  # Frame periodicity in milliseconds
            "triggerSelect": None,  # Trigger selection (1: Software, 2: Hardware, 3: CPTS-based)
            "frameTriggerDelay": None  # Frame trigger delay in milliseconds
        }

        """
        Number of loops per frame:
        - Legacy Chirp Mode (dfeOutputMode = 1 or 3): Number of times to loop through unique chirps (1 to 255).
        - Advanced Chirp Mode (dfeOutputMode = 4 or 5): Total number of chirps in a subframe.

        Notes:
        - Value should be >= 4.
        - If set to 2 for Doppler Chirps, demo code must be updated to use rectangular window for Doppler DPU instead of Hanning.
        """

        self.guiMonitor = {
            "subFrameIdx": None,  # Subframe index (-1 for legacy mode, specific values for advanced mode)
            "detectedObjects": None,  # Enable detected object data export
            "logMagRange": None,  # 1 to enable export of log magnitude range profile at zero Doppler, 0 to disable
            "noiseProfile": None,  # 1 to enable export of log magnitude noise profile, 0 to disable
            "rangeAzimuthHeatMap": None,  # Enable range-azimuth heat map
            "rangeDopplerHeatMap": None,  # 1 to enable full detection matrix export, 0 to disable
            "statsInfo": None  # 1 to enable system statistics export (CPU load, temperature, etc.), 0 to disable
        }

        """
        Enable detected object data export:
        - 0: Disabled
        - 1: Export point cloud (x, y, z, Doppler) and side info (SNR, noise)
        - 2: Export only point cloud
        """

        self.cfarCfg = {
            "subFrameIdx": None,  # Subframe index (-1 for legacy mode, specific values for advanced mode)
            "procDirection": None,  # CFAR processing direction
            "mode": None,  # CFAR averaging mode (0: CA, 1: CAGO, 2: CASO)
            "noiseWin": None,  # Noise averaging window length
            "guardLen": None,  # Guard length in samples
            "divShift": None,  # Noise sum divisor (expressed as shift value)
            "cyclicMode": None,  # 0 to disable cyclic mode, 1 to enable
            "thresholdScale": None,  # Detection threshold in dB (max allowed: 100dB)
            "peakGrouping": None  # 0 to disable, 1 to enable peak grouping
        }

        """
        CFAR processing direction:
        - 0: Range direction
        - 1: Doppler direction

        Notes:
        - Two separate commands are needed: one for range and one for Doppler.
        """

        self.compressionCfg = {
            "subFrameNum": None,  # Subframe index (0 to RL_MAX_SUBFRAMES-1)
            "enabled": None,  # 1 to enable compression (must be enabled), 0 to disable
            "compressionMethod": None,  # 0: EGE compression, 1: BFP compression
            "compressionRatio": None,  # Compression ratio (floating-point value between 0 and 1)
            "rangeBinsPerBlock": None  # Number of range bins per compressed block (must be a power of 2)
        }

        self.intfMitigCfg = {
            "subFrameNum": None,  # Subframe index (0 to RL_MAX_SUBFRAMES-1)
            "magSNRdB": None,  # Magnitude SNR for interference mitigation (integer in dB)
            "magDiffSNRdB": None  # Magnitude difference SNR for interference mitigation (integer in dB)
        }

        self.localMaxCfg = {
            "subFrameNum": None,  # Subframe index (0 to RL_MAX_SUBFRAMES-1)
            "azimThreshdB": None,  # Azimuth threshold for local max detection (in dB)
            "dopplerThreshdB": None  # Doppler threshold for local max detection (in dB)
        }

        self.ddmPhaseShiftAntOrder = {
            "tx0": None,
            "tx1": None,
            "tx2": None,
            "tx3": None
        }

        """
        Defines the antenna phase shift order in increasing values.

        Notes:
        - In DDMA, elevation antennas should always be last.
        - Example for AWR2944 ETS antenna array: {0, 2, 3, 1}.
        """

        self.antGeometryCfg = {
            "txPositions": None,  # Antenna positions in <row, column> format
            "xSpacebylambda": None,  # Azimuth spacing in units of lambda (e.g., 0.5 for AWR2944 ETS)
            "zSpacebylambda": None  # Elevation spacing in units of lambda (e.g., 0.8 for AWR2944 ETS)
        }

        """
        Antenna positions in <row, column> format.

        Notes:
        - Example: For N antennas, provide positions as [(Tx0Row, Tx0Col), (Tx1Row, Tx1Col), ..., (TxNRow, TxNCol)]
        """

        self.antennaCalibParams = {
            "calibrationData": None  # Antenna calibration parameters
        }

        """
        Format:
        - [Q0, I0, ..., Q15, I15] (for 16 virtual antennas of AWR294X)
        - For AWR2943, last 8 values will be ignored.

        Values are in Im(Q)-Re(I) format.
        """

        self.measureRangeBiasAndRxChanPhase = {
            "enabled": None,  # 1 to enable measurement, 0 to disable
            "targetDistance": None,  # Distance in meters of test object
            "searchWin": None  # Search window in meters around target distance
        }

        self.analogMonitor = {
            "rxSaturation": None,  # Enable/disable RX saturation monitoring (1: enable, 0: disable)
            "sigImgBand": None,  # Enable/disable signal and image band energy monitoring (1: enable, 0: disable)
            "apllLdoSCMonEn": None  # APLL LDO Short Circuit Monitor enable/disable
        }

        """
        APLL LDO Short Circuit Monitor enable/disable.

        Notes:
        - 1: Enable, 0: Disable.
        - Supported only for AWR2544.
        """

        self.aoaFovCfg = {
            "subFrameIdx": None,  # Subframe index (-1 for legacy mode, specific values for advanced mode)
            "minAzimuthDeg": None,  # Minimum azimuth angle (in degrees)
            "maxAzimuthDeg": None,  # Maximum azimuth angle (in degrees)
            "minElevationDeg": None,  # Minimum elevation angle (in degrees)
            "maxElevationDeg": None  # Maximum elevation angle (in degrees)
        }

        self.calibData = {
            "saveEnable": None,  # Boot-time RF calibration save option
            "restoreEnable": None,  # Boot-time RF calibration restore option
            "flashOffset": None  # Address offset in Flash for saving/restoring calibration data
        }

        """
        Boot-time RF calibration save/restore options:

        - saveEnable:
        - 1: Save calibration data to FLASH.
        - 0: Disable save.

        - restoreEnable:
        - 1: Restore calibration data from FLASH.
        - 0: Disable restore.

        Notes:
        - If enabled, Flash offset must be set.self.
        """
        
        # List of the dictionaries that correspond to the mmwave sdk commands (originally, made for version 04.07.01)
        self.dictionaries_list = list(self.__dict__.keys())
        
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Every other variable that is not a configuration command from the mmwave SDK must be declared bellow here ---------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        # self.c = 3e2 # m/us
        
        self.cfg_file_path = cfg_file_path
        
        return

    def calculate_configuration_metrics(self):
        self.cfg_metrics = {
            "TChirpSampling": None,
            
            "Bandwidth": None,
            "MaxIntermediateFrequency": None,
            
            "nChirpsLoop": None,
            "ADCValidStartTime": None,
            "CarrierFreq": None,
            
            "nRxAntennas": None,
            "nTxAntennas": None,
            "nVirtualAntennas": None,
            
            "maxRadialDistance": None,
            "resolutionRadialDistance": None,
            
            "maxVelocity": None,
            "resolutionVelocity": None,
            
            "maxAzimuth": None,
            "resolutionAzimuth": None,
            
            "maxElevation": None,
            "resolutionElevation": None,
            
        }
        
        # is_tdm = self.chirpCfg['txEnable'] in [1, 2, 4, 8] # values for singular ones in the 4 bits used to select the antennas
        
        self.cfg_metrics['TChirpSampling'] = self.profileCfg['numAdcSamples'] * (self.profileCfg['rampEndTime'] - self.profileCfg['adcStartTime'])
        self.cfg_metrics['Bandwidth'] = self.cfg_metrics['TChirpSampling'] * self.profileCfg['freqSlopeConst']
        self.cfg_metrics['MaxIntermediateFrequency'] = 0.9 / (self.cfg_metrics['TChirpSampling'] * 2)
        self.cfg_metrics['CarrierFreq'] = self.profileCfg['startFreq'] + self.cfg_metrics['Bandwidth']/2
        
        self.cfg_metrics['nRxAntennas'] = bin(int(self.channelCfg['rxChannelEn'])).count("1")
        self.cfg_metrics['nTxAntennas'] = bin(int(self.channelCfg['txChannelEn'])).count("1")
        
        self.cfg_metrics['nVirtualAntennas'] = self.cfg_metrics['nRxAntennas'] * self.cfg_metrics['nTxAntennas']
        
        self.cfg_metrics['resolutionRadialDistance'] = self.C / (2 * self.cfg_metrics['Bandwidth'])
        # self.cfg_metrics['maxRadialDistance'] = self.cfg_metrics['MaxIntermediateFrequency'] * self.C / (2 * self.profileCfg['freqSlopeConst'])
        self.cfg_metrics['maxRadialDistance'] = self.cfg_metrics['resolutionRadialDistance'] * self.profileCfg['numAdcSamples']
        
        self.cfg_metrics['maxVelocity'] = self.C / (4* self.cfg_metrics['CarrierFreq'] * self.cfg_metrics['TChirpSampling']) * self.cfg_metrics['nTxAntennas'] # multiply by the number of simultanious antennas
        
        self.cfg_metrics['resolutionVelocity'] = self.cfg_metrics['maxVelocity'] / (2 * self.profileCfg['numAdcSamples'])
        
        self.cfg_metrics['maxAzimuth'] = 90 # ?
        self.cfg_metrics['resolutionAzimuth'] = None # i dont know how
        
        self.cfg_metrics['maxElevation'] = 90 # ?
        self.cfg_metrics['resolutionElevation'] = None # i dont know how
        
        return
    
    def print_metrics(self):
        print(self.cfg_metrics)
        return
        
    
    def populate_from_file(self, cfg_file_path_input = None):
        """
        Function to read the configuration files for the radar and save the data from its parameters.
        
            If no path given, populate with the one given when the class was created.
            If path is given, update the class path with the new path
        """
        
        if cfg_file_path_input == None:
            cfg_file_path_input = self.cfg_file_path
        else:
            self.cfg_file_path = cfg_file_path_input
        
        if not isinstance(cfg_file_path_input, str):
            print(f'Configuration File Address should be a string')
            return
        
        with open(cfg_file_path_input, 'r') as file:
            for line in file:
                # if line is empty or if its a comment line
                if not line or line.startswith('%'): 
                    continue
                
                parts = line.strip().split()
                dict_name = parts[0]
                values = parts[1:]

                # if there is a dict with the name with the first word in the line
                if hasattr(self, dict_name):
                    dictionary = getattr(self, dict_name)
                    keys = list(dictionary.keys())
                    for i, value in enumerate(values):
                        if i < len(keys):
                            dictionary[keys[i]] = float(value) # populate the dicts
                            
    def print_parameters_parsed(self):
        for dictionary_name in self.dictionaries_list:
            print(f'\n{dictionary_name}:')
            print(getattr(self, dictionary_name))
            
    def print_cfg_metrics(self):
        return