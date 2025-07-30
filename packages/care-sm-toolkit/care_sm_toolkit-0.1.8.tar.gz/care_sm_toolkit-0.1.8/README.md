# CARE-SM Toolkit

## CSV datatable toolkit for CARE semantic model implementation

The implementation of the Clinical And Registry Entries (CARE) Semantic Model for CSV data entails a meticulous and technically advanced workflow. By leveraging the power of the CARE-SM, YARRRML templates and incorporating the critical curation step executed by the CARE-SM toolkit, this implementation achieves robustness, accuracy, and reliability in generating RDF-based CDE-oriented patient data.

The toolkit serves as a module dedicated to performing a curation step prior to the conversion of data into RDF. The primary transformations carried out by the toolkit include:

* Quality control for column names.

* Adding every domain specific ontological term required to define every instances of the model, these terms are specific for every data element.

* Splitting the column labeled as `value` into distinct datatypes. This enables YARRRML to interpret each datatype differently, facilitating the subsequent processing.

* Conducting a quality control among `age`/`date`, `startdate` and `enddate` columns to ensure data consistency and validity.

* Eliminating any row that lacks the minimal required data to minimize the generation of incomplete RDF transformations.

* Creation of the column called `uniqid` that assigns a unique identifier to each observation. This prevents the RDF instances from overlapping with one another, ensuring their distinctiveness and integrity.

## Requirements 

- In order to use CARE-SM Toolkit functionality:
* All CSV files **MUST** be named according the data tags described at the CARE-SM glossary, documented at [CARE-SM implementation](https://github.com/CARE-SM/CARE-SM-Implementation/blob/main/CSV/README.md) E.g.: `Diagnosis.csv`, `Birthdate.csv`

 * All your CSV data content **MUST** be compatible with the CARE-SM glossary, documented at [CARE-SM implementation](https://github.com/CARE-SM/CARE-SM-Implementation/blob/main/CSV/README.md)


## Dockerized implementation

There's a Docker-based implementation controlled via API (using FastAPI) that you can use for mounting this data transformation step as a part of your CARE-SM implementation.

You can edit the [docker-compose.yaml](docker-compose.yaml) to control the volume folder in order to pass your CSV-based patient data:

```
    volumes:
      - ./location/of/your/data:/code/data
```

**Note** IP and Port can be customized in the docker compose as well.

Run [docker compose](https://docs.docker.com/compose/) to start the containers:

``` 
 docker compose up -d
```

Once its running, you can use in your browser the OpenAPI documentation at http://localhost:8080/docs so inspect all the possible requests and trigger the execution

Alternatively, you trigger the data transformation in the terminal by the following:

```
curl -X POST http://localhost:8080/toolkit
```
 
**Congrats!** You will find your transformed data, stored as `CARE.csv` at the folder you defined as volume below.

To stop and remove the implementation, do the following:

```
docker compose down
```

## Local implementation

If you are not interested in running our Docker image, you can install the Python module for local implementation.

###  Installation
 
Python 3.5 or later is needed. The script depends on standard libraries, plus the ones declared in [requirements.txt](requirements.txt).
 
In order to install the dependencies you need `pip` and `venv` Python modules.
	- `pip` is available in many Linux distributions (Ubuntu package `python-pip`, CentOS EPEL package `python-pip`), and also as [pip](https://pip.pypa.io/en/stable/) Python package.
	- `venv` is also available in many Linux distributions (Ubuntu package `python3-venv`). In some of these distributions `venv` is integrated into the Python 3.5 (or later) installation.

The creation of a virtual environment and installation of the dependencies in that environment is done running:

```
python3 -m venv envCARESM
source envCARESM/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Remember to `deactivate` your Python environment after using it.

###  Execution

Then, change the folder path inside the [trial.py](trial.py) script. And run it:

```
python3 trial.py
```
