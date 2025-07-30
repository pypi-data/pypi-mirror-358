def get_list_from_metadata(metadata: str):

    parts = metadata.split(';')

    # find the list part
    for part in parts:
        if 'list:' in part:
            metadata = part

    return metadata.split(':')[-1].strip().replace('"', '').replace('[', '').replace(']', '').split(',')