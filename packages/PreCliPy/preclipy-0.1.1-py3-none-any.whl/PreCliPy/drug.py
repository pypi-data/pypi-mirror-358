import duckdb
import os
import pandas as pd
from importlib.resources import files

class drug:
    DB_PATH = str(files("PCPy.data").joinpath("pcpy.duckdb"))

    def __init__(self, query):
        self.query = query.strip().lower()
        self.conn = duckdb.connect(self.DB_PATH)
        self.df = self.conn.execute("SELECT * FROM drugs").fetchdf()
        self.df["drug_name"] = self.df["drug_name"].astype(str).str.lower()
        self.summary_data = self._lookup()

    def _lookup(self):
        matches = self.df[self.df["drug_name"] == self.query]
        if matches.empty:
            raise ValueError(f"No data found for: {self.query}")

        return {
            "Drug": self.query,
            "disease_count": matches.shape[0],
            "preclinical_count": int(matches["p_count"].sum()),
            "clinical_count": int(matches["c_count"].sum()),
            "disease_breakdown": matches[["mesh_id", "mesh_term", "p_count", "c_count"]].copy()
        }

    def summary(self, key=None):
        if key is None:
            return self.summary_data
        return self.summary_data.get(key, None)

    def export(self, fields):
        output = []

        if "drug.name" in fields:
            output.append(self.summary_data["Drug"])
        if "drug.disease_count" in fields:
            output.append(str(self.summary_data["disease_count"]))
        if "drug.p_count" in fields:
            output.append(str(self.summary_data["preclinical_count"]))
        if "drug.c_count" in fields:
            output.append(str(self.summary_data["clinical_count"]))

        if "drug.disease" in fields and not self.summary_data["disease_breakdown"].empty:
            df = self.summary_data["disease_breakdown"]
            df.columns = ["mesh_id", "mesh_term", "p_count", "c_count"]
            os.makedirs("extract/drug", exist_ok=True)
            file_name = self.summary_data["Drug"].replace(" ", "_") + "_breakdown.tsv"
            df.to_csv(os.path.join("extract/drug", file_name), sep="\t", index=False)

        return "\n".join(output)

    @property
    def name(self):
        return self.summary_data["Drug"]

    @property
    def disease_count(self):
        return self.summary_data["disease_count"]

    @property
    def p_count(self):
        return self.summary_data["preclinical_count"]

    @property
    def c_count(self):
        return self.summary_data["clinical_count"]

    @property
    def diseases(self):
        return self.summary_data["disease_breakdown"]

    @property
    def disease_breakdown_count(self):
        return len(self.summary_data["disease_breakdown"])