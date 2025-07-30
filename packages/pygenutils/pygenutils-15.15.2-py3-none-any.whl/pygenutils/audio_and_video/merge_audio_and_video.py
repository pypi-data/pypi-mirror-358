#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'merge_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from filewise.file_operations.path_utils import find_files
from pygenutils.audio_and_video.audio_and_video_manipulation import merge_media_files

#-------------------#
# Define parameters #
#-------------------#

# Simple data #
#-------------#

# File type delimiters #
AUDIO_DELIMITER = "audio"
VIDEO_DELIMITER = "video"

# File extensions and globstrings #
AUDIO_EXTENSION = "mp3"
AUDIO_FILE_PATTERN = f"_{AUDIO_DELIMITER}.{AUDIO_EXTENSION}"

VIDEO_EXTENSION = "mp4"
VIDEO_FILE_PATTERN = f"_{VIDEO_DELIMITER}.{VIDEO_EXTENSION}"

# Path to walk into for file searching #
SEARCH_PATH = "../Curso_superior_ML/"

# Input media #
#-------------#

# Set common keyword arguments #
COMMON_KWARGS = dict(search_path=SEARCH_PATH, match_type="glob_left")

# Find target audio and video files #
INPUT_AUDIO_FILE_LIST = find_files(AUDIO_FILE_PATTERN, **COMMON_KWARGS)
INPUT_VIDEO_FILE_LIST = find_files(VIDEO_FILE_PATTERN, **COMMON_KWARGS)

# Output media #
#--------------#

# Name output file names manually #
"""Taking into account the names of the files, the simplest way to rename them is by removing the item type"""

OUTPUT_FILE_NAME_LIST = [
    f"{input_audio_file.split(AUDIO_DELIMITER)[0][:-1]}.{VIDEO_EXTENSION}"
    for input_audio_file in INPUT_AUDIO_FILE_LIST
]
# OUTPUT_FILE_NAME_LIST = None

# Zero-padding and bit rate factor #
"""The factor is multiplied by 32, so that the bit rate is in range [32, 320] kBps"""
ZERO_PADDING = None
QUALITY = 4

# Overwrite existing files #
# If True, uses '-y' flag; if False, uses '-n' flag (will not overwrite)
OVERWRITE = True

# Command execution parameters #
CAPTURE_OUTPUT = True
RETURN_OUTPUT_NAME = False
ENCODING = "utf-8"
SHELL = True

#-------------------#
# Program operation #
#-------------------#

merge_media_files(
    INPUT_VIDEO_FILE_LIST,
    INPUT_AUDIO_FILE_LIST,
    output_file_list=OUTPUT_FILE_NAME_LIST,
    zero_padding=ZERO_PADDING,
    quality=QUALITY,
    overwrite=OVERWRITE,
    capture_output=CAPTURE_OUTPUT,
    return_output_name=RETURN_OUTPUT_NAME,
    encoding=ENCODING,
    shell=SHELL
)

