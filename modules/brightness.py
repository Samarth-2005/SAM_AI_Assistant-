import screen_brightness_control as sbc


def get_brightness():
    try:
        brightness = sbc.get_brightness()

        if isinstance(brightness, list):
            brightness = brightness[0]

        return int(brightness)

    except Exception as e:
        print("Brightness Error:", e)
        return None


def set_brightness(percent):
    try:
        percent = max(0, min(100, int(percent)))

        sbc.set_brightness(percent)

        return True

    except Exception as e:
        print("Brightness Error:", e)
        return False


def increase_brightness():
    current = get_brightness()

    if current is not None:
        set_brightness(current + 10)


def decrease_brightness():
    current = get_brightness()

    if current is not None:
        set_brightness(current - 10)