def mac_str_to_int(mac):
    vals = "".join(mac.split(':'))
    return int(vals, 16)


def mac_int_to_str(mac_int):
    s = str(hex(mac_int))[2:].zfill(12)
    return ":".join([a + b for a, b in zip(s[0::2], s[1::2])])
