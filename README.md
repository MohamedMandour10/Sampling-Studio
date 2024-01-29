# Signal Processing and Sampling Application

## Overview

This Python application is designed for signal processing and analysis. It provides a graphical user interface (GUI) built with PyQt6 and utilizes various signal processing techniques and features. Users can load, process, and analyze signal data from different sources, as well as manipulate and visualize signals with components. The application includes features for handling noise, signal reconstruction, and more.

## Features

### Main Window Class

The core of the application is represented by the `MainWindow` class, which extends `QtWidgets.QMainWindow`. This class serves as the main user interface for the application.

### Signal Management

- **Loading Signals**: Users can load signal data from various file types, including CSV and WAV files. The application can read and parse the data, making it available for further analysis.

- **Adding Components**: Signals can be composed of multiple components, which users can add and configure. Components include frequency, amplitude, and phase parameters.

- **Signal Generation**: The application allows users to generate mixed signals by specifying and combining components. It supports the generation of signals with added noise based on signal-to-noise ratio (SNR).

- **Signal Visualization**: Loaded signals and generated mixed signals are plotted for visualization. Users can select and analyze specific signals using the GUI.

### Signal Processing

- **Signal Sampling**: Users can adjust the sampling rate, either based on the actual signal frequency or by specifying a custom rate. The application provides options for subsampling and signal reconstruction.

- **Signal Reconstruction**: The application supports signal reconstruction using sinc interpolation, allowing users to see the effects of subsampling on the signal.

- **Signal Error Analysis**: Users can visualize the difference between the original and reconstructed signals to analyze the quality of the reconstruction.

- **Noise Handling**: Noise can be added to signals based on the specified SNR. The application calculates and adds noise to the signal data, allowing users to observe the impact on signal quality.

### User Interface

- **Graphical Visualization**: Signals, reconstructed signals, and error plots are displayed in graphical form using PyQtGraph.

- **Interactive Elements**: Users can interact with the GUI through buttons, sliders, and radio buttons to control various aspects of signal processing and visualization.
## Demo
- **Top Graph**: Original signal
- **Middle Graph**: Reconstructed signal
- **Bottom Graph**: Difference error between Original signal and Reconstructed signal

https://github.com/MohamedMandour10/Sampling-Studio/assets/115044826/e29edee7-b996-44d4-b918-eb997573653b


## Getting Started

1. **Installation**: To run the application, you need to have the required Python packages installed. You can create a virtual environment and install the necessary dependencies listed in the `requirements.txt` file.

   ```bash
   pip install -r requirements.txt

2. **Running the Application**: Run the application using Python. The GUI will open, allowing you to load, process, and analyze signals.

   ```bash
   python main.py

## Contributors <a name = "Contributors"></a>
<table>
  <tr>
    <td align="center">
    <a href="https://github.com/MohamedMandour10" target="_black">
    <img src="https://avatars.githubusercontent.com/u/115044826?v=4" width="150px;" alt="Mohamed Elsayed Eid"/>
    <br />
    <sub><b>Mohamed Elsayed Eid</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/mohamedmosilhy" target="_black">
    <img src="https://avatars.githubusercontent.com/u/93820559?v=4" width="150px;" alt="mohamed mosilhy"/>
    <br />
    <sub><b>Mohamed Mosilhy</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/MahmoudMagdy404" target="_black">
    <img src="https://avatars.githubusercontent.com/u/83336074?v=4" width="150px;" alt="Mahmoud Magdy"/>
    <br />
    <sub><b>Mahmoud Magdy</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/joyou159" target="_black">
    <img src="https://avatars.githubusercontent.com/u/85418161?v=4" width="150px;" alt="Youssef Ahmed"/>
    <br />
    <sub><b>Youssef Ahmed</b></sub></a>
    </td>
      </tr>

