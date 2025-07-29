import configparser

def get_mode_serius():
    config = configparser.ConfigParser()
    config.read('.kalkulator_ngaco.cfg')
    return config.get('mode', 'serius', fallback='off').lower() == 'on'
