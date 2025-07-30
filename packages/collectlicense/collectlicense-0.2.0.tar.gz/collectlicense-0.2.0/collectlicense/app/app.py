from collectlicense.app import common
from pathlib import Path
import json
import re
import shutil
import subprocess

def safe_fname(fname:str) -> str:
    """
    ファイル名に使えない文字を置換します。

    Args:
        fname (str): ファイル名

    Returns:
        str: 置換後のファイル名
    """
    #fname = re.sub('[_]', '-_-',str(fname))
    fname = re.sub('[\s:;\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]', '_',str(fname))
    fname = re.sub('[_]{2,}', '-', fname)
    return fname.strip('_').strip('-').strip()

def main(out_dir:Path, clear:bool):
    _, logger = common.load_config()
    if clear:
        shutil.rmtree(out_dir, ignore_errors=True)
    common.mkdirs(out_dir)
    proc = subprocess.run(common.CMD, capture_output=True, text=True)
    if proc.returncode != 0:
        logger.error(proc.stderr, stack_info=True)
        return
    output_str = proc.stdout
    license_json = json.loads(output_str)
    exclude_key = ('LicenseText','LicenseFile')
    maxfnsize = 128
    with open(out_dir / f"files.txt", "w", encoding="utf-8") as lf:
        for i, license_info in enumerate(license_json):
            ln = license_info['License'].translate(str.maketrans({'\\':'','/':'',':':'','*':'','?':'','"':'','<':'','>':'','|':''}))
            fn = safe_fname(f"LICENSE.{license_info['Name']}.{license_info['Version']}({ln})") + '.txt'
            if len(fn) > maxfnsize:
                fn = fn[:maxfnsize] + '.txt'
            output_file = out_dir / fn
            license_info['File'] = str(output_file)
            cols = [key for key in license_info if key not in exclude_key]
            if i==0:
                lf.write('\t'.join(cols)+'\n')
            with open(output_file, "w", encoding="UTF-8") as f:
                f.write(license_info['LicenseText'])
            lf.write('\t'.join([license_info[col] for col in cols if col not in exclude_key])+'\n')

