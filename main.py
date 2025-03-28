import os
import argparse

from classes.class_packet_parser import PacketParser
from classes.class_recording_serializer import RecordingSerializer
from classes.class_configuration_parser import ConfigurationParser

def find_recordings(test_folder):
    configuration_folders = []

    for folder in os.listdir(test_folder):
        configuration_folders.append(f'{test_folder}/{folder}')

    cfg_to_recording_dict = {}
    cfg_counter = 1

    for cfg_folder in configuration_folders:
        profile_files = os.listdir(cfg_folder)

        cfg_file = [file for file in profile_files if file.endswith('.cfg')][0]  # Should have only one configuration per folder.
        cfg_file_path = f'{cfg_folder}/{cfg_file}'

        scene_folders = [file for file in profile_files if file != cfg_file]
        scene_file_path = [f'{cfg_folder}/{scene}' for scene in scene_folders]
        
        scene_recordings_paths = []
        print(f'Configuration: {cfg_file}')
        
        for scene in scene_file_path:
            files = os.listdir(scene)
            recording_file = [recording for recording in files if recording.endswith('.dat')]
            print(f'    {scene}   -   {recording_file}')
            
            if recording_file:  # if not empty folder
                recording_path = f'{scene}/{recording_file[0]}'  # should have only one recording file per folder
                scene_recordings_paths.append(recording_path)
            else:
                continue

        cfg_to_recording_dict[cfg_file_path] = scene_recordings_paths
            
    return cfg_to_recording_dict

def translate_data(cfg_to_recording_dict, no_plot = False):
    for cfg, recordings_list in cfg_to_recording_dict.items():
        print(f'Configuration: {cfg}')
        for recording in recordings_list:
            print(f'    {recording}')
            serializer = RecordingSerializer(packet_parser=PacketParser(recording), cfg_parser=ConfigurationParser(cfg))
            serializer.packet_parser.read_recording()
            
            if not no_plot:
                serializer.packet_parser.plot_detections_timeline(show_plot=False, save_figure = True)
            
            serializer.cfg_parser.populate_from_file()
            serializer.cfg_parser.calculate_configuration_metrics()
            
            serializer.populate_dataframe()
            serializer.save_as_mat_file()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find .cfg and .dat recordings from a given folder.')
    parser.add_argument('test_folder', type=str, help='Path to the test folder')
    parser.add_argument('--no_plot', action='store_true', help='Disable plotting of recordings')

    args = parser.parse_args()

    cfg_to_recording_dict = find_recordings(args.test_folder)
    
    print('\nThese are the detected radar recordings.')
    procede = input('Do you want to procede? [y/n]')
    
    print(args.no_plot)
    
    yes_aliases = ['y', 'yes', 'Y', 'YES']

    if procede in yes_aliases:
        print('\nProcessing recordings...\n')
        translate_data(cfg_to_recording_dict, no_plot=args.no_plot)
        
    else:
        print('Exiting without processing recordings.')
    
    
    