import micropython_ota

OTA_HOST = "http://192.168.1.2:8000"
OTA_PROJECT = "esp-temp-and-pressure"
OTA_FILES = ['boot.py', 'ota_update.py', 'main.py']

def get_ota_creds() -> tuple:
    """
    Retrieves the OTA credentials from the 'update.dat' file.

    Returns:
        A tuple containing the OTA credentials (username, password).
    """
    try:
        with open("update.dat", encoding="utf-8") as file:
            line = file.readline().strip()
            if ";" in line:
                return tuple(line.split(";", 1))
    except Exception as error:
        print(f"[OTA CREDENTIALS ERROR] {error}")
    return ("", "")


def ota_update():
    """
    Perform over-the-air (OTA) update for the device.

    This function connects to the OTA server and updates the device firmware
    using the specified host, project, filenames, user, and password.

    Parameters:
        None

    Returns:
        None
    """
    user, passwrd = get_ota_creds()

    if not user or not passwrd:
        print("[OTA] Missing credentials. Skipping OTA check.")
        return

    micropython_ota.ota_update(
        host=OTA_HOST,
        project=OTA_PROJECT,
        filenames=OTA_FILES,
        user=user,
        passwd=passwrd,
        use_version_prefix=False)

def check_ota():
    """
    Check for OTA updates.

    This function checks for Over-The-Air (OTA) updates by retrieving the OTA credentials and
    calling the `check_for_ota_update` function from the `micropython_ota` module.

    If the OTA credentials are missing, the function prints a message and skips the OTA check.

    Parameters:
        None

    Returns:
        None
    """
    user, passwrd = get_ota_creds()

    if not user or not passwrd:
        print("[OTA] Missing credentials. Skipping OTA check.")
        return

    micropython_ota.check_for_ota_update(
        host=OTA_HOST,
        project=OTA_PROJECT,
        user=user,
        passwd=passwrd
    )
