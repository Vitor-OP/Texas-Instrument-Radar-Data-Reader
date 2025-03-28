import numpy as np
import scipy.io
import os

from classes.class_tlv_parser import TLVParser
from classes.class_packet_parser import PacketParser
from classes.class_configuration_parser import ConfigurationParser

class RecordingSerializer:
    """
    Class to gather the data parsed from the PacketParser and ConfigurationParser to Serialize it as an ISO .mat file.
    """
    
    # Collums from the ISO used by Valentin
    DF_COLLUMS =    [ # Information Interface
                    'Number_Of_Valid_Serving_Sensors', 
                    'SensorID', 
                    'Time_Stamp_Measurement', 
                    'Cycle_Counter', 
                    'Interface_Cycle_Time',
                    'Interface_Cycle_Time_Variation',
                    # Information Ambiguity Domain
                    'Radial_Velocity_Ambiguity_Domain',
                    'Range_Ambiguity_Domain',
                    'Angle_Azimuth_Ambiguity_Domain',
                    'Angle_Elevation_Ambiguity_Domain',
                    # Detections
                    'Number_Of_Valid_Detections',
                    # Status
                    'Detection_ID',
                    'Object_ID_Reference',
                    'Time_Stamp_Difference',
                    # Information
                    'Radar_Cross_Section',
                    'Radar_Cross_Section_Error',
                    'Signal_To_Noise_Ratio',
                    'Signal_To_Noise_Ratio_Error',
                    'Number_Of_Valid_Detection_Classifications',
                    'Detection_Classification_Type',
                    # Position
                    'Position_Radial_Distance',
                    'Position_Azimuth',
                    'Position_Elevation',
                    'Position_Radial_Distance_Error',
                    'Position_Azimuth_Error',
                    'Position_Elevation_Error',
                    # Dynamics
                    'Relative_Velocity_Radial_Distance',
                    'Relative_Velocity_Radial_Distance_Error']
    
    def __init__(self, packet_parser: PacketParser, cfg_parser: ConfigurationParser):
        
        self.packet_parser = packet_parser
        self.cfg_parser = cfg_parser
        self.dict_for_populate = {key:float('nan') for key in self.DF_COLLUMS} # dict that will be appended with the iso structure for each frame
        self.dict_populated = {key:[] for key in self.DF_COLLUMS} # dict containing in lists the values of each detection from the dict_for_populate

        return
    
    def populate_dataframe(self):
        # Pre-requisits validation
        if self.packet_parser.packet_counter == 0:
            print('Zero packets stored. Use methode read_recording() to read the recording files.')
            return
        
        detection_index = 0
        recorded_time = 0
        for frame in range(1, self.packet_parser.packet_counter):
            for intra_frame_detection_idx in range(self.packet_parser.objects_per_packet[frame - 1]):
                
                detection_index += 1
                frame_time = (self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_STATS'][0] + self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_STATS'][2])/10e6
                recorded_time += frame_time
                
                try: # Some problem getting the value from the message, maybe when there is 0 or only 1 point in the frame. Here it just pass nothing if there is any probem with the values.           
                    x = self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS'][intra_frame_detection_idx][0]
                    y = self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS'][intra_frame_detection_idx][1]
                    z = self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS'][intra_frame_detection_idx][2]
                    v = self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS'][intra_frame_detection_idx][3]
                    
                    snr = self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO'][intra_frame_detection_idx][0]
                    # noise = self.packet_parser.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO'][intra_frame_detection_idx][1]

                    r = np.sqrt(x**2 + y**2)
                    
                except:
                    x = np.nan
                    y = np.nan
                    z = np.nan
                    v = np.nan
                    
                    snr = np.nan
                    
                    r = np.nan
                
                # Information Interface
                self.dict_for_populate['Number_Of_Valid_Serving_Sensors'] = [float(self.packet_parser.packet_counter)]
                self.dict_for_populate['SensorID'] = [float('nan')]
                self.dict_for_populate['Time_Stamp_Measurement'] = [float(recorded_time)]
                self.dict_for_populate['Cycle_Counter'] = [float(frame)]
                self.dict_for_populate['Interface_Cycle_Time'] = [float('nan')]
                self.dict_for_populate['Interface_Cycle_Time_Variation'] = [float('nan')]

                # Information Ambiguity Domain
                self.dict_for_populate['Radial_Velocity_Ambiguity_Domain'] = [float(-self.cfg_parser.cfg_metrics['maxVelocity']), float(self.cfg_parser.cfg_metrics['maxVelocity'])]
                self.dict_for_populate['Range_Ambiguity_Domain'] = [float(0), float(self.cfg_parser.cfg_metrics['maxRadialDistance'])]
                self.dict_for_populate['Angle_Azimuth_Ambiguity_Domain'] = [float(-self.cfg_parser.cfg_metrics['maxAzimuth']), float(self.cfg_parser.cfg_metrics['maxAzimuth'])]
                self.dict_for_populate['Angle_Elevation_Ambiguity_Domain'] = [float(-self.cfg_parser.cfg_metrics['maxElevation']), float(self.cfg_parser.cfg_metrics['maxElevation'])]

                # Detections
                self.dict_for_populate['Number_Of_Valid_Detections'] = [float(self.packet_parser.total_objects_detected)]

                # Status
                self.dict_for_populate['Detection_ID'] = [float(detection_index)]
                self.dict_for_populate['Object_ID_Reference'] = [float('nan')]
                self.dict_for_populate['Time_Stamp_Difference'] = [float(frame_time)]

                # Information
                self.dict_for_populate['Radar_Cross_Section'] = [float('nan')]
                self.dict_for_populate['Radar_Cross_Section_Error'] = [float('nan')]
                self.dict_for_populate['Signal_To_Noise_Ratio'] = [float(snr)]
                self.dict_for_populate['Signal_To_Noise_Ratio_Error'] = [float('nan')]
                self.dict_for_populate['Number_Of_Valid_Detection_Classifications'] = [float('nan')]
                self.dict_for_populate['Detection_Classification_Type'] = [float(0)]

                # Position
                self.dict_for_populate['Position_Radial_Distance'] = [float(r)]
                self.dict_for_populate['Position_Azimuth'] = [float(np.degrees(np.arctan2(y, x)) - 90)]
                self.dict_for_populate['Position_Elevation'] = [float(np.degrees(np.arctan2(z, r)))]
                self.dict_for_populate['Position_Radial_Distance_Error'] = [float(self.cfg_parser.cfg_metrics['resolutionRadialDistance'])]
                self.dict_for_populate['Position_Azimuth_Error'] = [float('nan')]
                self.dict_for_populate['Position_Elevation_Error'] = [float('nan')]

                # Dynamics
                self.dict_for_populate['Relative_Velocity_Radial_Distance'] = [float(v)]
                self.dict_for_populate['Relative_Velocity_Radial_Distance_Error'] = [float('nan')]
                    
                    
                    
                for key in self.DF_COLLUMS:
                    self.dict_populated[key].append(self.dict_for_populate[key])

                # just for testing
                # if frame > 2:
                #     if any(self.df_iso_structure.columns != self.DF_COLLUMS):
                #         print(f'Warning: iso structure collums incomplete! dp.concat might deleted full empty collum.')

                #     print(self.dict_populated)
                #     return

        return
    
    def save_as_mat_file(self, path = None):
        if self.packet_parser.packet_counter == 0:
            print('Zero packets stored. Use methode read_recording() to read the recording files.')
            return
        
        if path == None:
            path = os.path.dirname(self.packet_parser.recording_path)
        
        file = os.path.basename(self.packet_parser.recording_path[:-4])
        
        scipy.io.savemat(f'{path}/{file}.mat', {'iso': self.dict_populated}, long_field_names=True)
        
        