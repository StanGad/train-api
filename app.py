from flask import Flask, jsonify, Response
import requests
import dateutil.parser
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

def get_horaires():
    url = "https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring"
    params = {
        "MonitoringRef": "STIF:StopArea:SP:63244:",
        "LineRef": "STIF:Line::C01743:"
    }
    headers = {
        "accept": "application/json",
        "apiKey": "AmqPoHD01WFdNOnQtkW24tTjz36LKWzX"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    visits = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
    resultats = []
    for visit in visits:
        journey = visit["MonitoredVehicleJourney"]
        call = journey["MonitoredCall"]
        heure_arrivee = call.get("ExpectedArrivalTime")
        destination = journey["DestinationName"][0]["value"]
        quai = call.get("DeparturePlatformName", {}).get("value", "")
        if heure_arrivee:
            dt = dateutil.parser.isoparse(heure_arrivee)
            dt_paris = dt.astimezone(ZoneInfo("Europe/Paris"))  # conversion ici
            heure_locale = dt_paris.strftime("%H:%M")
            resultats.append({
                "heure": heure_locale,
                "destination": destination,
                "quai": quai
            })
    resultats.sort(key=lambda r: r["heure"])
    print(resultats)
    return resultats

@app.route("/horaires.json")
def horaires_json():
    return jsonify(get_horaires())

@app.route("/horaires.xml")
def horaires_xml():
    horaires = get_horaires()
    xml = '<?xml version="1.0" encoding="UTF-8"?><horaires>'
    for r in horaires:
        xml += f'<passage><heure>{r["heure"]}</heure><destination>{r["destination"]}</destination><quai>{r["quai"]}</quai></passage>'
    xml += '</horaires>'
    return Response(xml, mimetype='application/xml')

@app.route("/horaires.rss")
def horaires_rss():
    horaires = get_horaires()
    items = ""
    for r in horaires:
        items += f"""
        <item>
            <title>Train vers {r['destination']} à {r['heure']} quai {r['quai']}</title>
            <description>Départ à {r['heure']} quai {r['quai']}</description>
            <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        </item>
        """
    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
        <title>Prochains trains</title>
        <link>http://localhost/horaires</link>
        <description>Horaires des prochains trains</description>
        {items}
    </channel>
    </rss>
    """
    return Response(rss, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
