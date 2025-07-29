import duckdb
import os
import re
import ast
import pandas as pd
from importlib.resources import files

class disease:
    DB_PATH = str(files("PCPy.data").joinpath("pcpy.duckdb"))

    def __init__(self, query):
        self.query = query.strip().lower()
        self.conn = duckdb.connect(self.DB_PATH)
        self.df = self.conn.execute("SELECT * FROM diseases").fetchdf()
        self.df["mesh_id"] = self.df["mesh_id"].astype(str).str.lower()
        self.df["mesh_term"] = self.df["mesh_term"].astype(str).str.lower()
        self.summary_data = self._lookup()

    def _lookup(self):
        def match_row(row):
            if row["mesh_id"] == self.query or row["mesh_term"] == self.query:
                return True
            try:
                terms = ast.literal_eval(str(row["entry_terms"]))
                return self.query in [t.lower() for t in terms]
            except:
                return False

        matches = self.df[self.df.apply(match_row, axis=1)]
        if matches.empty:
            raise ValueError(f"No data found for: {self.query}")
        row = matches.iloc[0]

        child_nodes = []
        if pd.notna(row["child_nodes"]) and row["child_nodes"].strip():
            nodes = re.findall(r'([^\[\]]+)\s*\[p=(\d+),\s*c=(\d+)\]', row["child_nodes"])
            for name, p, c in nodes:
                child_nodes.append({
                    "name": name.strip(),
                    "p_count": int(p),
                    "c_count": int(c)
                })

        drugs = []
        if pd.notna(row["drug_names"]) and row["drug_names"].strip():
            try:
                drug_list = ast.literal_eval(row["drug_names"])
                for entry in drug_list:
                    match = re.match(r"(.*?)\s*\(p_count\s*=\s*(\d+),\s*c_count\s*=\s*(\d+)\)", entry)
                    if match:
                        drugs.append({
                            "name": match.group(1).strip(),
                            "p_count": int(match.group(2)),
                            "c_count": int(match.group(3)),
                        })
            except:
                pass

        return {
            "Disease": row["mesh_term"],
            "mesh_id": row["mesh_id"],
            "is_specific": bool(row.get("is_specific", False)),
            "p_count": row["p_count"],
            "c_count": row["c_count"],
            "child_nodes": pd.DataFrame(child_nodes) if child_nodes else pd.DataFrame(columns=["name", "p_count", "c_count"]),
            "drugs": pd.DataFrame(drugs) if drugs else pd.DataFrame(columns=["name", "p_count", "c_count"]),
        }

    def summary(self, key=None):
        if key is None:
            return self.summary_data
        return self.summary_data.get(key, None)

    def export(self, fields):
        output = []
        if "disease.id" in fields:
            output.append(str(self.summary_data["mesh_id"]))
        if "disease.term" in fields:
            output.append(str(self.summary_data["Disease"]))
        if "disease.type" in fields:
            output.append("Specific" if self.summary_data["is_specific"] else "Non-Specific")
        if "disease.p_count" in fields:
            output.append(str(self.summary_data["p_count"]))
        if "disease.c_count" in fields:
            output.append(str(self.summary_data["c_count"]))
        if "disease.node_count" in fields:
            output.append(str(len(self.summary_data["child_nodes"])))
        if "disease.drug_count" in fields:
            output.append(str(len(self.summary_data["drugs"])))

        if "disease.nodes" in fields and not self.summary_data["child_nodes"].empty:
            df_nodes = self.summary_data["child_nodes"]
            df_nodes.columns = ["disease", "p_count", "c_count"]
            os.makedirs("extract/disease", exist_ok=True)
            file_name = self.summary_data["Disease"].replace(" ", "_") + "_nodes.tsv"
            df_nodes.to_csv(os.path.join("extract/disease", file_name), sep="\t", index=False)

        if "disease.drugs" in fields and not self.summary_data["drugs"].empty:
            df_drugs = self.summary_data["drugs"]
            df_drugs.columns = ["drug_name", "p_count", "c_count"]
            os.makedirs("extract/disease", exist_ok=True)
            file_name = self.summary_data["Disease"].replace(" ", "_") + "_drugs.tsv"
            df_drugs.to_csv(os.path.join("extract/disease", file_name), sep="\t", index=False)

        return "\n".join(output)

    @property
    def id(self):
        return self.summary_data["mesh_id"]

    @property
    def term(self):
        return self.summary_data["Disease"]

    @property
    def p_count(self):
        return self.summary_data["p_count"]

    @property
    def c_count(self):
        return self.summary_data["c_count"]

    @property
    def type(self):
        return "Specific" if self.summary_data["is_specific"] else "Non-Specific"

    @property
    def nodes(self):
        return self.summary_data["child_nodes"]

    @property
    def node_count(self):
        return len(self.summary_data["child_nodes"])

    @property
    def drugs(self):
        return self.summary_data["drugs"]

    @property
    def drug_count(self):
        return len(self.summary_data["drugs"])