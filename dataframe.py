import re
import math

class DataFrame:
    def __init__(self, data):
        self.data = data
        self.columns = list(data.keys())
        self.num_rows = len(next(iter(data.values()))) if data else 0

    def __getitem__(self, key):
        """Get a column by name."""
        return self.data[key]

    def __repr__(self):
        """Pretty print a preview of the DataFrame (first 5 rows)."""
        preview_rows = min(5, self.num_rows)
        preview = {col: self.data[col][:preview_rows] for col in self.columns}
        return f"DataFrame({preview})"
    
    def to_rows(self, n=None):
        """Helps w/ printing table pretty for application"""
        data_dict = getattr(self, "data", None) or getattr(self, "columns", None)
        if not isinstance(data_dict, dict):
            raise TypeError("Expected internal data to be a dict of columns.")
    
        col_names = list(data_dict.keys())
        rows = list(zip(*data_dict.values()))
        if n is not None:
            rows = rows[:n]
        return [dict(zip(col_names, row)) for row in rows]
    
    @classmethod
    def from_rows(cls, rows: list[dict]):
        """Create a DataFrame from a list of dictionaries (rows)."""
        if not rows:
            return cls({})

        # extract column names
        columns = rows[0].keys()
        data = {col: [] for col in columns}

        # fill columns with row values
        for row in rows:
            for col in columns:
                data[col].append(row.get(col))

        return cls(data)

    def head(self, n=5):
        """Return the first n rows as a new DataFrame-like dict."""
        n = min(n, self.num_rows)
        return {col: values[:n] for col, values in self.data.items()}

    def describe(self):
        """Return basic statistics for numeric columns."""
        desc = {}
        for col, values in self.data.items():
            # numeric values convert to float
            numeric = []
            for v in values:
                try:
                    numeric.append(float(v))
                except ValueError:
                    pass
            if numeric:
                mean = sum(numeric) / len(numeric)
                std = math.sqrt(sum((x - mean) ** 2 for x in numeric) / len(numeric))
                desc[col] = {
                    "count": len(numeric),
                    "mean": round(mean, 2),
                    "std": round(std, 2),
                    "min": min(numeric),
                    "max": max(numeric)
                }
        return desc

    def unique(self, column):
        """Return unique values in a given column."""
        if column not in self.data:
            raise KeyError(f"Column '{column}' not found.")
        return list(set(self.data[column]))

    def row(self, index):
        """Return a single row as a dict."""
        if index < 0 or index >= self.num_rows:
            raise IndexError("Row index out of range")
        return {col: self.data[col][index] for col in self.columns}

    def filter(self, func):
        """Filter rows based on a condition (function returns True/False)."""
        filtered_data = {col: [] for col in self.columns}
        for i in range(self.num_rows):
            row = {col: self.data[col][i] for col in self.columns}
            if func(row):
                for col in self.columns:
                    filtered_data[col].append(self.data[col][i])
        return DataFrame(filtered_data)

    def select(self, cols):
        """Select a subset of columns."""
        selected_data = {col: self.data[col] for col in cols}
        return DataFrame(selected_data)

    def group_by(self, group_col):
        """Group the DataFrame by a column, returning a dict of DataFrames."""
        groups = {}
        for i in range(self.num_rows):
            key = self.data[group_col][i]
            if key not in groups:
                groups[key] = {col: [] for col in self.columns}
            for col in self.columns:
                groups[key][col].append(self.data[col][i])
        return {k: DataFrame(v) for k, v in groups.items()}

    def aggregate(self, col, func):
        """Apply an aggregate function to a single column."""
        return func(self.data[col])
    
    def join(self,other,on=None,left_on=None,right_on=None,how="inner",lsuffix="_x",rsuffix="_y",substring=False):
        """Apply a join between 2 columns, optionally using substring matching."""

        # handle parameter compatibility
        if on is not None and (left_on is not None or right_on is not None):
            raise ValueError("Cannot specify both 'on' and 'left_on'/'right_on'")

        # normalize keys
        if on is not None:
            if isinstance(on, str):
                on = [on]
            left_keys = right_keys = on
        else:
            if isinstance(left_on, str):
                left_on = [left_on]
            if isinstance(right_on, str):
                right_on = [right_on]
            if left_on is None or right_on is None:
                raise ValueError("Must specify both 'left_on' and 'right_on' when joining on differently named columns.")
            if len(left_on) != len(right_on):
                raise ValueError("'left_on' and 'right_on' must have the same number of columns.")
            left_keys = left_on
            right_keys = right_on

        # validate keys exist
        for lcol in left_keys:
            if lcol not in self.columns:
                raise KeyError(f"Join key '{lcol}' not found in left DataFrame.")
        for rcol in right_keys:
            if rcol not in other.columns:
                raise KeyError(f"Join key '{rcol}' not found in right DataFrame.")

        # prepare combined columns (handle duplicates)
        new_cols = {}
        for col in self.columns:
            if col in other.columns and col not in right_keys:
                new_cols[col + lsuffix] = self.data[col]
            else:
                new_cols[col] = self.data[col]
        for col in other.columns:
            if col not in right_keys:
                name = col + rsuffix if col in self.columns else col
                new_cols[name] = []

        result_data = {col: [] for col in new_cols.keys()}

        # build join key lists
        left_keys_values = [tuple(self.data[k][i] for k in left_keys) for i in range(self.num_rows)]
        right_keys_values = [tuple(other.data[k][i] for k in right_keys) for i in range(other.num_rows)]

        matches = []  # list of (li, ri) index pairs

        # substring matching
        if substring:
            if len(left_keys) != 1 or len(right_keys) != 1:
                raise ValueError("Substring matching only supports single-column joins for now.")
            left_col = left_keys[0]
            right_col = right_keys[0]

            for li, left_val in enumerate(self.data[left_col]):
                if left_val is None:
                    continue
                left_val_str = str(left_val).strip().lower()
                matched = False
                for ri, right_val in enumerate(other.data[right_col]):
                    if right_val is None:
                        continue
                    right_val_str = str(right_val).strip().lower()

                    pattern = r"\b" + re.escape(left_val_str) + r"\b"
                    if re.search(pattern, right_val_str):
                        matches.append((li, ri))
                        matched = True
                if not matched and how in ("left", "outer"):
                    matches.append((li, None))

        else:
            # exact matching
            def build_index(df, keys):
                idx = {}
                for i in range(df.num_rows):
                    key = tuple(df.data[k][i] for k in keys)
                    idx.setdefault(key, []).append(i)
                return idx

            left_index = build_index(self, left_keys)
            right_index = build_index(other, right_keys)

            if how == "inner":
                all_keys = left_index.keys() & right_index.keys()
            elif how == "left":
                all_keys = left_index.keys()
            elif how == "right":
                all_keys = right_index.keys()
            elif how == "outer":
                all_keys = left_index.keys() | right_index.keys()
            else:
                raise ValueError("how must be one of: 'inner', 'left', 'right', 'outer'")

            for key in all_keys:
                left_rows = left_index.get(key, [None])
                right_rows = right_index.get(key, [None])
                for li in left_rows:
                    for ri in right_rows:
                        matches.append((li, ri))

        # combine rows
        for li, ri in matches:
            row = {}
            for col in self.columns:
                name = col + lsuffix if col in other.columns and col not in right_keys else col
                row[name] = self.data[col][li] if li is not None else None
            for col in other.columns:
                if col not in right_keys:
                    name = col + rsuffix if col in self.columns else col
                    row[name] = other.data[col][ri] if ri is not None else None
            # Add join key columns
            for i, lcol in enumerate(left_keys):
                row[lcol] = self.data[lcol][li] if li is not None else None
            for k, v in row.items():
                result_data[k].append(v)

        return DataFrame(result_data)


# helper functions
def convert_value(val):
    """Try to convert strings to int or float, otherwise keep as str."""
    if val == "":
        return val
    if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
        val = val[1:-1]
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


def read_csv(source, sep=","):
    """Read a CSV file into a DataFrame (handles quotes and numeric types).
    Works with both file paths and file-like objects (e.g., UploadedFile).
    """
    pattern = re.compile(
        r'''
        \s*
        (?:
          "((?:[^"]|"")*)"   # Quoted field, handle escaped quotes
          |
          ([^",]*)           # Unquoted field
        )
        \s*
        (?:,|$)
        ''',
        re.VERBOSE
    )

    # file path vs. file-like object
    if hasattr(source, "read"): 
        # Ensure it's read as text
        if isinstance(source.read(0), bytes):
            text = source.read().decode("utf-8-sig")
        else:
            text = source.read()
        source.seek(0)  # reset pointer if needed
        lines = text.splitlines()
    else:
        # standard file path
        with open(source, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()

    columns = None
    for i, line in enumerate(lines):
        line = line.rstrip("\n\r")
        if not line:
            continue

        values = []
        for m in pattern.finditer(line):
            val = m.group(1) or m.group(2) or ""
            val = val.replace('""', '"').strip()
            val = convert_value(val)
            values.append(val)

        if i == 0:
            header = values
            columns = {h: [] for h in header}
        else:
            for h, v in zip(header, values):
                columns[h].append(v)

    return DataFrame(columns)
