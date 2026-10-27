from pycaw.pycaw import AudioUtilities


def get_volume_interface():

    devices = AudioUtilities.GetSpeakers()

    volume = devices.EndpointVolume

    return volume


def get_volume():

    volume = get_volume_interface()

    current = volume.GetMasterVolumeLevelScalar()

    return int(current * 100)


def set_volume(percent):

    percent = max(0, min(100, percent))

    volume = get_volume_interface()

    volume.SetMasterVolumeLevelScalar(
        percent / 100,
        None
    )


def increase_volume():

    current = get_volume()

    set_volume(current + 10)


def decrease_volume():

    current = get_volume()

    set_volume(current - 10)


def mute_volume():

    volume = get_volume_interface()

    volume.SetMute(1, None)


def unmute_volume():

    volume = get_volume_interface()

    volume.SetMute(0, None)