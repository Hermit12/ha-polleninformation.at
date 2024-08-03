# Home Assistant Integration für Polleninformation.at

## Überblick
Die Polleninformation.at Integration für Home Assistant ermöglicht es Benutzern, Pollenbelastungen und Allergierisiken in Österreich zu überwachen. Sie stellt Sensordaten für verschiedene Pollenarten und eine Gesamtbewertung des Allergierisikos bereit.

## Installation & Konfiguration

Zum installieren wie folgt vorgehen:

1. Den Ordner *polleninformation_at* samt Inhalt im Ordner *custom_components* einfügen
2. In ha unter Einstellungen/Geräte und Integrationen die Integration *Polleninformation.at* suchen und hinzufügen

Die Integration wird über das UI von Home Assistant eingerichtet. Benutzer können Folgendes konfigurieren:

1. API-URL
   Die GPS Koordinaten müssen im link noch für den passenden Standort geändert werden. Hier ein Beispiel für Klagenfurt:

   https://www.polleninformation.at/index.php?eID=appinterface&pure_json=1&lang_code=de&lang_id=0&action=getFullContaminationData&type=gps&value[latitude]=46.628&value[longitude]=14.309&show_polls=23&country_id=1&personal_contamination=false&sensitivity=0&country=AT&sessionid=

2. Zu aktivierende Sensoren (Benutzer können aus einer Liste verfügbarer Sensortypen auswählen)

## Verfügbare Sensoren
Die Integration bietet Sensoren für verschiedene Pollenarten, darunter:

- Erle
- Pilzsporen
- Ragweed
- Beifuß
- Birke
- Hasel
- Zypressengewächse
- Esche
- Ölbaum
- Platane
- Gräser
- Roggen
- Nessel- und Glaskraut

Zusätzlich gibt es einen Gesamtsensor für das "Allergierisiko".

## Lovelace-Benutzeroberfläche
Die bereitgestellte YAML-Konfiguration erstellt eine benutzerdefinierte Lovelace-Karte zur Anzeige von Polleninformationen:

1. Es werden bedingte Karten verwendet, um nur aktive Pollenarten anzuzeigen (solche mit einem anderen Zustand als "keine").
2. Jede aktive Pollenart wird als Entität in einer eigenen Karte angezeigt.
3. Eine Gesamtanzeige für das Allergierisiko wird mit Werten von 0 bis 4 dargestellt.
4. Eine Markdown-Karte zeigt eine tägliche Pollennachricht an.

Hier ein Beispiel der Lovelace Karte:

```
type: vertical-stack
title: Polleninfo
cards:
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_erle_alnus
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_erle_alnus
          name: Erle
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_pilzsporen_alternaria
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_pilzsporen_alternaria
          name: Pilzsporen
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_ragweed_ambrosia
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_ragweed_ambrosia
          name: Ragweed
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_beifuss_artemisia
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_beifuss_artemisia
          name: Beifuß
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_birke_betula
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_birke_betula
          name: Birke
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_hasel_corylus
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_hasel_corylus
          name: Hasel
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_zypressengewachse_cupressaceae
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_zypressengewachse_cupressaceae
          name: Zypressengewächse
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_esche_fraxinus
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_esche_fraxinus
          name: Esche
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_olbaum_olea
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_olbaum_olea
          name: Ölbaum
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_platane_platanus
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_platane_platanus
          name: Plantane
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_graser_poaceae
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_graser_poaceae
          name: Gräser
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_roggen_secale
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_roggen_secale
          name: Roggen
  - type: conditional
    conditions:
      - condition: state
        entity: sensor.pollen_nessel_und_glaskraut_urticaceae
        state_not: keine
    card:
      type: entities
      entities:
        - entity: sensor.pollen_nessel_und_glaskraut_urticaceae
          name: Nessel- und Glaskraut
  - type: gauge
    entity: sensor.allergierisiko
    max: 4
    name: Allergierisiko Wien
    needle: false
    min: 0
    severity:
      green: 0
      yellow: 3
      red: 4
  - type: markdown
    content: |

      {{ state_attr('sensor.tagliche_pollennachricht', 'message') }}
```

