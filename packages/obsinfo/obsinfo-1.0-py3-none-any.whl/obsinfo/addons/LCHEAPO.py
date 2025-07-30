"""
Write extraction script for LCHEAPO instruments (proprietary to miniseed)
"""


def get_ref_code(inst):
    """
    Returns the LCHEAPO reference code corresponding to the instrumentation

    Arguments:
        inst (:class: ~obsinfo.Instrumentation)
    """
    sps = 50
    ch = inst.channels
    if len(ch) == 2:
        if  (ch[0].channel_code(sps) == 'SH3' and
             ch[1].channel_code(sps) == 'BDH'):
            return 'SPOBS1'
    elif len(ch) == 4:
        if  (ch[0].channel_code(sps) == 'BDH' and
             ch[1].channel_code(sps) == 'SH2' and
             ch[2].channel_code(sps) == 'SH1' and
             ch[3].channel_code(sps) == 'SH3'):
            return 'SPOBS2'
        elif (ch[0].channel_code(sps) == 'BH2' and
              ch[1].channel_code(sps) == 'BH1' and
              ch[2].channel_code(sps) == 'BHZ' and
              ch[3].channel_code(sps) in ['BDH', 'BDG']):
            return 'BBOBS1'
        elif (ch[0].channel_code(sps) == 'BDH' and
              ch[1].channel_code(sps) == 'BDH' and
              ch[2].channel_code(sps) == 'BDH' and
              ch[3].channel_code(sps) == 'BDH'):
            return 'HYDROCT1'
    return "UNKNOWN"
