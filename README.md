# Koda: Case til ansættelsesprocess i Backend-teamet

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