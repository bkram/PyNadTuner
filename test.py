from NadTuner import NadTuner

Tuner = NadTuner()


def guess_rds_ps_smash():
    ps = None
    ps2 = None
    count = 0
    pscount = 0
    ps2count = 0
    while count <= 16:
        bitjes = Tuner.__read_bytes__()
        print(count, bitjes[2], bitjes)
        if bitjes[2] == 83:
            if pscount <= 4:
                ps = bitjes[2:10]
                pscount += 1

        if bitjes[2] == 84:
            ps2 = bitjes[2:10]
            if ps2count <= 4:
                ps2 = bitjes[2:10]
                ps2count += 1

        if ps2count == 4 and pscount == 4:
            break

        count += 1

    if ps:
        text = ps.decode('utf-8', errors='ignore')
    if ps2:
        text += ' ' + ps2.decode('utf-8', errors='ignore')
    print(ps, ps2)
    # return " ".join((ps.decode('utf-8', errors='ignore'),

    #  ps2.decode('utf-8', errors='ignore')))
    # return text


# print(guess_rds_ps_smash())


def sample_rds():
    ps = None

    response = Tuner.__read_bytes__()
    if response[1] == 27:
        # print(count, response[1], response)
        ps = response[2:10].decode('utf-8', errors='ignore')

    return ps


print(sample_rds())
