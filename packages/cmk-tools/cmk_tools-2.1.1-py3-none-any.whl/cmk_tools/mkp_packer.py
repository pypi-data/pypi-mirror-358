#!/usr/bin/env python3
# Template Author: NhanDD <hp.duongducnhan@gmail.com>

"""
Simple Packer and (later) unpacker for MKP Files
MKP is the Package format for Check_MK
"""
import os
import json
import tarfile


def pack_mkp(
    package_name: str,
    checks_file: str,
    lib_file: str,
    wato_file: str,
    base_path: str = os.getcwd()
):
    """
    Pack a MKP File from the given files
    - info
    - info.json
    - active_check 
    - check_invoker
    - wato
    -> version get from 'info' file
    """

    checks_file_path = os.path.join(base_path, 'check_invoker', checks_file)
    lib_file_path = os.path.join(base_path, 'active_check', lib_file)
    wato_file_path = os.path.join(base_path, 'wato', wato_file)

    with open('info', 'r') as f:
        info = f.read()
        info_dict = eval(info)
    if not isinstance(info_dict, dict):
        raise ValueError("Info File is invalid")
    
    # info_dict['files'] = {}

    with open('temp_info', 'w') as info_file:
        info_file.write(str(info_dict))
    
    with open('temp_info.json', 'w') as info_json_file:        
        info_json_file.write(json.dumps(info_dict, indent=4))
        
    filename = f"{package_name}-{info_dict.get('version', '1.0.0')}"
    if os.path.isfile(filename + '.mkp'):
        os.remove(filename + '.mkp')
    
    with tarfile.open(filename + '.mkp', "w:gz") as mkp_tar:
        with tarfile.open('checks.tar', 'w') as checks_tar:
            checks_tar.add(checks_file_path, arcname=f"{checks_file}")
            
        with tarfile.open('lib.tar', 'w') as lib_tar:
            lib_tar.add(lib_file_path, arcname=f"nagios/plugins/{lib_file}")
            
        with tarfile.open('web.tar', 'w') as web_tar:
            web_tar.add(wato_file_path, arcname=f"plugins/wato/{wato_file}")
        
        for tar_file in ['checks.tar', 'lib.tar', 'web.tar']:
            mkp_tar.add(tar_file, arcname=tar_file)
            os.remove(tar_file)

        # # Add check file to the 'checks' directory
        # mkp_tar.add(checks_file_path, arcname=f"{checks_file}")
        
        # # Add active check file to the 'agents/plugins' directory
        # mkp_tar.add(lib_file_path, arcname=f"agents/plugins/{lib_file}")
        
        # # Add WATO plugin file to the 'web/plugins/wato' directory
        # mkp_tar.add(wato_file_path, arcname=f"web/plugins/wato/{wato_file}")
        
        # Add info files
        mkp_tar.add('temp_info', arcname='info')
        mkp_tar.add('temp_info.json', arcname='info.json')
        
    os.remove('temp_info')
    os.remove('temp_info.json')


if __name__ == "__main__":
    pack_mkp()