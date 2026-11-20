import importlib.util,os,pickle
spec=importlib.util.spec_from_file_location('iot_','/'.join([os.path.dirname(os.path.abspath(__file__)),'io.py'])); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
_t=None
def toc():
    global _t
    if _t is None: _t=m.Toc(os.path.expanduser("~/mnt/game/FFRS/Content/Paks/FFRS-Windows"))
    return _t
