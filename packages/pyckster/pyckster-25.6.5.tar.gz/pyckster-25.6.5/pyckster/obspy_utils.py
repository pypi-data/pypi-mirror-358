import os
import re
import numpy as np
import obspy

#######################################
# Obspy functions
#######################################
def read_seismic_file(seismic_file, separate_sources=False):
    '''
    Read a seismic file and return a list of streams, one for each source.

    Parameters
    ----------
    seismic_file : str
        The path to the seismic file.
    separate_sources : bool, optional
        If True, separate the traces into different streams based on the original_field_record_number.
        Default is False.
        
    Returns
    -------
    stream : obspy.Stream
        The stream object containing the seismic data.
    '''
    # Read the seismic file
    stream = obspy.read(seismic_file,unpack_trace_headers=True)

    input_format = check_format(stream)

    if input_format == 'seg2':
        input_format = 'segy'
        # Extract the FFID from the file name (any number in the file name)
        file_base_name = os.path.basename(seismic_file) # Get the base name of the file
        file_base_name, _ = os.path.splitext(file_base_name) # Remove the extension
        ffid = re.findall(r'\d+', file_base_name) # Find any number in the file name
        if ffid:
            ffid = int(ffid[0])
        else:
            ffid = 1

        stream.write('tmp.sgy',format='SEGY',data_encoding=5, byteorder='>')
        stream = obspy.read('tmp.sgy',unpack_trace_headers=True)
        os.remove('tmp.sgy')
        for trace_index, trace in enumerate(stream):
            trace.stats[input_format].trace_header.trace_sequence_number_within_line = trace_index+1 #tracl
            trace.stats[input_format].trace_header.trace_sequence_number_within_segy_file = trace_index+1 #tracr
            trace.stats[input_format].trace_header.original_field_record_number = ffid #fldr
            trace.stats[input_format].trace_header.trace_number_within_the_original_field_record = trace_index+1 #tracf
    
    if separate_sources:
        stream = separate_streams(stream)

    return stream

def check_format(stream):
    '''
    Check the input format of the stream.
    
    Parameters
    ----------
    stream : obspy.Stream
        The stream object containing the seismic data.
        
    Returns
    -------
    input_format : str
        The input format of the stream.
    '''

    if hasattr(stream[0].stats, 'su'):
        input_format = 'su'
    elif hasattr(stream[0].stats, 'segy'):
        input_format = 'segy'
    elif hasattr(stream[0].stats, 'seg2'):
        input_format = 'seg2'
    else:
        raise ValueError('The input format is not recognized')
    
    return input_format

def separate_streams(stream):
    '''
    Separate the traces into different streams based on the original_field_record_number.

    Parameters
    ----------
    stream : obspy.Stream
        The stream object containing the seismic data.

    Returns
    -------
    streams : list
        A list of streams, one for each source.
    '''
    
    # Check the input format
    input_format = check_format(stream)
        
    # Get the unique original_field_record_number values
    unique_record_numbers = sorted(list(set(trace.stats[input_format].trace_header.original_field_record_number for trace in stream)))
    
    # Initialize an empty list to store the shot gathers in different streams
    streams = []
    
    # Iterate over the unique record numbers
    for record_number in unique_record_numbers:
        # Select the traces with the current record number and add them to the list
        substream = obspy.Stream([trace for trace in stream if trace.stats[input_format].trace_header.original_field_record_number == record_number])
        streams.append(substream)
    
    return streams

def merge_streams(streams):
    """
    Merge multiple streams into a single stream.

    Parameters
    ----------
    streams : list
        A list of obspy.Stream objects to be merged.

    Returns
    -------
    merged_stream : obspy.Stream
        The merged stream containing all traces from the input streams.
    """
    
    merged_stream = streams[0].copy()  # Start with a copy of the first stream
    for stream in streams[1:]:  # Iterate over the rest of the streams
        merged_stream += stream  # Add each stream to the merged stream

    return merged_stream

def swap_traces(stream, trace1, trace2):
    """
    Switch the amplitude data of two traces in a stream.
    
    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    trace1 : int
        Index of the first trace.
    trace2 : int
        Index of the second trace.
        
    Returns
    -------
    stream : obspy.Stream
        Stream with the amplitude data of the two traces switched.
    """

    input_format = check_format(stream)

    # Copy the traces based on the trace indices in header
    tr1 = [trace for trace in stream if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == trace1]
    tr2 = [trace for trace in stream if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == trace2]

    if not tr1 or not tr2:
        raise ValueError("Trace not found in the stream")

    tr1 = tr1[0]
    tr2 = tr2[0]
    
    # Switch the amplitude data
    tr1.data, tr2.data = tr2.data.copy(), tr1.data.copy()

    return stream

def remove_trace(stream, removed_trace):
    """
    Remove trace from a stream based on their trace numbers.

    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    removed_trace : int
        First trace number to remove.

    Returns
    -------
    stream : obspy.Stream
        Stream with the specified traces removed.
    """

    input_format = check_format(stream)

    # Remove trace based on the trace numbers in header
    for trace in stream :
        if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == removed_trace:
            stream.remove(trace)
            break

    return stream

def move_trace(stream, moved_trace, new_position):
    """
    Move trace in a stream based on their trace numbers.

    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    moved_trace : int
        First trace number to move.
    new_position : int
        New position for the trace.

    Returns
    -------
    stream : obspy.Stream
        Stream with the specified trace moved to the new position.
    """

    input_format = check_format(stream)

    # Find the trace to move
    for i, trace in enumerate(stream):
        if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == moved_trace:
            # Remove the trace from its current position
            stream.remove(trace)
            # Insert it at the new position
            stream.insert(new_position, trace)
            break

    # Reset the trace sequence numbers
    for i, trace in enumerate(stream):
        trace.stats[input_format].trace_header.trace_sequence_number_within_line = i + 1
        trace.stats[input_format].trace_header.trace_sequence_number_within_segy_file = i + 1
        trace.stats[input_format].trace_header.original_field_record_number = trace.stats[input_format].trace_header.original_field_record_number
        trace.stats[input_format].trace_header.trace_number_within_the_original_field_record = i + 1

    return stream

def mute_trace(stream, muted_trace):
    """
    Mute trace in a stream based on their trace numbers.

    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    muted_trace : int
        First trace number to mute.

    Returns
    -------
    stream : obspy.Stream
        Stream with the specified traces muted.
    """

    input_format = check_format(stream)

    # Mute trace based on the trace numbers in header
    for trace in stream :
        if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == muted_trace:
            trace.data = np.zeros(trace.data.shape)
            break

    return stream

def swap_header_format(stream,output_format):

    output_format = output_format.lower()

    input_format = check_format(stream)
    
    for trace in stream:
        # Get the AttribDict for the input format
        attrib_dict = trace.stats[input_format]
        # Create a new AttribDict for the output format
        trace.stats[output_format] = obspy.core.AttribDict()

        # Iterate over the items in the AttribDict
        for key, value in attrib_dict.items():
            trace.stats[output_format][key] = value

        trace.stats._format = output_format.upper()

        # Delete the input format AttribDict
        if input_format != output_format:
            del trace.stats[input_format]

    stream._format = output_format.upper()

    return stream

def get_max_decimals(positions):
    # Extract unique x and z positions
    unique_positions = np.unique(positions)

    # Function to count decimals
    def count_decimals(number):
        s = str(number)
        if '.' in s:
            return len(s.split('.')[1])
        else:
            return 0

    # Count decimals for each unique position
    decimals = [count_decimals(pos) for pos in unique_positions]

    # Return the maximum number of decimals
    return max(decimals)