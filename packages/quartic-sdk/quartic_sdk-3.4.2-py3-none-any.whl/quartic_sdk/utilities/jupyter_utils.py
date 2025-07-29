import ipynbname

def get_ipynb_name():
    try:
        return str(ipynbname._find_nb_path()[1])
    except Exception as e:
        return ipynbname.name() + '.ipynb'
