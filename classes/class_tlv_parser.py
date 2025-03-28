import struct
from collections import defaultdict
import numpy as np

class TLVParser:
    """Class to parse TLV messages based on their type."""
    
    # Dictionary containing the index of each message type that come in the packet, having the values as the name of the message type and its size
    # This should be everything you need to change case the mmwave sdk change the communication of the packages in the mmwave demos.
    TLV_FORMATS = {
        1: ("MMWDEMO_OUTPUT_MSG_DETECTED_POINTS", "4f"), # Length = NObjects * 4f (x, y, z, velocity)
        2: ("MMWDEMO_OUTPUT_MSG_RANGE_PROFILE", "H"), # Length = RangeFFTsize * uint16_t (Array of profile points at 0th Doppler (stationary objects). The points represent the sum of log2 magnitudes of received antennas expressed in Q9 format.)
        3: ("MMWDEMO_OUTPUT_MSG_NOISE_PROFILE", "H"), # Length = RangeFFTsize * uint16_t (This is the same format as range profile but the profile is at the maximum Doppler bin (maximum speed objects))
        4: ("MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP", "hh"), # Not used
        5: ("MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP", None),
        6: ("MMWDEMO_OUTPUT_MSG_STATS", "6I"), # Length = 6I (interFrameProcessingTime, transmitOutputTime, interFrameProcessingMargin, interChirpProcessingMargin, activeFrameCPULoad, interFrameCPULoad)
        7: ("MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO", "2h"), # Length = NObjects * 2I (snr, noise)
        8: ("MMWDEMO_OUTPUT_MSG_AZIMUT_ELEVATION_STATIC_HEAT_MAP", None),
        9: ("MMWDEMO_OUTPUT_MSG_TEMPERATURE_STATS", "I6h"),  # What ever
    }
    
    @classmethod
    def parse_tlv(cls, tlv_type, data, packet_index):
        """Parses a TLV based on its type and associates it with a packet index."""
        struct_name, fmt = cls.TLV_FORMATS.get(tlv_type, (None, None))
        
        if not struct_name:
            return None
        
        struct_size = struct.calcsize(fmt)
        num_entries = len(data) // struct_size
        parsed_data = [struct.unpack(fmt, data[i * struct_size:(i + 1) * struct_size]) for i in range(num_entries)]
        
        if parsed_data:        
            if isinstance(parsed_data[0], tuple) and len(parsed_data) == 1:
                parsed_data = [*parsed_data[0]]
        
        else:
            parsed_data = np.nan
        
        return {
            "type": struct_name,
            "parsed_data": parsed_data,
            "packet_index": packet_index
        }
    
    @classmethod
    def get_message_names_dict(cls):
        messages_type_dict = {}
        for key, value in cls.TLV_FORMATS.items():
            messages_type_dict[key] = value[0]
            
        return messages_type_dict