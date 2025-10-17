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
Se vedhæftede diagram for en illustration af en mulig relationel database-model til indfangelse af den underliggende datamodel, der ligger til grund for data i `MOCK_STREAMING_Q4_2023.json` og `RADIO_MOCK_FM.csv` (klik [her](https://www.figma.com/design/WoGem8spvpNwCWoVfGSf6B/koda-case-relational-db?node-id=0-1&t=paPps8LeHHCEsTlN-1) for interaktivt link):  

![Frame 1 (2)](https://github.com/user-attachments/assets/b9e3e122-baba-41d9-a194-49412acf917c)

<br>

`music_usage`-tabellen er central for dette databasedesign. Denne indeholder samme [granularitet](https://www.coursera.org/articles/data-granularity) som de enkelte datapunkter i `rapportering.udsendelser.udsendelse.udsendelse_indslag.indslag` fra `MOCK_STREAMING_Q4_2023.json` samt hver enkelt række i `RADIO_MOCK_FM.csv`. Således haves komplet historik over forbrug af ophavsretsligt beskyttede aktiver. 

<br>

`broadcast_history` indeholder historiske data for udsendelserne. `broadcast_history` indeholder tidssensitive data fra `MOCK_STREAMING_Q4_2023.json` fra felterne `rapportering.udsendelser.udsendelse`. `broadcast_history` indeholder primært data fra `MOCK_STREAMING_Q4_2023.json` fra felterne `rapportering.udsendelser.udsendelse`.
- I tilfælde af streaming kan kolonnen `broadcast_history.channel_name` indtage værdier som `"spotify"`, `"youtube"`, etc.

<br>

`program_info` indeholder metadata for de enkelte udsendelser. Disse indfanger statiske data fra `MOCK_STREAMING_Q4_2023.json` fra felterne `rapportering.udsendelser.udsendelse`. Datapunker i `RADIO_MOCK_FM.csv` vil ikke have et link til `program_info`-tabellen.

<br>

`track_info` indeholder metadata for ophavsretsligt beskyttede aktiver. Tabellen linker til `music_usage` og viser hvilken musik blev udsendt.
Denne tabel indfanger data fra `RADIO_MOCK_FM.csv` samt fra `rapportering.udsendelser.udsendelse.udsendelse_indslag.indsalg` fra `MOCK_STREAMING_Q4_2023.json`.

<br>

`copyright_holders_track_bridge` modellerer forholdet mellem musik og rettighedshavere. Der er tale om et _many-to-many_-forhold, da hvert musikstykke kan have flere rettighedshavere og hver rettighedshaver kan eje flere musikstykker. `copyright_holders_track_bridge` sikrer integritet i database-strukturen, da et givent musikstykke kan have duplikerede rækker i `copyright_holders_track_bridge`. For et givent musikstykke er der i `bridge`-tabellen kun en unik rettighedshaver registreret.

<br>

`copyright_holders` indeholder data om rettighedshaverne. Tabellen linker til `track_info` tabellen, og viser hvilken ejer har rettighederne til givne ophavsretsligt beskyttede værker.


