import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle
import gradio as gr

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

# Logo image
image = Image.open('logo.png')

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'data:file/csv;base64,{b64}'
    return href

# Interface
def predict_interface(input_data):
    desc_subset = desc_calc(input_data)
    prediction_df = build_model(desc_subset)
    href = filedownload(prediction_df)
    return prediction_df, href

iface = gr.Interface(
    fn=predict_interface,
    inputs=gr.inputs.Dataframe(header=False, type='csv'),
    outputs=[gr.outputs.Dataframe(), "text"]
)

iface.launch()
