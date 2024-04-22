import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import subprocess
import os
import base64
import pickle

# Molecular descriptor calculator
def desc_calc(input_data):
    input_data.to_csv('molecule.smi', sep='\t', header=False, index=False)
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    desc = pd.read_csv('descriptors_output.csv')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    return desc_subset

# Model building
def build_model(input_data):
    # Reads in saved regression model
    load_model = pickle.load(open('acetylcholinesterase_model.pkl', 'rb'))
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(input_data.iloc[:, 0], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    return b64

def predict():
    try:
        input_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not input_file:
            return

        input_data = pd.read_csv(input_file, header=None)
        desc_subset = desc_calc(input_data)
        prediction_df = build_model(desc_subset)
        b64_csv = filedownload(prediction_df)

        with open("predictions.csv", "w") as f:
            f.write(base64.b64decode(b64_csv).decode())

        messagebox.showinfo("Success", "Prediction completed. Results saved as 'predictions.csv'")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Bioactivity Prediction")

label = tk.Label(root, text="Please select your input CSV file:")
label.pack()

button = tk.Button(root, text="Select File", command=predict)
button.pack()

root.mainloop()
