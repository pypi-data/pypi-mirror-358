import boto3

def get_channels():
    """
    Return channels that have a 'video_data' subdirectory within the 'cliptu' bucket.

    Args:
        None

    Returns:
        List[str]: A list of channel names that contain 'video_data'.
    """
    s3 = boto3.client('s3')
    bucket_name = 'cliptu'
    channels_with_video_data = []

    # List all objects in the bucket with '/' as delimiter to get folder-like prefixes
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Delimiter='/')

    for page in pages:
        if 'CommonPrefixes' in page:
            for prefix in page['CommonPrefixes']:
                channel_prefix = prefix['Prefix']
                # Now check inside each channel if there is a 'video_data' folder
                subfolder_response = s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=channel_prefix,
                    Delimiter='/'
                )
                # Check if 'video_data' is in the subdirectories
                if 'CommonPrefixes' in subfolder_response:
                    for subprefix in subfolder_response['CommonPrefixes']:
                        if 'video_data/' in subprefix['Prefix']:
                            # The channel has a 'video_data' folder, add to list
                            channel_name = channel_prefix.strip('/')
                            if channel_name not in channels_with_video_data:
                                channels_with_video_data.append(channel_name)
                            break  # Once found, no need to check further in this channel

    if not channels_with_video_data:
        print("No channels with 'video_data' found in the bucket.")
    return channels_with_video_data