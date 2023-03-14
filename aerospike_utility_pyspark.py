__all__ = ['update_ttl', 'update_bin', 'replace_bin', 'remove_from_bin']

import aerospike
import json

with open('./aerospike_utility_config.json') as config_json:
    config = json.load(config_json)

_region = config['region']
_host_port = config['aerospike'][_region]['hosts_ports']
_timeout = config['aerospike'][_region]['timeout']
_ttl = config['aerospike'][_region]['ttl']
_ns = config['aerospike'][_region]['namespace']
_set = config['aerospike'][_region]['set']
_aero_config = {
    "hosts": _host_port,
    "policies": {"timeout": _timeout}
}
_client = aerospike.client(_aero_config)
_client.connect()

def _get_record(key):
    _, metadata, record = _client.get(key)
    return metadata, record

def _get_record_or_create_new(key):
    try:
        metadata, record = _get_record(key)
        if 'ttl' not in metadata:
            metadata['ttl'] = _ttl
    except aerospike.exception.RecordNotFound:
        record = {'key': key[2]}
        metadata = {'ttl': _ttl}
    return record, metadata 

def _put_record(key, record, metadata):
    try:
        _client.put(key, record, meta=metadata)
        return True
    except Exception:
        return False  

def _update_record_ttl(key, ttl):
    try:
        _client.touch(key=key, val=ttl)
        return True
    except Exception:
        return False

def _update_list(old_data, new_data):
    for i in new_data:
        if i not in old_data:
            old_data.append(i)
    return old_data

def _update_dict(old_data, new_data):
    old_data.update(new_data)
    return old_data

def _remove_from_list(old_data, new_data):
    for i in new_data:
        if i in old_data:
            old_data.remove(i)
    return old_data

def _replace_list(old_data, new_data):
    old_data.clear()
    old_data.extend(new_data)
    return old_data

def _replace_dict(old_data, new_data):
    old_data.clear()
    old_data.update(new_data)
    return old_data

def _validate_bin_type(bin_data):
    if not (isinstance(bin_data, list) or isinstance(bin_data, dict)):
        raise TypeError('only list or dict is supported for input data')

def _preprocess_bin(record, bin, dtype):
    if bin not in record:   
        record.setdefault(bin, dtype())
    else:
        if not isinstance(record[bin], dtype):
            record[bin] = _convert_bin(record[bin], dtype)
    return record

def _convert_bin(bin_data, dtype):
    if dtype == list:
        converted_data = list(bin_data.keys())
    elif dtype == dict:
        converted_data = {i: [0, 0] for i in bin_data}
    return converted_data

def _transform_bin(mode, old_data, new_data):
    if mode == 'update':
        if isinstance(old_data, list):
            return _update_list(old_data, new_data)
        else:
            return _update_dict(old_data, new_data)
    elif mode == 'replace':
        if isinstance(old_data, list):
            return _replace_list(old_data, new_data)
        else:
            return _replace_dict(old_data, new_data)
    elif mode == 'delete':
        if isinstance(old_data, list):
            return _remove_from_list(old_data, new_data)
        else:
            return _remove_from_dict(old_data, new_data)

def _update_bin(df, key_column, transform_row_func, bin, mode): 
    def map_partitions_update_list_bin(iterable):
        for item in iterable:
            new_bin_data, new_ttl = transform_row_func(item)
            _validate_bin_type(new_bin_data)
            key = (_ns, _set, getattr(item, key_column))
            record, metadata = _get_record_or_create_new(key)
            record = _preprocess_bin(record, bin, type(new_bin_data))
            record[bin] = _transform_bin(mode, record[bin], new_bin_data)
            if new_ttl:
                metadata['ttl'] = max(metadata['ttl'], new_ttl)
            else:
                metadata['ttl'] = max(metadata['ttl'], _ttl)
            result = _put_record(key, record, metadata)
            yield result

    status = df.rdd.mapPartitions(map_partitions_update_list_bin).collect()
    return status

def _validate_column(df, column):
    if column not in df.columns:
        raise ValueError(f'column {column} does not exist in dataframe')

def update_bin(df, key_column, transform_row_func, bin):
    """
    update specified bin in aerospike, with segment data passed from a pyspark dataframe.
    If a segment already exists in original bin, update its value. otherwise add it to the bin.
    If data in the original bin has different type from the input data, the function will convert original bin to input data's type.
    search user_id first, if cannot be found, create new record.
    if original record has longer ttl, keep it. otherwise update with new ttl.
    
    Input
    df: pyspark dataframe. should contain:
        a colume that contains the key for aerospike. could be device id, 3rd party id, UAIP, etc.
        a column that contains segment info and/or ttl info.
    key_column: the name of the dataframe column that contains aerospike key.
    transform_row_func: a function that tranforms row items to data that will be passed in aerospike.
        function's input argument is pyspark row. columns in the row object should corresponds to the columns in dataframe.
        function outputs bin_data (type be dict or list) and ttl (int).
        if no need to update ttl, return None for ttl.

    Output
    A list of booleans indicating successful or failed aerospike operations.
    """
    _validate_column(df, key_column)
    return _update_bin(df, key_column, transform_row_func, bin, 'update')

def replace_bin(df, key_column, transform_row_func, bin):
    """
    update specified bin in aerospike, with segment data passed from a pyspark dataframe.
    Completely replace original bin with new data.
    If data in the original bin has different type from the input data, the function will convert original bin to input data's type.
    search user_id first, if cannot be found, create new record.
    if original record has longer ttl, keep it. otherwise update with new ttl.
    
    Input
    df: pyspark dataframe. should contain:
        a colume that contains the key for aerospike. could be device id, 3rd party id, UAIP, etc.
        a column that contains segment info and/or ttl info.
    key_column: the name of the dataframe column that contains aerospike key.
    transform_row_func: a function that tranforms row items to data that will be passed in aerospike.
        function's input argument is pyspark row. columns in the row object should corresponds to the columns in dataframe.
        function outputs bin_data (type be dict or list) and ttl (int).
        if no need to update ttl, return None for ttl.

    Output
    A list of booleans indicating successful or failed aerospike operations.
    """
    _validate_column(df, key_column)
    return _update_bin(df, key_column, transform_row_func, bin, 'replace')

def remove_from_bin(df, key_column, transform_row_func, bin):
    """
    Remove data from specified bin in aerospike, using segment data passed from a pyspark dataframe.
    If segment from input data exists in original bin, remove it. Otherwise ignore it.
    If data in the original bin has different type from the input data, the function will convert original bin to input data's type.
    search user_id first, if cannot be found, create new record.
    if original record has longer ttl, keep it. otherwise update with new ttl.
    
    Input
    df: pyspark dataframe. should contain:
        a colume that contains the key for aerospike. could be device id, 3rd party id, UAIP, etc.
        a column that contains segment info and/or ttl info.
    key_column: the name of the dataframe column that contains aerospike key.
    transform_row_func: a function that tranforms row items to data that will be passed in aerospike.
        function's input argument is pyspark row. columns in the row object should corresponds to the columns in dataframe.
        function outputs bin_data (type be dict or list) and ttl (int).
        if no need to update ttl, return None for ttl.

    Output
    A list of booleans indicating successful or failed aerospike operations.
    """
    _validate_column(df, key_column)
    return _update_bin(df, key_column, transform_row_func, bin, 'delete')

def update_ttl(df, key_column, transform_row_func):
    """
    update records' ttl in aerospike.
    if user_id doesn't exist, ignore it.
    no matter original record's ttl is longer or shorter, always overwrite with new ttl.
    """
    def map_partitions_update_ttl(iterable):
        for item in iterable:
            key = (_ns, _set, getattr(item, key_column))
            _, new_ttl = transform_row_func(item)
            if not new_ttl:
                new_ttl = _ttl
            
            yield _update_record_ttl(key, new_ttl)

    _validate_column(df, key_column)
    status = df.rdd.mapPartitions(map_partitions_update_ttl).collect()
    return status
