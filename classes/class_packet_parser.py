import struct
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

from classes.class_tlv_parser import TLVParser


class PacketParser:
    """
    Class to parse radar data packets from a binary file.
    
    The methode plot_detections_timeline() is a nice exemple on how to access the data parsed.
    
    """
    
    # Define packet header format
    HEADER_FORMAT = "4H 8I"  # 4 uint16_t + 8 uint32_t
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    """
        AWR2944EVM SDK 04.07.00.01:
        (MagicWorld, MagicWorld, MagicWorld, MagicWorld, 
        version, totalPacketLen, Plataform, frameNumber, timeCpuCycles, numDetectedObj, numTLVs, subFrameNumber)
    """

    # Define TLV header format
    TLV_HEADER_FORMAT = "2I"  # TLV type (uint32) + TLV length (uint32)
    TLV_HEADER_SIZE = struct.calcsize(TLV_HEADER_FORMAT)

    # Define the magic word
    MAGIC_WORD = struct.pack("4H", 0x0102, 0x0304, 0x0506, 0x0708)

    def __init__(self, recording_path):
        self.recording_path = recording_path
        self.message_type_counts = defaultdict(int)
        self.unknown_packets = []
        self.zero_objects_packet = []
        self.objects_per_packet = []
        self.total_objects_detected = 0
        self.packet_counter = 0
        self.parsed_tlvs = defaultdict(dict)

    def find_first_magic_word(self):
        with open(self.recording_path, "rb") as f:
            file_size = f.seek(0, 2)
            f.seek(0)
            
            buffer_size = 4096
            search_window = b""
            position = 0
            
            while position < file_size:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                
                search_window += chunk
                magic_index = search_window.find(self.MAGIC_WORD)
                if magic_index != -1:
                    return position + magic_index
                
                search_window = search_window[-7:]
                position += buffer_size - 7
        
        return -1
    
    def find_next_magic_word(self, start_position):
        """
        Finds the next occurrence of the magic word in the binary file starting from a given position.
        
        Parameters:
            start_position (int): The position in the file to start searching from.
        
        Returns:
            int: The position of the next magic word, or -1 if none is found.
        """
        with open(self.recording_path, "rb") as f:
            f.seek(start_position)
            file_size = f.seek(0, 2)
            f.seek(start_position)
            
            buffer_size = 4096
            search_window = b""
            position = start_position
            
            while position < file_size:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                
                search_window += chunk
                magic_index = search_window.find(self.MAGIC_WORD)
                if magic_index != -1:
                    return position + magic_index
                
                search_window = search_window[-7:]  # Keep last bytes in case magic word is split across chunks
                position += buffer_size - 7
        
        return -1
    
    def read_recording(self):
        magic_word_addr = self.find_first_magic_word()
        if magic_word_addr == -1:
            print('No Magic Word was found in file.')
            return -1

        with open(self.recording_path, "rb") as f:
            file_size = f.seek(0, 2)
            f.seek(magic_word_addr)
            
            while f.tell() < file_size:
                start_pos = f.tell()
                self.packet_counter += 1
                header_data = f.read(self.HEADER_SIZE)
                
                if len(header_data) < self.HEADER_SIZE:
                    print("Incomplete packet header. Stopping.")
                    break

                unpacked_data = struct.unpack(self.HEADER_FORMAT, header_data)
                magic_word = struct.pack("4H", *unpacked_data[:4])
                total_packet_len = unpacked_data[5]
                detected_objects = unpacked_data[9]
                num_tlvs = unpacked_data[10]
                
                if magic_word != self.MAGIC_WORD:
                    print(f"Invalid magic word found at packet {self.packet_counter}. Searching for the next magic word...")
                    next_magic_pos = self.find_next_magic_word(start_pos + 2)  # Skip ahead and find the next magic word
                    if next_magic_pos == -1:
                        print("No more valid magic words found.")
                        break
                    f.seek(next_magic_pos)
                    self.objects_per_packet.append(0)
                    continue
                
                if total_packet_len <= self.HEADER_SIZE:
                    print(f"Invalid packet length ({total_packet_len} bytes). Skipping packet.")
                    self.objects_per_packet.append(0)
                    continue
                
                self.objects_per_packet.append(detected_objects)
                
                if detected_objects == 0:
                    self.zero_objects_packet.append(self.packet_counter)
                
                bytes_read = self.HEADER_SIZE
                
                for _ in range(num_tlvs):
                    if bytes_read + self.TLV_HEADER_SIZE > total_packet_len:
                        break
                    
                    tlv_header = f.read(self.TLV_HEADER_SIZE)
                    if len(tlv_header) < self.TLV_HEADER_SIZE:
                        break
                    
                    bytes_read += self.TLV_HEADER_SIZE
                    tlv_type, tlv_length = struct.unpack(self.TLV_HEADER_FORMAT, tlv_header)
                    tlv_data = f.read(tlv_length)
                    
                    parsed_tlv = TLVParser.parse_tlv(tlv_type, tlv_data, self.packet_counter)
                    
                    if parsed_tlv:
                        # Register the amount of messages in the file                        
                        if tlv_type in self.message_type_counts:
                            self.message_type_counts[tlv_type] += 1
                        else:
                            self.message_type_counts[tlv_type] = 1
                        
                        # Store the data from the messages
                        self.parsed_tlvs[self.packet_counter][parsed_tlv['type']] = parsed_tlv['parsed_data']
                        
                    else:
                        self.unknown_packets.append(self.packet_counter)
                    
                    bytes_read += tlv_length
                
                expected_end_pos = start_pos + total_packet_len
                f.seek(expected_end_pos, 0)
                
        self.total_objects_detected = sum(self.objects_per_packet)

    def print_summary(self, frame_window = None, frame_step:int = 1):
        
        # Pre-requisits validation
        if self.packet_counter == 0:
            print('Zero packets stored. Use methode read_recording() to read the recording files.')
            return
        
        # General recording informations.
        print(f"Total Frames: {self.packet_counter}")
        print(f'Total objects detected: {self.total_objects_detected}')
        print(f'Zero objects Frames: {len(self.zero_objects_packet)}')
        print(f'Unknown message types: {len(self.unknown_packets)}')
        print("Message Type Counts:")
        
        for msg_type, count in self.message_type_counts.items():
            print(f"  {TLVParser.get_message_names_dict()[msg_type]}: {count}")

        # Input validation
        if frame_window != None:
            if isinstance(frame_window, tuple):
                if len(frame_window) != 2 or not all(isinstance(i, (int)) for i in frame_window):
                    print(f'ERROR: \nFrame interval invalid! Should be (int, int)')
                    return
                
                if min(frame_window) < 1 or max(frame_window) > self.packet_counter:
                    print(f'ERROR: \nInterval {frame_window} out of bounts (1, {self.packet_counter})')
                    return
                
                frame_window = (min(frame_window), max(frame_window))
            
            elif isinstance(frame_window, int):
                if frame_window > self.packet_counter or frame_window < 1:
                    print(f'ERROR: Out of bounds request! {frame_window}. Total frames ({self.packet_counter})')
                    return
                
                frame_window = (1, frame_window)
                
            else:
                print('The input must be an int = n_frames or tuple = frame_interval.')
                return

            # Printing TLVs for each frame
            print()
            print("Parsed TLVs:")
            for frame in range(frame_window[0], frame_window[1] + 1, frame_step):
            # for _, tlv_dict in self.parsed_tlvs.items():
                tlv_dict = self.parsed_tlvs.get(frame)
                print(f"Frame {frame}:")
                print(f"  Number of detected objects: {self.objects_per_packet[frame - 1]}")
                for tlv_type, tlv_data in tlv_dict.items():
                    print(f"  {tlv_type}: {tlv_data}")

    def plot_detections_timeline(self, min_range_threshold = 1, recording_name = None, save_figure = False, show_plot = True):
        # Pre-requisits validation
        if self.packet_counter == 0:
            print('Zero packets stored. Use methode read_recording() to read the recording files.')
            return
        
        if self.total_objects_detected == 0:
            print('Zero objects in the recording')
            return
        
        range_frame_list = []
        frame_list = []
        velocity_frame_list = []
        azimuth_frame_list = []
        elevation_frame_list= []
        
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(30, 15), sharex=True, dpi=300)
        
        # Nice exemple of how to get the data from the recording:
        # Get the distance and velocity of each point from the recording.

        for frame in range(1, self.packet_counter):
            try:  # Important when getting points data because package might not contain any (zero detection frame)
                for point in self.parsed_tlvs[frame]['MMWDEMO_OUTPUT_MSG_DETECTED_POINTS']:  # point cloud data (x, y, z, velocity)
                    range_value = np.sqrt(point[0]**2 + point[1]**2 + point[2]**2)
                    if range_value >= min_range_threshold:
                        velocity_frame_list.append(point[3])
                        range_frame_list.append(range_value)
                        azimuth_frame_list.append(np.degrees(np.arctan2(point[1], point[0])) - 90)
                        elevation_frame_list.append(np.degrees(np.arctan2(point[2], np.sqrt(point[0]**2 + point[1]**2))))
                        frame_list.append(frame)
            except:
                pass
        
        # Plot n detected objects per frame
        ax1.plot(range(self.packet_counter), self.objects_per_packet, marker='o', markersize=2, linestyle='-', color='b', linewidth=0.5)
        ax1.set_ylabel('Number of Detections')
        ax1.grid(True)
        
        # Plot doppler per frame
        ax2.scatter(frame_list, velocity_frame_list, marker='o', color='b', alpha = 0.1)
        ax2.set_ylabel('Speed (m/s)')
        # ax2.set_ylim(-4, 4) # some recordings have speed values outside of the unambiguous range
        # ax2.set_ylim(-max(velocity_frame_list)*1.1, max(velocity_frame_list)*1.1)
        ax2.grid(True)
        
        # Plot range per frame
        ax3.scatter(frame_list, range_frame_list, marker='o', color='b', alpha = 0.05)
        ax3.set_ylim(0, max(range_frame_list)*1.1)
        ax3.set_ylabel('Range (m)')
        ax3.grid(True)
        
        # Plot azimuth per frame
        ax4.scatter(frame_list, azimuth_frame_list, marker='o', color='b', alpha=0.05)
        ax4.set_ylabel('Azimuth (rad)')
        ax4.grid(True)
        
        # Plot elevation per frame
        ax5.scatter(frame_list, elevation_frame_list, marker='o', color='b', alpha=0.05)
        ax5.set_ylabel('Elevation (rad)')
        ax5.grid(True)
        
        # recording_name = os.path.basename(self.recording_path)
        recording_name = self.recording_path
        
        fig.suptitle(f'Time line of file: {recording_name}', fontsize=24)  # Set the title with a larger font size
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the layout to make space for the title

        plt.xlabel('Packet Number/Recording Frame Number')
        plt.xlim([0, self.packet_counter])
        
        if show_plot:
            plt.show()
        
        if save_figure:
            plt.savefig(f'{self.recording_path[:-4]}.png')
            
        plt.close()