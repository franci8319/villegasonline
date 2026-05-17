import requests
import re
import json
from datetime import datetime, timezone

FOTMOB = {
    'primera division':          87,
    'primera división':          87,
    'laliga':                    87,
    'premier league':            47,
    'champions league':          42,
    'uefa champions league':     42,
    'europa league':             73,
    'uefa europa league':        73,
    'conference league':         155,
    'bundesliga':                54,
    'serie a':                   55,
    'ligue 1':                   53,
    'copa del rey':              138,
    'fa cup':                    132,
    'primera liga':              94,
    'primeira liga':             94,
    'eredivisie':                88,
    'liga mx':                   262,
    'copa america':              77,
    'copa américa':              77,
}

def get_estado(status_id):
    sid = int(status_id) if str(status_id).isdigit() else 0
    if sid == 0:     return 'proximo'
    if 1 <= sid <= 5: return 'live'
    return 'finalizado'

def fetch_html():
    # Jina AI Reader — accede como navegador real, bypasa el bloqueo 406
    r = requests.get(
        'https://r.jina.ai/https://es.besoccer.com/',
        headers={
            'Accept':          'application/json',
            'X-Return-Format': 'html',
            'Authorization':   'Bearer jina_free',
        },
        timeout=60,
    )
    print(f'Jina status: {r.status_code} — bytes: {len(r.content)}')

    if r.status_code == 200:
        try:
            data = r.json()
            html = data.get('data', {}).get('content', '') or data.get('data', {}).get('html', '')
            if html:
                print('HTML obtenido via JSON de Jina')
                return html
        except Exception:
            pass
        print('Usando respuesta directa de Jina')
        return r.text

    raise RuntimeError(f'Jina devolvió {r.status_code}')

def extract_matches(html):
    competiciones = []
    vistas = set()

    for m in re.finditer(r"popupAlertFav\(`([^`]+)`,\s*`([^`]+)`,\s*\[", html):
        nombre_comp = m.group(1).strip()
        if nombre_comp in vistas:
            continue
        vistas.add(nombre_comp)

        inicio = m.end() - 1
        depth, i = 0, inicio
        while i < len(html):
            if html[i] == '[':   depth += 1
            elif html[i] == ']':
                depth -= 1
                if depth == 0: break
            i += 1

        try:
            raw = json.loads(html[inicio:i + 1])
        except json.JSONDecodeError as e:
            print(f'  JSON error en {nombre_comp}: {e}')
            continue

        partidos = []
        for p in raw:
            lid = str(p.get('lid', ''))
            vid = str(p.get('vid', ''))
            sid = str(p.get('statusId', '0'))
            resultado = p.get('r', '')

            goles_l = goles_v = None
            if resultado and resultado != '-1':
                partes = resultado.replace(' ', '').split('-')
                if len(partes) == 2:
                    try:
                        goles_l = int(partes[0])
                        goles_v = int(partes[1])
                    except ValueError:
                        pass

            partidos.append({
                'local':          p.get('l', ''),
                'visitante':      p.get('v', ''),
                'logoLocal':      f'https://cdn.resfu.com/img_data/equipos/{lid}.png' if lid else '',
                'logoVisitante':  f'https://cdn.resfu.com/img_data/equipos/{vid}.png' if vid else '',
                'hora':           p.get('ld', ''),
                'utc':            p.get('utc', ''),
                'golesLocal':     goles_l,
                'golesVisitante': goles_v,
                'statusId':       int(sid) if sid.isdigit() else 0,
                'estado':         get_estado(sid),
                'minuto':         str(p.get('lmin', '')),
            })

        if partidos:
            competiciones.append({
                'nombre':   nombre_comp,
                'fotmobId': FOTMOB.get(nombre_comp.lower()),
                'partidos': partidos,
            })
            print(f'  {nombre_comp}: {len(partidos)} partidos')

    return competiciones

def main():
    print('Obteniendo BeSoccer via Jina AI...')
    html = fetch_html()
    print(f'popupAlertFav encontrados: {html.count("popupAlertFav")}')

    competiciones = extract_matches(html)

    if not competiciones:
        print('AVISO: sin competiciones. Primeras 500 chars:')
        print(html[:500])

    total = sum(len(c['partidos']) for c in competiciones)
    print(f'Total: {len(competiciones)} competiciones, {total} partidos')

    out = {
        'actualizado': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'competiciones': competiciones,
    }

    with open('futbol/partidos.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('partidos.json guardado.')

if __name__ == '__main__':
    main()
