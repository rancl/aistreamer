#!/usr/bin/env python

# Copyright (c) 2018 Google LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Streaming shot change annotation sample.

This application demonstrates how to perform streaming shot change detection
with the Google Cloud Video Intelligence API.

For more information, check out the documentation at
https://cloud.google.com/video-intelligence/docs.

Usage Example:
    $ python streaming_shot_detection.py file_path.mp4

Sample Output:
    Reading response.
    Shot: 0.0s to 4.170837s
    Shot: 4.204204s to 7.107107s
    Shot: 7.140473s to 11.778445s
    Shot: 11.811811s to 17.28395s
    Shot: 17.317317s to 20.82082s
    Shot: 20.854187s to 24.591257s
    Shot: 24.624624s to 30.063396s

"""
from __future__ import print_function

import argparse

from google.cloud import videointelligence
from google.cloud.videointelligence import enums
from google.cloud.videointelligence import types


def stream(file_object, chunk_size):
  """Reads a file in chunks."""
  while True:
    data = file_object.read(chunk_size)
    if not data:
      break
    yield data


def streaming_annotate(stream_file):
  """Annotate a local video file through streaming API."""

  client = videointelligence.StreamingVideoIntelligenceServiceClient()
  # Set the chunk size to 5MB (recommended less than 10MB).
  chunk_size = 5 * 1024 * 1024

  # Open file.
  with open(stream_file) as video_file:
    requests = (
      types.StreamingAnnotateVideoRequest(input_content=chunk)
      for chunk in stream(video_file, chunk_size))

    # Set streaming config.
    config = types.StreamingVideoConfig(
        feature=enums.StreamingFeature.STREAMING_SHOT_CHANGE_DETECTION)
    config_request = types.StreamingAnnotateVideoRequest(video_config=config)

    # streaming_annotate_video returns a generator.
    # timeout argument specifies the maximum allowable time duration between
    # the time that the last packet is sent to Google video intelligence API
    # and the time that an annotation result is returned from the API.
    # timeout argument is represented in number of seconds.
    responses = client.streaming_annotate_video(
        config_request, requests, timeout=10800)

    print('\nReading response.')
    # Retrieve results from the response generator.
    for response in responses:
      for annotation in response.annotation_results.shot_annotations:
        print('Shot: {}s to {}s'.format(
            annotation.start_time_offset.seconds +
            annotation.start_time_offset.nanos / 1e9,
            annotation.end_time_offset.seconds +
            annotation.end_time_offset.nanos / 1e9))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      'file_path', help='Local file location for streaming video annotation.')
  args = parser.parse_args()

  streaming_annotate(args.file_path)