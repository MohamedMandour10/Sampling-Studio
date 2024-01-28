from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QColorDialog, QListWidgetItem, QPushButton
import numpy as np
import sys
from PyQt6 import QtWidgets, uic
import pyqtgraph as pg
import csv
import os
from PyQt6.QtGui import QIcon
import pandas as pd
from scipy.io import wavfile
from scipy.fft import fft
from scipy.signal import butter, lfilter


from Signal import Signal
from Components import Components


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Signals objects

        self.signals = []
        self.current_signal = None
        self.preparing_signal = None
        self.sliders_init1 = False  # handling_sliders (either set or update)
        self.sliders_init2 = False  # handling_sliders (either set or update)

        self.init_ui()

    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('Lightmode.ui', self)

        self.addComponent.clicked.connect(self.add_component)
        self.ui.GenerateButton.clicked.connect(self.generate_mixer)
        self.ui.signalsList.itemSelectionChanged.connect(
            self.handle_selected_signal)
        self.ui.uploadButton.clicked.connect(self.browse)
        self.ui.startLabel.setText("")
        self.ui.endLabel.setText("")
        self.ui.indicatLabel.setText("")
        self.ui.sampleSlider.valueChanged.connect(self.handle_sample_sliders)
        self.ui.noiseSlider.valueChanged.connect(self.handle_noise_sliders)
        self.ui.actualRadio.toggled.connect(self.radioToggled)
        self.ui.normalRadio.toggled.connect(self.radioToggled)
        self.ui.downloadButton.clicked.connect(self.download_signal)

        # there is a function called update_sliders() that can be used with Noise slider as well
        self.ui.graph1.setBackground("transparent")
        self.ui.graph2.setBackground("transparent")
        self.ui.graph3.setBackground("transparent")
        self.setWindowTitle("Sampling Studio")
        # Replace with the actual path to your icon file
        self.setWindowIcon(QIcon("Icons/sine-wave.png"))

    def handle_last_index(self):
        last_row = len(self.signals) - 1
        if last_row >= 0:
            self.ui.signalsList.setCurrentRow(last_row)
            self.plot_mixed_signals(self.current_signal)

    def browse(self):
        file_filter = "Raw Data (*.csv *.wav)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)

        if file_path:
            file_name = os.path.basename(file_path)
            self.open_file(file_path, file_name)

    def open_file(self, path: str, file_name: str):
        # Lists to store time and data
        time = []  # List to store time values
        data = []  # List to store data values
        frequency = 0

        # Extract the file extension (last 3 characters) from the path
        filetype = path[-3:]

        if filetype == "wav":
            # Read the WAV file
            sample_rate, data = wavfile.read(path)
            time = np.linspace(0, data.shape[0] / sample_rate, data.shape[0])

        # Check if the file type is CSV, text (txt), or Excel (xls)
        if filetype in ["csv", "txt", "xls"]:
            # Open the data file for reading ('r' mode)
            with open(path, 'r') as data_file:
                # Create a CSV reader object with a comma as the delimiter
                data_reader = csv.reader(data_file, delimiter=',')
                next(data_reader)

                # Iterate through each row (line) in the data file
                for row in data_reader:

                    # Extract the time value from the first column (index 0)
                    time_value = float(row[0])

                    # Extract the amplitude value from the second column (index 1)
                    amplitude_value = float(row[1])

                    # Append the time and amplitude values to respective lists
                    time.append(time_value)
                    data.append(amplitude_value)
                    if len(row) == 3:
                        frequency = int(row[2])

        # Create a Signal object with the file name without the extension
        signal = Signal(file_name[:-4])

        signal.data = data[:1000]
        if frequency:
            signal.maxFreq = frequency
        else:
            sample_rate = 1 / (time[1] - time[0])  # Calculate the sample rate
            # Calculate the max frequency
            signal.maxFreq = int(self.get_max_freq(signal, sample_rate))

        signal.sample_rate = signal.maxFreq
        signal.sampling_mode = 0  # Set the sampling mode to 0 by default

        signal.old_noise = np.zeros(1000)

        self.current_signal = signal
        self.signals.append(signal)
        # Add the signal to the GUI signals list
        self.add_to_signalsList(self.current_signal)
        self.handle_last_index()  # Handle the last index
        self.set_sample_sliders()
        self.set_noise_sliders()
        self.add_noise(signal)
        self.plot_mixed_signals(signal)
        self.plot_error(signal)

    def get_max_freq(self, signal, sample_rate):
        fft_result = fft(signal.data)
        # Calculate the frequencies corresponding to the FFT result
        frequencies = np.fft.fftfreq(len(fft_result), 1 / sample_rate)
        return max(frequencies)

    def sample_and_reconstruct(self, signal):
        # signal.sample_rate = 20 # for the sake of testing.sample_ratesnr
        self.ui.graph2.clear()

        # Sample the continuous signal
        # sampled_time = np.linspace(0, 3, signal.sample_rate * 3)
        sampled_time = np.arange(
            0, 3.00000001, 1/signal.sample_rate)  # the upper limit is included
        sampled_data = np.interp(sampled_time, signal.time, signal.data)
        # marking the samples at graph1 plot
        scatter_plot = pg.ScatterPlotItem(
            x=sampled_time, y=sampled_data, pen='r', symbol='x', size=10)
        self.ui.graph1.addItem(scatter_plot)

        # reconstruct the signal using sinc interpolation
        sampling_interval = 1 / signal.sample_rate
        interpolated_data = np.zeros_like(signal.time)

        for i in range(len(sampled_data)):  # convolution
            interpolated_data += sampled_data[i] * np.sinc(
                (signal.time - sampled_time[i])/sampling_interval)

        signal.interpolated_data = interpolated_data

        # plotting the interpolated signal in graph2
        self.ui.graph2.setLabel('left', "Amplitude")
        self.ui.graph2.setLabel('bottom', "Time")
        pen = pg.mkPen(color=(86, 140, 249), width=2)
        self.ui.graph2.plot(signal.time, interpolated_data, pen=pen)

        # y_min = min(signal.data)
        # y_max = max(signal.data)
        # x_min = min(signal.time)
        # x_max = max(signal.time)

        # self.ui.graph2.setLimits(
        #     xMin=x_min-0.3, xMax=x_max+0.3, yMin=y_min+0.3, yMax=y_max+0.3)
        # self.ui.graph2.autoRange()

    def plot_mixed_signals(self, signal):
        if signal:
            self.ui.graph1.clear()

            # Create a plot item
            self.ui.graph1.setLabel('left', "Amplitude")
            self.ui.graph1.setLabel('bottom', "Time")

            # Initialize the time axis (assuming all signals have the same time axis)
            x_data = signal.time

            y_data = signal.data

        # Plot the mixed waveform
            pen = pg.mkPen(color=(86, 140, 249), width=2)
            self.ui.graph1.plot(x_data, y_data, name=signal.name, pen=pen)
            x_min = min(x_data)
            x_max = max(x_data)
            # x_range = [x_min, x_max]
            y_min = min(y_data)
            y_max = max(y_data)
            # y_range = [y_min - 0.3, y_max + 0.3]

            # self.ui.graph1.setRange(xRange=x_range, yRange=y_range)
            self.ui.graph1.setLimits(
                xMin=x_min-0.3, xMax=x_max+0.3, yMin=y_min-0.3, yMax=y_max+0.3)
            self.ui.graph1.autoRange()

            # handling plot in graph2
            self.sample_and_reconstruct(signal)

        self.updateCurrentValueLabel()

    def add_noise(self, signal):
        # Remove old noise from the signal
        signal.data = signal.data - signal.old_noise

        # Calculate the power of the signal
        signal_power = np.mean(signal.data**2)

        # Calculate the noise power based on SNR
        if signal.snr < 50:
            # Calculate noise power using SNR in linear scale
            noise_power = signal_power / (10**(signal.snr / 10))

            # Generate noise with the calculated power
            # Adjust 0.1 to control noise magnitude
            noise_std_dev = np.sqrt(noise_power) * (70 / signal.snr)
            noise = np.random.normal(0, noise_std_dev, len(signal.data))

            # Update the signal's noise attribute
            signal.change_noise(noise)

            # Add noise to the signal
            signal.data = signal.data + noise
        else:
            # If SNR is 0 or negative, no noise is added
            signal.change_noise(np.zeros(len(signal.data)))

    def plot_error(self, signal):
        self.updateCurrentValueLabel()
        if signal:
            self.ui.graph3.clear()

            # Create a plot item
            self.ui.graph3.setLabel('left', "Amplitude")
            self.ui.graph3.setLabel('bottom', "Time")

            # Initialize the time axis (assuming all signals have the same time axis)
            x_data = signal.time

            original_data = signal.data - signal.old_noise

            y_data = original_data - signal.interpolated_data

        # Plot the mixed waveform
            pen = pg.mkPen(color=(86, 140, 249), width=2)
            self.ui.graph3.plot(x_data, y_data, name=signal.name, pen=pen)
            x_min = min(x_data)
            x_max = max(x_data)
            # x_range = [x_min, x_max]
            y_min = min(y_data)
            y_max = max(y_data)
            # y_range = [y_min - 0.3, y_max + 0.3]

            # self.ui.graph3.setRange(xRange=x_range, yRange=y_range)
            self.ui.graph3.setLimits(
                xMin=x_min-0.3, xMax=x_max+0.3, yMin=y_min-0.3, yMax=y_max+0.3)
            self.ui.graph3.autoRange()

    def add_component(self):
        frequency = int(self.ui.freqSpinBox.text())
        amplitude = int(self.ui.ampSpinBox.text())
        phase = int(self.ui.phaseSpinBox.text())

        component = Components(frequency, amplitude, phase)

        if self.preparing_signal is None:
            name = f"Signal {len(self.signals)}"
            signal = Signal(name)

            self.preparing_signal = signal

        self.preparing_signal.add_component(component)
        self.add_to_attrList(component)
        self.handle_real_time()

    def add_to_attrList(self, component):

        text = str(component)

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color:black; background: rgba(74, 74, 74, 0); font-family:opensans;font-weight: 500;")

        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.png"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_attrList(component))

        layout.addWidget(icon_button)
        layout.addWidget(label)
        custom_widget.setLayout(layout)

        # Create a QListWidgetItem and set the custom widget as the display widget
        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.ui.attrList.addItem(item)
        self.ui.attrList.setItemWidget(item, custom_widget)

        # Reset the values
        self.ui.freqSpinBox.setValue(0)
        self.ui.ampSpinBox.setValue(0)
        self.ui.phaseSpinBox.setValue(0)

    def delete_from_attrList(self, component):
        self.preparing_signal.delete_component_during_preparing(component)
        if self.preparing_signal.components == []:
            self.preparing_signal = None
            self.update_attrList()

        else:
            self.update_attrList()
        self.handle_real_time()

    def update_attrList(self):
        self.ui.attrList.clear()
        if self.preparing_signal != None:
            for component in self.preparing_signal.components:
                self.add_to_attrList(component)

    def handle_real_time(self):
        self.graph1.clear()
        self.graph2.clear()
        self.graph3.clear()
        if self.preparing_signal != None:

            self.preparing_signal.generate_points()

            x_data = self.preparing_signal.time

            y_data = self.preparing_signal.data

        # Plot the mixed waveform
            pen = pg.mkPen(color=(86, 140, 249), width=2)
            self.ui.graph1.plot(
                x_data, y_data, name=self.preparing_signal.name, pen=pen)

            x_min = min(x_data)
            x_max = max(x_data)
            y_min = min(y_data)
            y_max = max(y_data)

            self.ui.graph1.setLimits(
                xMin=x_min-0.3, xMax=x_max+0.3, yMin=y_min-0.3, yMax=y_max+0.3)

            self.ui.graph1.autoRange()

    def generate_mixer(self):
        if self.preparing_signal is not None:
            self.signals.append(self.preparing_signal)
            self.preparing_signal.generate_signal()
            self.ui.attrList.clear()
            self.add_to_signalsList(self.preparing_signal)
            self.preparing_signal = None

        # Select the last row in signalsList
        self.current_signal = self.signals[-1]
        self.handle_last_index()

        self.ui.actualRadio.setChecked(True)
        self.set_sample_sliders()
        self.set_noise_sliders()
        self.add_noise(self.current_signal)
        self.plot_mixed_signals(self.current_signal)
        self.plot_error(self.current_signal)

    def add_to_signalsList(self, signal):

        text = signal.name

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color:black;background: rgba(74, 74, 74, 0); font-family:opensans;font-weight: 500;")
        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.png"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_signalsList(signal))

        layout.addWidget(icon_button)
        layout.addWidget(label)
        custom_widget.setLayout(layout)

        # Create a QListWidgetItem and set the custom widget as the display widget
        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.ui.signalsList.addItem(item)
        self.ui.signalsList.setItemWidget(item, custom_widget)

    def delete_from_signalsList(self, signal):
        for sig in self.signals:
            if signal == sig:
                if self.current_signal == signal:
                    self.signals.remove(signal)
                    if len(self.signals) == 0:
                        self.current_signal = None
                        self.ui.componList.clear()
                    else:
                        self.current_signal = self.signals[-1]
                        self.handle_last_index()
                else:
                    self.signals.remove(signal)
        self.update_signalsList()

    def update_signalsList(self):
        self.ui.signalsList.clear()
        if self.current_signal:
            for signal in self.signals:
                self.add_to_signalsList(signal)
            self.handle_last_index()

    def handle_selected_signal(self):
        self.ui.graph1.clear()
        self.ui.graph2.clear()
        self.ui.graph3.clear()
        selected_signal = self.get_selected_signal()
        self.current_signal = selected_signal
        if self.current_signal:
            self.set_sample_sliders()
            self.set_noise_sliders()
            self.add_noise(self.current_signal)
            self.plot_mixed_signals(self.current_signal)
            self.plot_error(self.current_signal)
            self.add_to_componList()

    def add_to_componList(self):
        self.ui.componList.clear()
        for component in self.current_signal.components:
            text = str(component)
            custom_widget = QWidget()
            layout = QHBoxLayout()

            label = QLabel(text)
            label.setStyleSheet("color:black; background: rgba(74, 74, 74, 0); font-family:opensans;font-weight: 500;")
            icon_button = QPushButton()
            # Set the path to your icon file
            icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.png"))
            icon_button.setStyleSheet("background-color:transparent")
            icon_button.clicked.connect(
                lambda: self.delete_from_componList(component))

            layout.addWidget(icon_button)
            layout.addWidget(label)
            custom_widget.setLayout(layout)

            # Create a QListWidgetItem and set the custom widget as the display widget
            item = QListWidgetItem()
            item.setSizeHint(custom_widget.sizeHint())
            self.ui.componList.addItem(item)
            self.ui.componList.setItemWidget(item, custom_widget)

    def get_selected_signal(self):
        selected_item = self.ui.signalsList.currentItem()

        if selected_item:
            # Get the custom widget associated with the selected item
            custom_widget = self.ui.signalsList.itemWidget(selected_item)

            # Assuming the label is the first child of the custom widget
            label = custom_widget.findChild(QLabel)

            if label:
                signal_name = label.text()
                # Find the signal object with the matching name
                for signal in self.signals:
                    if signal.name == signal_name:
                        return signal  # Return the selected signal

    def delete_from_componList(self, component):
        self.current_signal.delete_component_after_preparing(component)
        self.handle_selected_signal()
        if self.current_signal.components == []:
            self.delete_from_signalsList(self.current_signal)

        else:
            self.update_componList()

    def update_componList(self):
        self.ui.componList.clear()

        self.add_to_componList()

    def handle_sample_sliders(self):
        self.updateCurrentValueLabel()
        if self.sliders_init1:  # the first call is always a set up
            self.sliders_init1 = False  # suppress the calling
        else:  # any further calling will be adjusting
            self.update_sample_sliders()

    def update_sample_sliders(self):
        self.current_signal.change_sample_rate(
            int(self.ui.sampleSlider.value()))
        self.add_noise(self.current_signal)
        self.plot_mixed_signals(self.current_signal)
        self.plot_error(self.current_signal)

    def set_sample_sliders(self):
        # flag for setting the sliders only, it has nothing to do with update
        self.sliders_init1 = True
        if self.current_signal == None:
            return
        elif self.current_signal.sampling_mode == 0:
            self.ui.fmaxLabel.setText("4Fmax")
            self.ui.actualRadio.setChecked(True)
            self.ui.sampleSlider.setMinimum(1)
            self.ui.sampleSlider.setMaximum(
                # handle_sliders is called() due to the connection, and i want to suppress this calling
                int(self.current_signal.maxFreq * 4))
            self.ui.sampleSlider.setValue(int(self.current_signal.sample_rate))
            self.ui.sampleSlider.setSingleStep(1)
            self.ui.startLabel.setText("1")
            self.ui.endLabel.setText(str(int(self.current_signal.maxFreq * 4)))
        else:
            self.ui.fmaxLabel.setText("")
            self.ui.normalRadio.setChecked(True)
            self.ui.sampleSlider.setMinimum(self.current_signal.maxFreq)
            self.ui.sampleSlider.setMaximum(self.current_signal.maxFreq * 4)
            self.ui.sampleSlider.setSingleStep(self.current_signal.maxFreq)
            self.ui.startLabel.setText("Max freq")
            self.ui.endLabel.setText(f"4 Max freq")
        self.sliders_init1 = False

    def handle_noise_sliders(self):
        self.updateCurrentValueLabel()
        if self.sliders_init2:  # the first call is always a set up
            self.sliders_init2 = False  # suppress the calling
        else:  # any further calling will be adjusting
            self.update_noise_sliders()


# #405cf5

    def update_noise_sliders(self):
        self.current_signal.change_snr(
            int(self.ui.noiseSlider.value()))
        self.add_noise(self.current_signal)
        self.plot_mixed_signals(self.current_signal)
        self.plot_error(self.current_signal)

    def set_noise_sliders(self):
        # flag for setting the sliders only, it has nothing to do with update
        self.sliders_init2 = True
        if self.current_signal == None:
            return
        else:
            self.ui.noiseSlider.setMinimum(1)
            self.ui.noiseSlider.setMaximum(100)
            self.ui.noiseSlider.setValue(
                int(self.current_signal.snr))
            self.ui.noiseSlider.setSingleStep(1)
        self.sliders_init2 = False

    def updateCurrentValueLabel(self):
        current_value = self.ui.sampleSlider.value()
        snr_value = self.ui.noiseSlider.value()
        if self.current_signal == None:
            return
        else:
            self.ui.snrLabel.setText(f"SNR Value: {snr_value}")
            if self.current_signal.sampling_mode == 0:
                self.ui.indicatLabel.setText(f"Current Value: {current_value}")
            else:
                self.ui.indicatLabel.setText(
                    f"Current Value: {current_value // self.current_signal.maxFreq}F_max")

    def radioToggled(self):
        if self.current_signal == None:
            return
        else:
            if self.ui.actualRadio.isChecked():
                self.current_signal.change_sampling_mode(0)
                self.set_sample_sliders()
                self.updateCurrentValueLabel()

            else:
                self.current_signal.change_sampling_mode(1)
                self.set_sample_sliders()
                self.updateCurrentValueLabel()

    def download_signal(self):
        self.folder_path, _ = QFileDialog.getSaveFileName(
            # Use .csv extension for CSV files
            None, 'Save the signal file', None, 'CSV Files (*.csv)')

        signal = self.current_signal
        df = pd.DataFrame(
            {"X": signal.time, "Y": signal.data, "fmax": signal.maxFreq})

        if self.folder_path:
            # Check if a file path was selected
            df.to_csv(self.folder_path, index=False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
