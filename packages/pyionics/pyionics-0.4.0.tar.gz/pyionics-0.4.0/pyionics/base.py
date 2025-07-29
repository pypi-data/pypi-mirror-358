import csv,json,os,requests,re
from tqdm import tqdm
import pandas as pd
def get_data_dir():
    # Use current working directory for storing downloaded data
    return os.path.abspath(os.path.join(os.getcwd(), "data"))

def getIdsets(prop=None, data_path=None, cmp="", ncmp="0", year="", auth="", keyw=""):
    if not prop:
        prop = ""
    if not prop and not any([cmp, ncmp != "0", year, auth, keyw]):
        raise ValueError("At least one parameter must be provided (prop or another search parameter).")

    prop_id = None
    if prop:
        if data_path is None:
            # Look for property_idsets.csv in package data (installed location)
            data_path = os.path.join(os.path.dirname(__file__), "keyData/property_idsets.csv")
        _, ext = os.path.splitext(data_path)
        if ext.lower() == ".json":
            with open(data_path, "r") as f:
                data = json.load(f)
                for row in data:
                    if row.get('short') == prop:
                        prop_id = row.get('id')
                        break
        else:
            with open(data_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['short'] == prop:
                        prop_id = row['id']
                        break
        if not prop_id:
            raise ValueError(f"Short property code '{prop}' not found in data file.")

    # Build the URL with user-supplied parameters
    url = (
        f"https://ilthermo.boulder.nist.gov/ILT2/ilsearch?"
        f"cmp={cmp}&ncmp={ncmp}&year={year}&auth={auth}&keyw={keyw}"
    )
    if prop_id:
        url += f"&prp={prop_id}"
    response = requests.get(url)
    response.raise_for_status()
    content = response.content

    # Build filename suffix from non-empty parameters
    params = []
    if cmp: params.append(f"cmp_{cmp}")
    if ncmp and ncmp != "0":
        ncmp_map = {"1": "pure", "2": "binary", "3": "triple"}
        ncmp_label = ncmp_map.get(str(ncmp), ncmp)
        params.append(f"ncmp_{ncmp_label}")
    elif ncmp == "0":
        params.append("ncmp_all")
    if year: params.append(f"year_{year}")
    if auth: params.append(f"auth_{auth}")
    if keyw: params.append(f"keyw_{keyw}")
    suffix = "_" + "_".join(params) if params else ""
    # Save to cwd/data/idsets
    data_dir = os.path.join(get_data_dir(), "idsets")
    os.makedirs(data_dir, exist_ok=True)
    save_path = f"{prop}_idsets{suffix}.json"
    save_path = os.path.join(data_dir, save_path)
    try:
        # Try to decode as JSON, else save as text
        data = response.json()
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except ValueError:
        # Not JSON, save as text
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content.decode("utf-8", errors="replace"))

    return save_path  # Return the path to the saved file


def getData(prop=None, data_path=None, cmp="", ncmp="0", year="", auth="", keyw=""):
    # Step 1: Call getIdsets to download the idsets file and get its path
    save_path = getIdsets(prop=prop, data_path=data_path, cmp=cmp, ncmp=ncmp, year=year, auth=auth, keyw=keyw)

    # Step 2: Determine the path to the saved idsets file (already absolute from getIdsets)
    # Determine folder name based on prop and ncmp
    prop_label = prop if prop else "all"
    ncmp_map = {"1": "pure", "2": "binary", "3": "triple"}
    ncmp_label = ncmp_map.get(str(ncmp), "all") if ncmp and ncmp != "0" else "all"

    # Add other input properties to the folder name if provided
    extra_labels = []
    if cmp:
        extra_labels.append(f"cmp_{cmp}")
    if year:
        extra_labels.append(f"year_{year}")
    if auth:
        extra_labels.append(f"auth_{auth}")
    if keyw:
        extra_labels.append(f"keyw_{keyw}")

    extra_suffix = "_" + "_".join(extra_labels) if extra_labels else ""
    # Save to cwd/data/{prop_label}_{ncmp_label}_data{extra_suffix}
    idset_dir = os.path.join(get_data_dir(), f"{prop_label}_{ncmp_label}_data{extra_suffix}")
    os.makedirs(idset_dir, exist_ok=True)

    # Step 3: Read the idsets from the JSON file
    with open(save_path, "r", encoding="utf-8") as f:
        idsets_json = json.load(f)
    # idsets are the first element of each sublist in 'res'
    idsets = []
    if isinstance(idsets_json, dict) and 'res' in idsets_json:
        idsets = [row[0] for row in idsets_json['res']]

    # Step 4: Download each idset's data and save as JSON in the new folder
    for setid in tqdm(idsets, desc="Downloading idsets"):
        url = f"https://ilthermo.boulder.nist.gov/ILT2/ilset?set={setid}"
        resp = requests.get(url)
        resp.raise_for_status()
        # Always save the full JSON/text response in the file, even if not valid JSON
        try:
            data = resp.json()
            # Use the 'data' field from the response for the filename if present
            file_base = None
            if isinstance(data, dict) and "idsets" in data:
                # If 'data' is a list, use the first element's 'id' or 'name' if available
                if isinstance(data["idsets"], list) and data["idsets"]:
                    entry = data["idsets"][0]
                    if isinstance(entry, dict):
                        file_base = entry.get("id") or entry.get("name")
            if not file_base:
                file_base = str(setid)
        except Exception:
            # Save the raw text content as a JSON string under a "raw" key
            data = {"raw": resp.content.decode("utf-8", errors="replace")}
            file_base = str(setid)
        # Save the original filename info in the content
        data["filename"] = file_base
        fname = os.path.join(idset_dir, f"idset_{setid}.json")
        with open(fname, "w", encoding="utf-8") as outf:
            json.dump(data, outf, ensure_ascii=False, indent=2)

    return setid


def convert2csv(folder_name='', file_name=''):
    """
    Convert files in the specified folder to CSV format.
    
    :param folder_name: The folder containing the files to convert.
    :param file_name: The specific file to convert (if empty, all files in the folder will be converted).
    """
    # Ensure 'data/' is in the folder path
    data_root = os.path.abspath(os.path.join(os.getcwd(), "data"))
    if folder_name and not folder_name.startswith(data_root):
        folder_name = os.path.join(data_root, folder_name) if not folder_name.startswith('data/') else os.path.join(os.getcwd(), folder_name)
    elif not folder_name:
        folder_name = data_root
    # Ensure the folder exists
    if not os.path.exists(folder_name):
        print(f"Folder '{folder_name}' does not exist.")
        return

    # Prepare output folder: data/csv_{folder_name}
    base_folder = os.path.basename(folder_name.rstrip('/\\'))
    output_folder = os.path.join(data_root, f'csv_{base_folder}')
    os.makedirs(output_folder, exist_ok=True)

    # List all files in the folder
    files = os.listdir(folder_name)
    
    # If a specific file is provided, filter the list
    if file_name:
        files = [file_name] if file_name in files else []
    
    for file in files:
        file_path = os.path.join(folder_name, file)
        if os.path.isfile(file_path) and file.endswith('.json'):
            # --- Extract idset from filename ---
            match = re.match(r'idset_(.+)\.json$', file)
            idset = match.group(1) if match else ''
            # Convert JSON to CSV
            with open(file_path, 'r', encoding='utf-8') as fin:
                try:
                    jdata = json.load(fin)
                except Exception as e:
                    print(f"Failed to load JSON from {file}: {e}")
                    continue
            dhead = jdata.get('dhead')
            data_rows = jdata.get('data')
            # --- Extract author from ref ---
            ref = jdata.get('ref')
            
            if not ref and isinstance(data_rows, list) and len(data_rows) > 0:
                # Try to get from first row if available
                # Assume first row, second column is ref
                try:
                    ref = data_rows[0][1]
                except Exception:
                    ref = ""
            author = ""
            if ref:
                if isinstance(ref, str):
                    # Get first surname before comma, add "et al."
                    surname = ref
                    author = f"{surname} et al."
                elif isinstance(ref, dict):
                    # Try to extract author from dict
                    author_val = ref.get('full') or ref.get('authors') or ""
                    if isinstance(author_val, str):
                        surname = author_val.split(",")[0].strip()
                        author = f"{surname} et al."
                    elif isinstance(author_val, list) and author_val:
                        # If it's a list, take the first element
                        surname = str(author_val[0]).split(",")[0].strip()
                        author = f"{surname} et al."
            if not dhead or not data_rows:
                continue
            # Flatten dhead to get header row
            header = ['idset', 'author']  # Insert idset and author as first columns
            for col in dhead:
                col_names = [str(x) for x in col if x]
                header.append(" - ".join(col_names) if col_names else "")
            # --- Add component columns ---
            components = jdata.get('components', [])
            n_components = len(components)
            comp_headers = []
            for i in range(n_components):
                comp_headers.append(f'component {i+1} idout')
                comp_headers.append(f'component {i+1} name')
                comp_headers.append(f'component {i+1} formula')
            header += comp_headers
            # Prepare CSV output path
            output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.csv')
            with open(output_file, 'w', newline='', encoding='utf-8') as fout:
                writer = csv.writer(fout)
                writer.writerow(header)
                for row in data_rows:
                    flat_row = [idset, author]  # Insert idset and author as first values
                    for cell in row:
                        if isinstance(cell, list):
                            cell_str = ";".join(str(x) for x in cell)
                        else:
                            cell_str = str(cell)
                        # Remove <SUB> and </SUB> tags
                        cell_str = cell_str.replace('<SUB>', '').replace('</SUB>', '')
                        flat_row.append(cell_str)
                    # --- Add component values ---
                    comp_values = []
                    for comp in components:
                        idout = str(comp.get('idout', '')).replace('<SUB>', '').replace('</SUB>', '')
                        name = str(comp.get('name', '')).replace('<SUB>', '').replace('</SUB>', '')
                        formula = str(comp.get('formula', '')).replace('<SUB>', '').replace('</SUB>', '')
                        comp_values.extend([idout, name, formula])
                    flat_row += comp_values
                    writer.writerow(flat_row)
        elif os.path.isfile(file_path):
            # Here you would implement the conversion logic for other file types
            # Example: Save to output_folder with .csv extension
            output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.csv')
            # Conversion logic goes here, e.g.:
            # with open(file_path, 'r') as fin, open(output_file, 'w') as fout:
            #     fout.write(fin.read())
        else:
            print(f"{file} is not a valid file.")

def convert2tsv(folder_name='', file_name=''):
    """
    Convert files in the specified folder to TSV format.
    
    :param folder_name: The folder containing the files to convert.
    :param file_name: The specific file to convert (if empty, all files in the folder will be converted).
    """
    # Ensure 'data/' is in the folder path
    data_root = os.path.abspath(os.path.join(os.getcwd(), "data"))
    if folder_name and not folder_name.startswith(data_root):
        folder_name = os.path.join(data_root, folder_name) if not folder_name.startswith('data/') else os.path.join(os.getcwd(), folder_name)
    elif not folder_name:
        folder_name = data_root
    # Ensure the folder exists
    if not os.path.exists(folder_name):
        print(f"Folder '{folder_name}' does not exist.")
        return

    # Prepare output folder: data/tsv_{folder_name}
    base_folder = os.path.basename(folder_name.rstrip('/\\'))
    output_folder = os.path.join(data_root, f'tsv_{base_folder}')
    os.makedirs(output_folder, exist_ok=True)

    # List all files in the folder
    files = os.listdir(folder_name)
    
    # If a specific file is provided, filter the list
    if file_name:
        files = [file_name] if file_name in files else []
    
    for file in files:
        file_path = os.path.join(folder_name, file)
        if os.path.isfile(file_path) and file.endswith('.json'):
            # Convert JSON to TSV
            with open(file_path, 'r', encoding='utf-8') as fin:
                try:
                    jdata = json.load(fin)
                except Exception as e:
                    print(f"Failed to load JSON from {file}: {e}")
                    continue
            dhead = jdata.get('dhead')
            data_rows = jdata.get('data')
            if not dhead or not data_rows:
                print(f"Skipping {file}: missing 'dhead' or 'data'")
                continue
            header = []
            for col in dhead:
                col_names = [str(x) for x in col if x]
                header.append(" - ".join(col_names) if col_names else "")
            # --- Add component columns ---
            components = jdata.get('components', [])
            n_components = len(components)
            comp_headers = []
            for i in range(n_components):
                comp_headers.append(f'component {i+1} idout')
                comp_headers.append(f'component {i+1} name')
                comp_headers.append(f'component {i+1} formula')
            header += comp_headers
            output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.tsv')
            with open(output_file, 'w', newline='', encoding='utf-8') as fout:
                writer = csv.writer(fout, delimiter='\t')
                writer.writerow(header)
                for row in data_rows:
                    flat_row = []
                    for cell in row:
                        if isinstance(cell, list):
                            cell_str = ";".join(str(x) for x in cell)
                        else:
                            cell_str = str(cell)
                        # Remove <SUB> and </SUB> tags
                        cell_str = cell_str.replace('<SUB>', '').replace('</SUB>', '')
                        flat_row.append(cell_str)
                    # --- Add component values ---
                    comp_values = []
                    for comp in components:
                        idout = str(comp.get('idout', '')).replace('<SUB>', '').replace('</SUB>', '')
                        name = str(comp.get('name', '')).replace('<SUB>', '').replace('</SUB>', '')
                        formula = str(comp.get('formula', '')).replace('<SUB>', '').replace('</SUB>', '')
                        comp_values.extend([idout, name, formula])
                    flat_row += comp_values
                    writer.writerow(flat_row)
        elif os.path.isfile(file_path):
            # Here you would implement the conversion logic for other file types
            # Example: Save to output_folder with .tsv extension
            output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.tsv')
            # Conversion logic goes here, e.g.:
            # with open(file_path, 'r') as fin, open(output_file, 'w') as fout:
            #     fout.write(fin.read())
        else:
            print(f"{file} is not a valid file.")


def mergeFiles(folder_name):
    # Use cwd/data as root
    data_root = os.path.abspath(os.path.join(os.getcwd(), "data"))
    folder_path = os.path.join(data_root, folder_name)
    
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_name}' does not exist in the 'data' directory (expected at: {folder_path}).")
        return
    
    # List all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    # Initialize an empty DataFrame to hold merged data
    merged_data = pd.DataFrame()
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            # Read each file into a DataFrame
            data = pd.read_csv(file_path)
            merged_data = pd.concat([merged_data, data], ignore_index=True)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Save the merged DataFrame to a new CSV file
    output_file = os.path.join(data_root, f'merged_{folder_name}.csv')
    merged_data.to_csv(output_file, index=False)



def addSmiles(folder_name='', file_name=''):
    """
    For each CSV file in the specified folder, or for a specific file, replace the 'component {n} formula' column value
    with the corresponding SMILES from smiles.csv, matching on 'component {n} idout'.
    Only one of folder_name or file_name should be provided.
    """
    # Use cwd/data as root
    data_root = os.path.abspath(os.path.join(os.getcwd(), "data"))

    # Determine input path(s)
    if folder_name and not file_name:
        # Only folder_name provided
        if not folder_name.startswith(data_root):
            folder_name = os.path.join(data_root, folder_name) if not folder_name.startswith('data/') else os.path.join(os.getcwd(), folder_name)
        files = [f for f in os.listdir(folder_name) if f.endswith('.csv')]
        input_paths = [os.path.join(folder_name, f) for f in files]
        base_folder = os.path.basename(folder_name.rstrip('/\\'))
    elif file_name and not folder_name:
        # Only file_name provided
        if not file_name.endswith('.csv'):
            file_name += '.csv'
        file_path = os.path.join(data_root, file_name)
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            return
        input_paths = [file_path]
        base_folder = ''
    elif folder_name and file_name:
        # Both provided: process just that file in the folder
        if not folder_name.startswith(data_root):
            folder_name = os.path.join(data_root, folder_name) if not folder_name.startswith('data/') else os.path.join(os.getcwd(), folder_name)
        file_path = os.path.join(folder_name, file_name)
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            return
        input_paths = [file_path]
        base_folder = os.path.basename(folder_name.rstrip('/\\'))
    else:
        print("Please provide either folder_name or file_name.")
        return

    # Prepare output folder
    output_folder = os.path.join(data_root, f'smiles_{base_folder}') if base_folder else os.path.join(data_root, 'smiles')
    os.makedirs(output_folder, exist_ok=True)

    # Load smiles.csv (must be in the same directory as this script)
    smiles_path = os.path.join(os.path.dirname(__file__), 'keyData/smiles.csv')
    if not os.path.exists(smiles_path):
        print(f"smiles.csv not found at {smiles_path}")
        return

    # Read smiles.csv into a dict: {component id: smiles}
    smiles_dict = {}
    with open(smiles_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        id_header = None
        smiles_header = None
        for h in reader.fieldnames:
            if 'compound id' in h:
                id_header = h
            if 'smiles' in h.lower():
                smiles_header = h
        if not id_header or not smiles_header:
            return
        for row in reader:
            smiles_dict[row[id_header]] = row[smiles_header]

    # Process each input file
    for file_path in input_paths:
        file = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as fin:
            reader = csv.reader(fin)
            rows = list(reader)
        if not rows:
            continue
        header = rows[0]
        # Find all component idout and formula columns
        comp_idout_idxs = []
        comp_formula_idxs = []
        for i, col in enumerate(header):
            if col.startswith('component ') and col.endswith(' idout'):
                comp_idout_idxs.append(i)
            if col.startswith('component ') and col.endswith(' formula'):
                comp_formula_idxs.append(i)
        # Optionally update header to say SMILES instead of formula
        for idx in comp_formula_idxs:
             header[idx] = header[idx].replace('formula', 'SMILES')
        new_rows = [header]
        for row in rows[1:]:
            new_row = row[:]
            for idx_idout, idx_formula in zip(comp_idout_idxs, comp_formula_idxs):
                comp_id = row[idx_idout].strip()
                smiles_val = smiles_dict.get(comp_id, row[idx_formula])
                new_row[idx_formula] = smiles_val
            new_rows.append(new_row)
        # Debug: print first row after replacement
        # Write to output
        output_file = os.path.join(output_folder, file)
        with open(output_file, 'w', newline='', encoding='utf-8') as fout:
            writer = csv.writer(fout)
            writer.writerows(new_rows)
