# -*- coding: utf-8 -*-
r"""
Created on Wed Jul 18 11:08:24 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
from datetime import datetime, timezone
from fnmatch import fnmatch as fnm
from itertools import chain
import os
from pathlib import Path
import platform

import numpy as np

from pyfuppes.txt2dict import txt_2_dict_simple


# helper functions ############################################################


def to_list_of_Path(folders):
    """
    helper function to turn input string or list of strings into a list of
    pathlib Path objects.
    """
    if not isinstance(folders, list):
        folders = [folders]
    return [Path(f) for f in folders]

#------------------------------------------------------------------------------

def insensitive_pattern(pattern):
    """
    return a case-insensitive pattern to use in glob.glob or path.glob
    https://stackoverflow.com/a/10886685/10197418
    """
    def either(c):
        return f'[{c.lower()}{c.upper()}]' if c.isalpha() else c
    return ''.join(map(either, pattern))

#------------------------------------------------------------------------------

def get_sel_files(folders, exts, insensitive=True):
    """
    return a generator object containing all files in "folders" having one of
    the extensions listed in "exts".
    keyword "insensitive" only has an effect on Linux platforms - on Windows,
    glob is always case-insensitive.
    """
    msg = "all inputs must be of type list."
    assert all((isinstance(i, list) for i in (folders, exts))), msg

    if insensitive and platform.system().lower() != 'windows':
        exts = [insensitive_pattern(e) for e in exts]

    sel_files = chain()
    for f in folders:
        for e in exts:
            sel_files = chain(sel_files, f.glob(f'*{e}'))

    return sel_files

#------------------------------------------------------------------------------

def V25logs_cleaned_dump(path):
    """
    helper function to dump a small txt file signaling that this folder of
    V25 logfiles has been cleaned.
    """
    with open(path/'V25Logs_cleaned.done', "w", encoding="UTF-8") as fobj:
        fobj.write("# files in this folder were cleaned.\n")


###############################################################################


def V25Logs_cleanup(folder: list, exts: list,
                    drop_info=True, check_info=True,
                    verbose=False):
    """
    delete empty files and remove incomplete lines from V25 logfiles.

    Parameters
    ----------
    folder : list
        where to clean.
    exts : list
        list with file extensions specifying the files to clean.
    drop_info : bool, optional
        drop a file saying "this folder was cleaned". The default is True.
    check_info : bool, optional
        check for drop_info file. The default is True.
    verbose : true, optional
        some print-outs to the console. The default is False.

    Returns
    -------
    None.

    """
    verboseprint = print if verbose else lambda *a, **k: None
    folder = to_list_of_Path(folder)

    if check_info:
        folder = [f for f in folder if not 'V25Logs_cleaned.done' in os.listdir(f)]

    if not isinstance(exts, list):
        exts = [exts]

    if folder:

        sel_files = list(sorted(get_sel_files(folder, exts)))

        for file in sel_files:
            with open(file, "r") as file_obj:
                data = file_obj.readlines()

            if len(data) <= 1: # empty file or header only
                verboseprint(f"*v25_logcleaner* deleted {os.path.basename(file)}")
                os.remove(file)
                continue

            if data[-1][-1] != "\n": # incomplete last line
                if len(data) <= 2: # file would be header only if incomplete line
                    verboseprint(f"*v25_logcleaner* deleted {os.path.basename(file)}")
                    os.remove(file)
                    continue
                with open(file, "w", encoding="UTF-8") as file_obj:
                    file_obj.writelines(data[0:-2])
                verboseprint(f"*v25_logcleaner* deleted last line in {os.path.basename(file)}")
        verboseprint("*v25_logcleaner* Done.")

        if drop_info:
            for f in folder:
                if not 'V25Logs_cleaned.done' in os.listdir(f):
                    V25logs_cleaned_dump(f)


###############################################################################


def Collect_V25Logs(folder, ext, delimiter="\t", colhdr_ix=0,
                    write_mergefile=False, verbose=False):
    """
    collect multiple logfiles of one type into one dictionary.

    Parameters
    ----------
    folder : str or pathlib.Path (or lists of that type)
        where to look for the files.
        can also be list with multiple folders..
    ext : str
        file extension.
    delimiter : str, optional
        delimiter. The default is "\t".
    colhdr_ix : int, optional
        line index where to find the column header. The default is 0.
    write_mergefile : bool, optional
        write all data to one file?. The default is False.
    verbose : bool, optional
        call some print statements. The default is False.

    Returns
    -------
    dict
        collected data.

    """
    verboseprint = print if verbose else lambda *a, **k: None
    folder = to_list_of_Path(folder)

    sel_files = list(sorted(get_sel_files(folder, [ext])))

    if sel_files:

        verboseprint(f"loading {sel_files[0].name}")

        data = txt_2_dict_simple(sel_files[0], sep=delimiter,
                                 colhdr_ix=colhdr_ix,
                                 to_float=False,
                                 ignore_repeated_sep=False,
                                 ignore_colhdr=False,
                                 preserve_empty=False)['data']

        keys = list(data.keys())

        if len(sel_files) > 1:
            for i in range(1, len(sel_files)):
                verboseprint(f"loading {os.path.basename(sel_files[i].name)}")
                tmp = txt_2_dict_simple(sel_files[i], sep=delimiter,
                                        colhdr_ix=0,
                                        to_float=False,
                                        ignore_repeated_sep=False,
                                        ignore_colhdr=False,
                                        preserve_empty=False)['data']
                if tmp is None:
                    continue # skip loop iteration if tmp dict is None

                keys_tmp = list(tmp.keys())

                if keys_tmp == keys: # check matching dict keys
                    for k in keys: # add data key-wise
                        data[k].extend(tmp[k])
                del tmp

        if write_mergefile: # optionally write merged data to file
            n_el = len(data[keys[0]])
            outfile = Path(os.path.dirname(folder[0]) + "/" +
                           os.path.basename(folder[0]) + "_merged" + "/" +
                           os.path.basename(folder[0]) + "_merged_." + ext)
            try: # check if directory exists
                os.stat(os.path.dirname(outfile))
            except OSError: # create if not
                os.mkdir(os.path.dirname(outfile))

            with open(outfile, "w", encoding="UTF-8") as fobj:
                fobj.write(delimiter.join(keys) + '\n')
                for i in range(n_el):
                    fobj.write(delimiter.join([data[k][i] for k in keys])+'\n')

        verboseprint("V25 logfiles import done.")

        return data
    return None # no files selected


###############################################################################


def Collect_OSC_Logs(folder,
                     min_len=6,
                     ix_t_start=0,
                     ix_n_osc=3,
                     ix_col_hdr=4,
                     del_hdr=' ',
                     del_dat='\t',
                     ts_fmt="%d.%m.%y %H:%M:%S.%f",
                     write_mergefile=False,
                     verbose=False):
    """
    collect multiple logfiles of the FAIRO Cl detector (OSCAR).

    Parameters
    ----------
    folder : str or pathlib.Path
        where to look for the files.
    min_len : int, optional
        minimum file lines. The default is 6.
    ix_t_start : int, optional
        line where to look for the starting time. The default is 0.
    ix_n_osc : int, optional
        line where to look for n osc parameter. The default is 3.
    ix_col_hdr : int, optional
        line where to look for the column header. The default is 4.
    del_hdr : str, optional
        delimiter inside the header of OSC files. The default is ' '.
    del_dat : str, optional
        delimiter inside the data part. The default is '\t'.
    ts_fmt : str, optional
        format of the starting time timestamp. The default is "%d.%m.%y %H:%M:%S.%f".
    write_mergefile : bool, optional
        write all data to one file?. The default is False.
    verbose : bool, optional
        call some print statements. The default is False.

    Returns
    -------
    dict
        collected Oscar data.

    """
    verboseprint = print if verbose else lambda *a, **k: None
    folder = to_list_of_Path(folder)
    sel_files = list(sorted(get_sel_files(folder, [".osc"])))

    if sel_files:

        verboseprint(f"loading {os.path.basename(sel_files[0])}")

        # read header
        with open(sel_files[0], "r") as file_obj:
            head = [next(file_obj) for x in range(min_len)]

        if len(head) == min_len:
            t_start = datetime.strptime((head[ix_t_start]).strip(), ts_fmt)
            t_start = t_start.replace(tzinfo=timezone.utc).timestamp()

            Set_HV = head[ix_n_osc-1].strip().split(del_hdr)[-1]
            N_Oscar = head[ix_n_osc].strip().split(del_hdr)[-1]

            # read rest of file
            osc_dat = txt_2_dict_simple(sel_files[0], sep=del_dat,
                                        colhdr_ix=ix_col_hdr, to_float=False,
                                        keys_upper=True,
                                        ignore_repeated_sep=False,
                                        ignore_colhdr=False,
                                        preserve_empty=False)['data']

            osc_dat['Set_HV'] = [Set_HV]
            osc_dat['N_Oscar'] = [N_Oscar]
            osc_dat['POSIX'] = [t_start+float(t) for t in osc_dat['TIME']]


            keys_data = list(osc_dat.keys())

        if len(sel_files) > 1:
            for file in sel_files[1:]:

                verboseprint(f"loading {os.path.basename(file)}")

                with open(file, "r") as file_obj:
                    head = [next(file_obj) for x in range(min_len)]

                if len(head) == min_len:
                    t_start = datetime.strptime((head[ix_t_start]).strip(), ts_fmt)
                    t_start = t_start.replace(tzinfo=timezone.utc).timestamp()

                    Set_HV = head[ix_n_osc-1].strip().split(del_hdr)[-1]
                    N_Oscar = head[ix_n_osc].strip().split(del_hdr)[-1]

                    tmp = txt_2_dict_simple(file, sep=del_dat,
                                            colhdr_ix=ix_col_hdr,
                                            to_float=False, keys_upper=True,
                                            ignore_repeated_sep=False,
                                            ignore_colhdr=False,
                                            preserve_empty=False)['data']

                    tmp['Set_HV'] = [Set_HV]
                    tmp['N_Oscar'] = [N_Oscar]
                    tmp['POSIX'] = [t_start+float(t) for t in tmp['TIME']]

                    keys_tmp = list(tmp.keys())

                    if keys_tmp == keys_data: # check matching dict keys
                        for key in keys_data: # add data key-wise
                            osc_dat[key].extend(tmp[key])


        if write_mergefile: # optionally write merged data to file
            keys_data = list(osc_dat.keys())
            keys_data.pop(keys_data.index('Set_HV'))
            keys_data.pop(keys_data.index('N_Oscar'))

            outfile = Path(os.path.dirname(folder[0]) + "/" +
                           os.path.basename(folder[0]) + "_merged" + "/" +
                           os.path.basename(folder[0]) + "_merged_.osc")

            try: # check if directory exists
                os.stat(os.path.dirname(outfile))
            except OSError: # create if not
                os.mkdir(os.path.dirname(outfile))

            with open(outfile, "w", encoding="UTF-8") as fobj: # write the merge file
                fobj.write(del_dat.join(keys_data) + '\n')
                for i, _ in enumerate(osc_dat['POSIX']):
                    fobj.write(del_dat.join([osc_dat[k][i] for k in keys_data]) + '\n')

        verboseprint("OSC logfiles import done.")

        return osc_dat

    return None # no files selected


###############################################################################


def parseHALOtime(cfgEVAL, data_in_ac):
    """
    parse IWG1 string from aircraft, as recorded by V25

    Parameters
    ----------
    cfgEVAL : dict
        pyfairoproc config dict.
    data_in_ac : dict
        data loaded from txt log files.

    Returns
    -------
    t_REF : np.ndarray
        aircraft time, reference.
    t_V25 : np.ndarray
        corresponding V25 time.

    """
    t_REF, t_V25 = None, None
    keys_t_ref_data = list(data_in_ac.keys())
    if not keys_t_ref_data:
        cfgEVAL['use_t_ref'] = False
    else:
        for ix, key in enumerate(keys_t_ref_data):
            if fnm(key.lower(), "v25*time"):
                t_V25 = data_in_ac[keys_t_ref_data[ix]]
            if True in [fnm(key.lower(), "master*time"),
                        fnm(key.lower(), "halo*time"),
                        fnm(key.lower(), "king*time")]:
                t_REF = data_in_ac[keys_t_ref_data[ix]]

        # check for invalid date in iwg1 string
        if cfgEVAL["platform"].upper() in ["HALO", "BBFLUX"]:
            for ix, element in enumerate(t_REF):
                dmy_ref = list(map(int, element[:8].split('.')))
                fails = (dmy_ref[0] > 31, dmy_ref[1] > 12,
                         dmy_ref[2] != int(str(cfgEVAL['exp_date_UTC'][0])[2:]))
                if any(fails):
                    dmy = t_V25[ix][:8] # replace invalid dates with V25 date
                    t_REF[ix] = ' '.join([dmy, element.split(' ')[-1]])
            del dmy_ref

        t_REF = [datetime.strptime(element, cfgEVAL['ts_fmt']) for element in t_REF]
        t_REF = np.array([d.replace(tzinfo=timezone.utc).timestamp() for d in t_REF])

        t_V25 = [datetime.strptime(element, cfgEVAL['ts_fmt']) for element in t_V25]
        t_V25 = np.array([d.replace(tzinfo=timezone.utc).timestamp() for d in t_V25])

    return t_REF, t_V25


###############################################################################


def V25Logs_append_simple(folder, ext, delimiter="\t", colhdr_ix=0,
                          write_mergefile=False, verbose=False):
    # Collect_irregular
    return None
    

###############################################################################

