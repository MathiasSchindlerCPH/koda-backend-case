# Koda: Case til ansættelsesprocess i Backend-teamet
<img src="https://via.ritzau.dk/data/images/00304/29b9a8c9-94a5-4cf3-9032-77dafd899e98.png" alt="Koda Logo" width="200"/>

## Introduktion
Dette repository indeholder løsningen til Kodas backend-case i forbindelse med ansættelsessamtale som [backendudvikler](https://www.epos-asp.dk/REK/Koda/Joblist/Job.aspx?jobOfferInstanceId=178&joblistId=1&lang=da).  
Projektet tager udgangspunkt i to tilsendte datafiler:
- `MOCK_STREAMING_Q4_2023.json`
- `RADIO_MOCK_FM.csv`
Disse filer er *ikke* inkluderet i dette repository på GitHub og er udeladt via `.gitignore`. Udviklere forventes selv at tilføje filerne manuelt i stien `/data` (se afsnittet [Opsætning](#opsætning)).

## Tekniske krav
Projektet kræver forudgående installation af følgende:
- [`python`](https://www.python.org/downloads/)
- [`pip`](https://pypi.org/project/pip/)
- [`git`](https://git-scm.com/downloads) *(valgfrit)* – til at klone projektet

Programmerne skal være installeret lokalt på maskinen og være tilgængelige i terminalen (dvs. ligge på systemets `PATH`).

## Opsætning
1. Klon repository
    ```bash
    git clone https://github.com/your-username/koda_case.git
    cd koda_case
    ```

2. Opret og aktiver virtuelt miljø
    ```bash
    python -m venv .venv
    source .venv/bin/activate       # Windows: .venv\Scripts\activate
    ```

3. Installér afhængigheder
    ```bash
    pip install -r requirements.txt
    ```

1. Tilføj datafiler i stien `/data`:
    ```bash
    .
    ├── data
    │   ├── MOCK_STREAMING_Q4_2023.json
    │   └── RADIO_MOCK_FM.csv
    ```

## Kør projektet
Efter opsætning (jf. afsnittet [Opsætning](#opsætning)), kan projektet eksekveres direkte fra terminalen:
```bash
python -m src.transform_json
python -m src.convert_csv
```
hvert program indlæser data som kopieret i stien `/data`.

## Datamodellering
Se vedhæftede diagram for en illustration af en mulig relationel database-model der indfanger den underliggende struktur i data fra `MOCK_STREAMING_Q4_2023.json` og `RADIO_MOCK_FM.csv` (klik [her](https://www.figma.com/design/WoGem8spvpNwCWoVfGSf6B/koda-case-relational-db?node-id=0-1&t=paPps8LeHHCEsTlN-1) for interaktivt link):  

![Frame 1 (2)](https://github.com/user-attachments/assets/b9e3e122-baba-41d9-a194-49412acf917c)

<br>

### Overblik
Datamodellen er bygget op omkring `music_usage`-tabellen, der repræsenterer den laveste [granularitet](https://www.coursera.org/articles/data-granularity) i de tilgængelige datasæt: Hvert enkelt brug af et ophavsretsligt beskyttet musikværk.  
Tabellen udgør forbindelsen mellem udsendelser (i `broadcast_history` og `program_info`) og de benyttede værker (`track_info`) med dertilhørende rettighedshaverne (`copyright_holders_track_bridge` og `copyright_holders`).

### Kernetable
#### `music_usage`
Denne tabel er central for designet og indeholder én række pr. enkelt registreret brug af et musikværk. Den afspejler strukturen `rapportering.udsendelser.udsendelse.udsendelse_indslag.indslag` i `MOCK_STREAMING_Q4_2023.json` samt hver række i R`RADIO_MOCK_FM.csv`.  
Tabellen gør det muligt at føre komplet historik over anvendelse af ophavsretsligt beskyttede værker på tværs af både radio-broadcast og streaming.


### Udsendelser
#### `broadcast_history`
Indeholder *tidsafhængige* data for udsendelser og streaming. Data stammer primært fra `rapportering.udsendelser.udsendelse` i JSON-filen.
- I tilfælde af streaming kan kolonnen `broadcast_history.channel_name` indtage værdier som `"spotify"`, `"youtube"`, etc.

#### `program_info`
Indeholder statiske metadata for de enkelte programmer eller serier, fx titel, producent, produktionsår og programkode.
Tabellen linker til `broadcast_history` via en fremmednøgle og dækker de samme datafelter som `rapportering.udsendelser.udsendelse` i `MOCK_STREAMING_Q4_2023.json`. Datapunker i `RADIO_MOCK_FM.csv` indeholder ikke statiske data over programmer og vil derfor ikke have et link til `program_info`-tabellen.


### Værker
#### `track_info`
Indeholder metadata for hvert enkelt musikværk, herunder titel, album, katalognummer, ISRC, ISWC og udgivelsesdato.
Tabellen dækker både værker fra CSV-filen og fra `rapportering.udsendelser.udsendelse.udsendelse_indslag.indsalg` i JSON-filen.
Tabellen linker til `music_usage` via en fremmednøgle, og viser hvilket musikværk der blev anvendt i hvilken udsendelse.


### Rettighedshavere
Der er tale om et _many-to-many_-forhold mellem rettighedshavere og musikværker, da hvert musikværk kan have flere rettighedshavere og hver rettighedshaver kan eje rettighederne til flere musikværker. Dette nødvendiggør et specielt design i den relationelle database:

#### `copyright_holders_track_bridge`
Brotabellen modellerer forholdet mellem værker og rettighedshavere og sikrer integritet i database-strukturen. Et givent musikværk kan have duplikerede rækker i `copyright_holders_track_bridge`. For et givent musikværk findes dog højest én række pr. rettighedshaver.  
Tabellen linker både til `track_info` og `copyright_holders` via fremmednøgler, og viser hvilket rettighedshavere ejer rettighederne til hvilke musikværker.

#### `copyright_holders`
Indeholder oplysninger om de individuelle rettighedshavere (fx komponister, producere, forlag m.m.).
Tabellen linker til `track_info` gennem `copyright_holders_track_bridge` og gør det muligt at se, hvilke ejere der har rettighederne til et givent værk.
