import numpy as np
from struct import unpack
import csv

channels = [
    ([1.0, 2.0, 3.0, 4.0], [0.0, 0.01, 0.02, 0.03]),  # Channel 1 data (volts, time)
    ([0.5, 1.5, 2.5, 3.5], [0.0, 0.01, 0.02, 0.03]),  # Channel 2 data (volts, time)
    ([0.2, 1.0, 1.8, 2.6], [0.0, 0.01, 0.02, 0.03]),  # Channel 3 data (volts, time)
]

def get_waveform_with_time(options):
    x_increment = options.get("x_increment")
    values=options.get("raw_scope_data")
    volts = ossiloscope_data_preprocessing(options)
    time = np.arange(0, x_increment * len(volts), x_increment)
    return volts, time.tolist()

def get_multi_channel_waveform_with_time(options):
    """
    Retrieve waveform data with corresponding time values for multiple channels from the oscilloscope.
    """
    waveform_data = []
    for channel in channels:
        data = get_waveform_with_time(options)
        waveform_data.append(data)
    return tuple(waveform_data)  # Reason for tuple format: Immutable and efficient.

def save_waveform_to_csv(options):
    """
    Save waveform data to a CSV file.
    """
    file_path = options.get("file_path") #'C:\\Users\\User\\Desktop\\blaze-cloud\\blaze-cloud-controller\\blaze_cloud\\test.csv'
    volts, time = get_waveform_with_time(options)
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Voltage'])
        for t, v in zip(time, volts):
            writer.writerow([t, v])

def save_waveform_to_csv_multi_channel(options):
    """
    Save multichannel waveform data to a CSV file.
    """
    file_path =  options.get("file_path") #'C:\\Users\\User\\Desktop\\blaze-cloud\\blaze-cloud-controller\\blaze_cloud\\test.csv'
    print(file_path)
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time'] + [f'Channel {i + 1} Voltage' for i in range(len(channels))])

        for i, time_point in enumerate(channels[0][1]):
            row = [time_point]  # Start each row with the corresponding time point
            for volts, _ in channels:
                if i < len(volts):
                    row.append(volts[i])
                else:
                    row.append('')  # Fill with empty string if the channel data is shorter
            writer.writerow(row)

def ossiloscope(options):
#seperate the reading part also add a function that reads the data from the ossiloscope and customize and format into options format and type

    """
    Handles the oscilloscope method.
    """
    try:
        values=options.get("binary_values")
        float_array = np.array([float(int(binary, 2)) for binary in values])
    except ValueError as e:
        print(f"Error converting binary to floats: {e}")
        return []

    padding_value = options.get("padding_value")
    operation = options.get("operation").lower()

    try:
        if operation == "negative":
            modified_values = float_array - padding_value
        elif operation == "additive":
            modified_values = float_array + padding_value
        elif operation == "multiplication":
            modified_values = float_array * padding_value
        elif operation == "division":
            if padding_value == 0:
                raise ValueError("Division by zero is not allowed.")
            modified_values = float_array / padding_value
        else:
            return "Error: Unsupported operation"
    except Exception as e:
        print(f"Error processing values: {e}")
        return []

    return modified_values.tolist()

def ossiloscope_data_preprocessing(options):
    """
    Preprocess oscilloscope data.
    """
    y_origin = options.get("y_origin")
    y_reference = options.get("y_reference")
    y_increment = options.get("y_increment")
    x_increment = options.get("x_increment")
#-----------------------------------------------------------------------------------------------
    scope_raw_data =options.get("scope_raw_data")
    header_length = 2 + int(scope_raw_data[1])
    scope_raw_data = scope_raw_data[header_length:-1]

    scope_data = np.array(unpack('%sB' % len(scope_raw_data), scope_raw_data))
    volts = (scope_data - y_origin - y_reference) * y_increment
    return volts.tolist()

def handle_incoming_data(method,options):
    """
    Handles incoming data based on the given method and options.
    """
    methods = {
        "ossiloscope": ossiloscope,
        "ossiloscope-data-preprocessing": ossiloscope_data_preprocessing,
        "get_waveform_with_time": get_waveform_with_time,
        "get_multi_channel_waveform_with_time": get_multi_channel_waveform_with_time,
        "save_waveform_to_csv": save_waveform_to_csv,
        "save_waveform_to_csv_multi_channel": save_waveform_to_csv_multi_channel,
    }

    if method in methods:
        return methods[method](options)
    else:
        return f"Error: Method '{method}' not implemented"

if __name__ == "__main__":
    
    binary_values = ['0b101', '0b111', '0b1001']
    method_name = "ossiloscope"
    scope_raw_data = (
        b'\x00\x00\x80\x3f' 
        b'\x00\x00\x00\x40'  
        b'\x00\x00\x40\x40'  
        b'\x00\x00\x80\x40'  
        b'\x00\x00\xa0\x40'  
        b'\x00\x00\xc0\x40'  
        b'\x00\x00\xe0\x40'  
        b'\x00\x00\x00\x41'  
    )
    options = {
        "padding_value": 0.5, 
        "operation": "additive",
        "y_origin": 2,
        "y_reference": 3,
        "y_increment": 4,
        "x_increment": 8,
        "scope_raw_data":scope_raw_data,
        "binary_values":binary_values,  
        
    }
    result = handle_incoming_data(method_name, options)
    print(result)
    

    method_name = "ossiloscope-data-preprocessing"
    result = handle_incoming_data(method_name, options)
    print(result)
    
    method_name = "get_waveform_with_time"
    options.update({"file_path": 'C:\\Users\\User\\Desktop\\blaze-cloud\\blaze-cloud-controller\\blaze_cloud\\test.csv'})
    result = handle_incoming_data(method_name, options)
    print("gwt", result)
    
    method_name = "save_waveform_to_csv"
    result = handle_incoming_data(method_name, options)
    print("single_channel_csv", result)
    
    method_name = "save_waveform_to_csv_multi_channel"
    result = handle_incoming_data(method_name, options)
    print("multi_channel_csv", result)
    
#write a function to read data from ossciloscope 