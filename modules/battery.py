import psutil


def get_battery_status():

    try:

        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery information is not available."

        percent = int(battery.percent)

        if battery.power_plugged:
            status = "plugged in and charging"
        else:
            status = "running on battery"

        return (
            f"Your battery is at {percent} percent "
            f"and the laptop is {status}."
        )

    except Exception as e:

        print("Battery Error:", e)

        return "Sorry, I couldn't get the battery status."