import pandas as pd

def filter(df, filter=True):
    """Filters the DataFrame for jobs that have certain strings in their title columns.

    Args:
        df (DataFrame): The DataFrame to be filtered.
        filter (bool, optional): If the DataFrame should be filtered. Defaults to True.
    """
    def check_keyword(string):
        for word in ["data", "analy", "daten"]:
            if word in string.lower():
                return True
        return False

    if filter:
        return df.loc[lambda _df: _df["Titel"].apply(check_keyword), :]
    else:
        return df

def zeit_remote(df):
    verfügbar = ~df["Teilzeit_Remote"].isin(
        ["Stellenanzeige nicht mehr verfügbar", "-", "Nicht stepstone"]
    )

    return df.assign(
        Vollzeit=lambda _df: _df.loc[verfügbar, "Teilzeit_Remote"].apply(
            lambda x: "Vollzeit" in x
        ),
        Teilzeit=lambda _df: _df.loc[verfügbar, "Teilzeit_Remote"].apply(
            lambda x: "Teilzeit" in x
        ),
        **{"Zeit flexibel": lambda _df: _df["Vollzeit"] & _df["Teilzeit"]},
        Remote=lambda _df: _df.loc[verfügbar, "Teilzeit_Remote"].apply(
            lambda x: "Home Office möglich" in x
        ),
    ).astype(
        {"Vollzeit": bool, "Teilzeit": bool, "Zeit flexibel": bool, "Remote": bool}
    )


def roles(df, categories_reduced=True):
    def role(title):
        data_science_roles = {
            "Praktikum/Student": ["praktik", "student", "studium"],
            "Trainee": ["trainee"],
            "Product Owner": ["product owner"],
            "Consultant": ["consult"],
            "Data Scientist": ["scien", "wissenschaft"],
            "Data Engineer": ["engineer"],
            "Data Analyst": ["analy"],
            "Data Architekt": ["archite"],
            "Data Warehouse": ["warehouse"],
            "Systemadministrator": ["systemadmin", "system admin"],
            "Datenbank": ["datenbank", "database"],
            "Data Protection": ["protection", "privacy", "datenschutz", "security"],
            "Management/Teamlead": [
                "manag",
                "teamlead",
                "team lead",
                "head of",
                "teamleit",
            ],
        }

        for role, keywords in data_science_roles.items():
            for word in keywords:
                if word in title.lower():
                    return role
        return "Andere"

    returned = df.assign(**{"Job Kategorie": lambda _df: _df["Titel"].apply(role)})

    if categories_reduced:
        return returned.loc[
            lambda _df: _df["Job Kategorie"].isin(["Data Analyst", "Data Scientist"]), :
        ].astype({"Job Kategorie": "category"})
    else:
        return returned.astype({"Job Kategorie": "category"})


def remote(df):
    def remote_entry(entry):
        for string in ["home office", "home-office", "homeoffice", "fernbedienung"]:
            if string in entry.lower():
                return True
        if entry.lower() == "bundesweit":
            return True
        else:
            return False

    jobs_non_remote = df[df["Remote"] != True]  # noqa: E712

    jobs_non_remote.loc[:, "Remote"] = jobs_non_remote["Ort"].apply(remote_entry)

    df.loc[jobs_non_remote.index, "Remote"] = jobs_non_remote["Remote"]

    return df

def clean(df):
    return (
        df.assign(
            Gehalt_min=lambda _df: pd.to_numeric(
                _df["Gehalt_min"], errors="coerce"
            ).astype("Int64"),
            Gehalt_max=lambda _df: pd.to_numeric(
                _df["Gehalt_max"], errors="coerce"
            ).astype("Int64"),
            JobID=lambda _df: _df["JobID"].astype("Int64"),
            Link=lambda _df: _df["Link"].str.rsplit("?&cid", n=1, expand=True)[0],
        )
        .drop_duplicates(subset=["Link"])
    )

def prep(df, filtered=True, categories_reduced=True):
    """Returns a cleaned DataFrame.
    - dtypes are set
    - Duplicate links removed
    - columns for remote/time, junior role and yearly salary columns created

    Args:
        df (DataFrame): DataFrame
        filtered (bool, optional): If only relevant jobs will be returned. Defaults to True.
        categories_reduced (bool, optional): If only Data Science and Data Analysis jobs will be returned. Defaults to True.

    Returns:
        DataFrame: Cleaned DataFrame
    """    
    return (
        df
        .pipe(clean)
        .pipe(lambda _df: filter(_df, filter=filtered))
        .pipe(zeit_remote)
        .pipe(lambda _df: roles(_df, categories_reduced=categories_reduced))
        .assign(Junior=lambda _df: _df["Titel"].apply(lambda x: "junior" in x.lower()))
        .astype({"Junior": bool})
        .assign(
            Gehalt_min_yearly=lambda _df: _df["Gehalt_min"] * 12,
            Gehalt_max_yearly=lambda _df: _df["Gehalt_max"] * 12,
            Gehalt_durchschnitt_yearly=lambda _df: (
                _df["Gehalt_min_yearly"] + _df["Gehalt_max_yearly"]
            )
            / 2,
        )
        .pipe(remote)
    )
