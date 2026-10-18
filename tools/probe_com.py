import sys, json, os
out = {
    "python": sys.version,
    "exe": sys.executable,
}
try:
    import comtypes
    out["comtypes"] = getattr(comtypes, "__version__", "?")
except Exception as e:
    out["comtypes"] = "ERR: %r" % (e,)

# проверим доступность COM-интерфейсов
try:
    from comtypes import client
    out["client"] = "ok"
except Exception as e:
    out["client"] = "ERR: %r" % (e,)

# SHDocVw / Shell32 модули (генерация)
try:
    m = client.GetModule("shdocvw.dll")
    out["shdocvw"] = "ok"
except Exception as e:
    out["shdocvw"] = "ERR: %r" % (e,)

try:
    m2 = client.GetModule("shell32.dll")
    out["shell32"] = "ok"
except Exception as e:
    out["shell32"] = "ERR: %r" % (e,)

# Windows версия
try:
    import platform
    out["win"] = platform.platform()
    out["win_ver"] = platform.version()
except Exception as e:
    out["win"] = "ERR: %r" % (e,)

print(json.dumps(out, ensure_ascii=False, indent=2))
