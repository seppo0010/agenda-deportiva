import requests
import os
import shutil
import html
from datetime import timedelta
import dateutil.parser
from ics import Calendar, Event

OUT_DIR = os.environ.get('OUT_DIR', './out')
IN_URL = os.environ.get('IN_URL', 'https://www.ole.com.ar/wg-agenda-deportiva/json/agenda.json')

req = requests.get(IN_URL)
agenda = req.json()
torneos = {}
for fecha in agenda['fechas']:
    for torneo in fecha['torneos']:
        nombre = torneo['nombre'].replace('/', '-')
        if nombre not in torneos:
            torneos[nombre] = Calendar()
        c = torneos[nombre]
        for evento in torneo['eventos']:
            c.events.add(Event(
                name=nombre,
                begin=evento['fecha'] + '-03:00',
                description='\n'.join(map(lambda canal: canal['nombre'], evento['canales'])),
                duration=timedelta(hours=2),
            ))

shutil.rmtree(OUT_DIR, ignore_errors=True)
os.mkdir(OUT_DIR)

for torneo, c in torneos.items():
    with open(f'{OUT_DIR}/{torneo}.ics', 'w') as f:
        f.writelines(c.serialize_iter())

with open(f'{OUT_DIR}/index.html', 'w') as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html lang="es">\n')
    f.write('<head><title>Agenda Deportiva</title></head>\n')
    f.write('<body>\n')
    f.write('<table>\n')
    for torneo, cal in torneos.items():
        f.write('<tr>\n')
        f.write(f'<th colspan="3"><a href="{html.escape(torneo)}.ics" target="_blank">{html.escape(torneo)}</a></th>\n')
        f.write('</tr>\n')
        for ev in sorted(cal.events, key=lambda ev: str(ev.begin)):
            f.write('<tr>\n')
            f.write(f'<td>{ev.name}</td>\n')
            f.write(f'<td>{dateutil.parser.isoparse(str(ev.begin)).strftime("%d/%m/%y %H:%M")}</td>\n')
            f.write(f'<td>{ev.description}</td>\n')
            f.write('</tr>\n')
    f.write('</table>\n')
    f.write('</body>\n')
    f.write('</html>\n')
