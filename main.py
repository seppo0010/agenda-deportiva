import requests
import os
import shutil
import html
from ics import Calendar, Event

OUT_DIR = os.environ.get('OUT_DIR', './out')
IN_URL = os.environ.get('IN_URL', 'https://www.ole.com.ar/wg-agenda-deportiva/json/agenda.json')

req = requests.get(IN_URL)
agenda = req.json()
torneos = {}
for fecha in agenda['fechas']:
    for torneo in fecha['torneos']:
        if torneo['nombre'] not in torneos:
            torneos[torneo['nombre']] = Calendar()
        c = torneos[torneo['nombre']]
        for evento in torneo['eventos']:
            c.events.add(Event(name=evento['nombre'], begin=evento['fecha']))

shutil.rmtree(OUT_DIR, ignore_errors=True)
os.mkdir(OUT_DIR)

for torneo, c in torneos.items():
    with open(f'{OUT_DIR}/{torneo}.ics', 'w') as f:
        f.writelines(c.serialize_iter())

with open(f'{OUT_DIR}/index.html', 'w') as f:
    f.write('<ul>\n')
    for torneo in torneos.keys():
        f.write(f'<li><a href="{html.escape(torneo)}.ics" target="_blank">{html.escape(torneo)}</a></li>\n')
    f.write('</ul>\n')
