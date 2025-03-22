
def get_creds() -> tuple:
    lines = []
    try:
        with open("update.dat") as file:
            lines = file.readlines()
    except Exception as error:
        print(error)
        pass

    user, passwrd = lines[0].strip().split(";")
    return (user, passwrd)
