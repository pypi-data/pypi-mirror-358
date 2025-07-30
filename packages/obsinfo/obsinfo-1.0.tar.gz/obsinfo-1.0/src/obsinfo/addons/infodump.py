"""Dump network/instrument info to standardized A-node file"""


def infodump(netinfo):
    """
    Args:
        netinfo (`obsinfo:Subetwork`): the network to dump

    Experiment > Campaign > Facility

    Dans la hiérarchie d'informations, le lien entre un "entity" enfant et un
    "entity" parent se fait au travers de la référence en utilisant la
    convention : "<child-key>@<parent-key>".

    Pour les liens avec des "entities" ne se trouvant pas dans la hiérarchie,
    je me suis inspiré des concepts de RDF (Resource Desciption Framework) :

    subject --predicate-> object

    Dans ce qui suit, on a :

    - sujet : une campagne (avec sa référence globalement unique)
    - objet : un réseau (identifié par sa référence unique)
    - prédicat : "est associé à" (forme verbale)

      "campaigns": [ {
          "_campaign-ref": "MOMAR_2007-2008_A@MOMAR",
          "name": "MOMAR_2007-2008_A",
          "is-associated-to": { "_network-ref": "4G+2007" },
    ...
        } ],

    - sujet : un parc OBS (avec sa référence globalement unique)
    - objet : des stations (identifiées par leur référence unique)
    - prédicat : "a opéré" (forme verbale)

      "facilities": [ {
          "_facility-ref": "INSU-IPGP@MOMAR_2007-2008_A@MOMAR",
          "name": "INSU-IPGP",
          "full-name": "INSU-IPGP OBS Park",
          "has-operated": { "_station-refs": [ "AZBBA@4G+2007",
                                               "LSV5A@4G+2007" ] }
        } ]
    """
    net_code = netinfo.network_code
    campaign_code = netinfo.campaign_ref
    facility_code = netinfo.operator.ref_name

    network_dict = dict(_network_ref=net_code,
                        fdsn_code=net_code,
                        name=netinfo.network_name,
                        operating_period=dict(start_date=netinfo.start_date,
                                              end_date=netinfo.end_date),
                        _campaign_ref=campaign_code)
    station_list = []
    for station in netinfo.stations:
        sta_code = station.code
        station_list.append(
            dict(_network_idx=0,
                 _station_ref=f'{sta_code}@{net_code}',
                 code=sta_code,
                 site_description=station.site,
                 aquisition_period=dict(start_datetime=station.start_time,
                                        end_datetime=station.end_time),
                 _facility_ref=f'{facility_code}@{campaign_code}'))
