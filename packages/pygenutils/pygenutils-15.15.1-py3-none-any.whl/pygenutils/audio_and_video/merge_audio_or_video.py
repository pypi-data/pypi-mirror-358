#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'merge_individual_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.audio_and_video.audio_and_video_manipulation import merge_individual_media_files

#-------------------#
# Define parameters #
#-------------------#

# Simple data #
#-------------#

OUTPUT_EXT = "mp4"

# Input media #
#-------------#

# Media input can be a list of files or a single file containing file names
MEDIA_INPUT = []
# MEDIA_INPUT = "media_name_containing_file.txt"

# Output media #
#--------------#

# Merged media file #
OUTPUT_FILE_NAME = f"merged_media_file.{OUTPUT_EXT}"
# OUTPUT_FILE_NAME = None

# Zero-padding and bit rate factor #
"""The factor is multiplied by 32, so that the bit rate is in range [32, 320] kBps"""
QUALITY = 4

# Safe mode for ffmpeg #
# If True, ffmpeg runs in safe mode to prevent unsafe file operations
SAFE = True

# Overwrite existing files #
# If True, uses '-y' flag; if False, uses '-n' flag (will not overwrite)
OVERWRITE = True

# Command execution parameters #
CAPTURE_OUTPUT = False
RETURN_OUTPUT_NAME = False
ENCODING = "utf-8"
SHELL = True

#------------#
# Operations #
#------------#

merge_individual_media_files(
    MEDIA_INPUT,
    safe=SAFE,
    output_file_name=OUTPUT_FILE_NAME,
    quality=QUALITY,
    overwrite=OVERWRITE,
    capture_output=CAPTURE_OUTPUT,
    return_output_name=RETURN_OUTPUT_NAME,
    encoding=ENCODING,
    shell=SHELL
)