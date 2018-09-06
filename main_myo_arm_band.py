# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 18:41:21 2018

Myo arm band project

développement sous Windows 10, python 3.6

@author: chalgand

"""

__author__ = "Christophe Halgand, Effie Ségas"
__copyright__ = "Copyright 2017, The HYRBID Python formation Project"
__version__ = "1.0.0"
__maintainer__ = "Christophe H."
__email__ = "christophe.halgand@u-bordeaux.fr"
__status__ = "Stable"


import os
import pandas as pd
import qdarkstyle
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import myo
from module_myo import my_myo_arm_band
from ui_src import ui_diagnostics_myo as ihm

# pour rendre l'application en fond noir
os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
APP = pg.mkQApp()
QDARK = qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph=True)
APP.setStyleSheet(QDARK)


class MainWindow(QtGui.QMainWindow, ihm.Ui_MainWindow):
    """
    fenêtre principale dessinée sur QtDesigner décomposée en trois QTabWidget

    1. la première permet de savoir :

        a) si le myo arm est connecté
        b) quel est le niveau de batterie
        c) si le myo arm est vérrouillé
        d) si le signal bluetooth est de bonne qualité
        e) quel est le numéro des électrodes
        f) et permet de faire vibrer le bracelet

    2. la deuxième permet de voir le signal brut de l'EMG en live

    3. la troisième permet de voir les données de la centrale inertielle

        a) orientation
        b) gyroscope
        c) accéléromètre

    """

    def __init__(self):
        super(MainWindow, self).__init__()
        # définition de tous les attributs
        self.p_gyro1 = None
        self.p_gyro2 = None
        self.p_gyro3 = None
        self.p_orix = None
        self.p_oriy = None
        self.p_oriz = None
        self.p_acc1 = None
        self.p_acc2 = None
        self.p_acc3 = None
        self.p_emg1 = None
        self.p_emg2 = None
        self.p_emg3 = None
        self.p_emg4 = None
        self.p_emg5 = None
        self.p_emg6 = None
        self.p_emg7 = None
        self.p_emg8 = None
        self.p_bluetooth = None
        self.data_emg = None
        self.data_acc = None
        self.data_gyro = None
        self.data_ori = None
        self.data = None
        self.data_tot = None
        # Create the main window
        self.setupUi(self)  # lance le montage des objets graphiques
        self.nb_value = 1000  # nombre de valeurs EMG sur le graph
        # chemin d'enregistrement des données
        self.path_doc = os.path.join(os.getcwd(), 'data')
        self.on_init()  # lance la méthode de personnalisation de l'interface
        self.show()  # montre l'interface
        self.init_connection()  # lance le timer Qt pour visualiser les données
        # change le titre de la fenêtre en fonction du nom du myo arm
        # nom modifiable dans l'application 'Myo Connect'
        self.setWindowTitle(f'Myo : {self.listener.device_name}')

    def on_init(self):
        """
        méthode appelée dans le constructeur de la classe

        permet de personaliser le fonctionnement de l'interface
        """
        # adresse de la racine des fichiers de ressources
        # pour la reconnaissance des poses
        racine = "image: url(:/gesture/images/gesture_"
        # création d'un dictionnaire pour faciliter l'appel
        self.path_im = {'fist': racine + "fist.png);",
                        'fist_on': racine + "fist_on.png);",
                        'wave_in': racine + "wave_in.png);",
                        'wave_in_on': racine + "wave_in_on.png);",
                        'wave_out': racine + "wave_out.png);",
                        'wave_out_on': racine + "wave_out_on.png);",
                        'spread': racine + "spread.png);",
                        'spread_on': racine + "spread_on.png);"}
        self.init_data()  # méthode de création des DataFrame
        self.init_plot()  # méthode de préparation des tracés
        # signal/slot pour faire vibrer le myo arm
        self.pb_vib_long.clicked.connect(self.vibration_long)
        self.pb_vib_medium.clicked.connect(self.vibration_medium)
        self.pb_vib_short.clicked.connect(self.vibration_short)

    def vibration_long(self):
        """
        méthode qui génère une vibration longue
        """
        self.listener.device.vibrate(myo.VibrationType.long)

    def vibration_medium(self):
        """
        méthode qui génère une vibration moyenne
        """
        self.listener.device.vibrate(myo.VibrationType.medium)

    def vibration_short(self):
        """
        méthode qui génère une vibration courte
        """
        self.listener.device.vibrate(myo.VibrationType.short)

    def init_connection(self):
        """
        lance un timer toutes les 20ms pour récupérer les données
        """
        # permet de charger la librairie du myo
        myo.init(sdk_path=os.path.join(os.getcwd(),
                                       'myo-sdk-win-0.9.0'))
        # connection à un myo
        self.hub = myo.Hub()
        # connection à une classe en écoute du myo
        self.listener = my_myo_arm_band.MyListener()
        self.startTimer(0.02)

    def init_plot(self):
        """
        initialise les tracés pour permettre l'affichage dynamique des données
        """
        # pour les données du gyroscope
        self.p_gyro1 = self.gv_gyro.plot(pen=(255, 0, 0))
        self.p_gyro2 = self.gv_gyro.plot(pen=(0, 255, 0))
        self.p_gyro3 = self.gv_gyro.plot(pen=(0, 0, 255))

        # pour les données d'orientation
        self.p_orix = self.gv_ori.plot(pen=(255, 0, 0))
        self.p_oriy = self.gv_ori.plot(pen=(0, 255, 0))
        self.p_oriz = self.gv_ori.plot(pen=(0, 0, 255))

        # pour les données de l'accéléromètre
        self.p_acc1 = self.gv_acc.plot(pen=(255, 0, 0))
        self.p_acc2 = self.gv_acc.plot(pen=(0, 255, 0))
        self.p_acc3 = self.gv_acc.plot(pen=(0, 0, 255))

        # pour les données des sEMG
        self.p_emg1 = self.gv_emg_1.plot()
        self.p_emg2 = self.gv_emg_2.plot()
        self.p_emg3 = self.gv_emg_3.plot()
        self.p_emg4 = self.gv_emg_4.plot()
        self.p_emg5 = self.gv_emg_5.plot()
        self.p_emg6 = self.gv_emg_6.plot()
        self.p_emg7 = self.gv_emg_7.plot()
        self.p_emg8 = self.gv_emg_8.plot()

        # échelle des ordonnées fixées
        self.gv_emg_1.setYRange(-128, 128)
        self.gv_emg_2.setYRange(-128, 128)
        self.gv_emg_3.setYRange(-128, 128)
        self.gv_emg_4.setYRange(-128, 128)
        self.gv_emg_5.setYRange(-128, 128)
        self.gv_emg_6.setYRange(-128, 128)
        self.gv_emg_7.setYRange(-128, 128)
        self.gv_emg_8.setYRange(-128, 128)

        # pour les données de la qualité du signal
        self.p_bluetooth = self.gv_bluetooth.plot()
        # échelle de 0 à 100 %
        self.gv_bluetooth.setYRange(0, 100)

    def init_data(self):
        """
        création de 5 dataframes qui
        permettront l'ajout dynamique des données
        avec un timestamp
        """
        self.data_emg = pd.DataFrame(columns=('timestamp',
                                              'emg1', 'emg2', 'emg3', 'emg4',
                                              'emg5', 'emg6', 'emg7', 'emg8'))

        self.data_acc = pd.DataFrame(columns=('timestamp',
                                              'acc1', 'acc2', 'acc3'))

        self.data_gyro = pd.DataFrame(columns=('timestamp',
                                               'gyro1', 'gyro2', 'gyro3'))

        self.data_ori = pd.DataFrame(columns=('timestamp',
                                              'orix', 'oriy', 'oriz', 'oriw'))

        self.data = pd.DataFrame(columns=('data_acc', 'data_gyro',
                                          'data_ori', 'data_emg'))

    def gestion_data(self, data_acc, data_gyro, data_ori, data_emg):
        """
        ajout dynamique des données dans les dataframe
        """
        for timestamp, (acc1, acc2, acc3) in data_acc:
            self.data_acc = self.data_acc.append({'timestamp': timestamp,
                                                  'acc1': acc1,
                                                  'acc2': acc2,
                                                  'acc3': acc3},
                                                 ignore_index=True)

        for timestamp, (gyro1, gyro2, gyro3) in data_gyro:
            self.data_gyro = self.data_gyro.append({'timestamp': timestamp,
                                                    'gyro1': gyro1,
                                                    'gyro2': gyro2,
                                                    'gyro3': gyro3},
                                                   ignore_index=True)

        for timestamp, (orix, oriy, oriz, oriw) in data_ori:
            self.data_ori = self.data_ori.append({'timestamp': timestamp,
                                                  'orix': orix,
                                                  'oriy': oriy,
                                                  'oriz': oriz,
                                                  'oriw': oriw},
                                                 ignore_index=True)

        for timestamp, (emg1, emg2, emg3, emg4,
                        emg5, emg6, emg7, emg8) in data_emg:
            self.data_emg = self.data_emg.append({'timestamp': timestamp,
                                                  'emg1': emg1,
                                                  'emg2': emg2,
                                                  'emg3': emg3,
                                                  'emg4': emg4,
                                                  'emg5': emg5,
                                                  'emg6': emg6,
                                                  'emg7': emg7,
                                                  'emg8': emg8},
                                                 ignore_index=True)

    def maj_plot(self):
        """
        mise à jour des graphiques avec les dernières nb_value
        """
        self.p_acc1.setData(self.data_acc['acc1'].values[-self.nb_value:])
        self.p_acc2.setData(self.data_acc['acc2'].values[-self.nb_value:])
        self.p_acc3.setData(self.data_acc['acc3'].values[-self.nb_value:])

        self.p_gyro1.setData(self.data_gyro['gyro1'].values[-self.nb_value:])
        self.p_gyro2.setData(self.data_gyro['gyro2'].values[-self.nb_value:])
        self.p_gyro3.setData(self.data_gyro['gyro3'].values[-self.nb_value:])

        self.p_orix.setData(self.data_ori['orix'].values[-self.nb_value:])
        self.p_oriy.setData(self.data_ori['oriy'].values[-self.nb_value:])
        self.p_oriz.setData(self.data_ori['oriz'].values[-self.nb_value:])

        self.p_emg1.setData(self.data_emg['emg1'].values[-self.nb_value:])
        self.p_emg2.setData(self.data_emg['emg2'].values[-self.nb_value:])
        self.p_emg3.setData(self.data_emg['emg3'].values[-self.nb_value:])
        self.p_emg4.setData(self.data_emg['emg4'].values[-self.nb_value:])
        self.p_emg5.setData(self.data_emg['emg5'].values[-self.nb_value:])
        self.p_emg6.setData(self.data_emg['emg6'].values[-self.nb_value:])
        self.p_emg7.setData(self.data_emg['emg7'].values[-self.nb_value:])
        self.p_emg8.setData(self.data_emg['emg8'].values[-self.nb_value:])

        self.p_bluetooth.setData(self.listener.rssi_data_queue)

    def read_imu_paquet(self):
        """
        lecture des données dernièrement acquises
        """
        data_acc = self.listener.get_acceleration_data()
        data_gyro = self.listener.get_gyroscope_data()
        data_ori = self.listener.get_orientation_data()
        data_emg = self.listener.get_emg_data()

        self.gestion_data(data_acc, data_gyro, data_ori, data_emg)

    def timerEvent(self, _):
        """
        méthode appelée toutes les 20ms
        pour récupérer les données et quelques informations
        """
        self.hub.run(self.listener.on_event, 20)
        self.listener.device.request_rssi()  # force du signal bluetooth
        self.read_imu_paquet()  # dernières données acquises
        self.maj_plot()  # mise à jour des tracés
        # mise à jour de la bar de progression informant du niveau de batterie
        self.pb_battery.setValue(self.listener.battery_level)
        # modification du label "connect" pour informer si un myo arm l'est
        if self.listener.connected:
            self.lab_connect.setText('CONNECTED')
        else:
            self.lab_connect.setText('DISCONNECTED')
        # modification du label "lock" pour informer si un myo l'est
        if self.listener.locked:
            self.lab_lock.setText('isLOCKED')
        else:
            self.lab_lock.setText('isUNLOCKED')
        # récupération de la pose détectée et mise à jour de l'image
        # pour en informer l'utilisateur
        if self.listener.pose == myo.Pose.rest:
            self.lab_fist.setStyleSheet(self.path_im['fist'])
            self.lab_spread.setStyleSheet(self.path_im['spread'])
            self.lab_wave_out.setStyleSheet(self.path_im['wave_out'])
            self.lab_wave_in.setStyleSheet(self.path_im['wave_in'])
        elif self.listener.pose == myo.Pose.fist:
            self.lab_fist.setStyleSheet(self.path_im['fist_on'])
        elif self.listener.pose == myo.Pose.wave_in:
            self.lab_wave_in.setStyleSheet(self.path_im['wave_in_on'])
        elif self.listener.pose == myo.Pose.wave_out:
            self.lab_wave_out.setStyleSheet(self.path_im['wave_out_on'])
        elif self.listener.pose == myo.Pose.fingers_spread:
            self.lab_spread.setStyleSheet(self.path_im['spread_on'])
#        elif self.listener.pose == myo.Pose.double_tap:
#            print('pose : double_tap')

    def enregistrement(self):
        """
        enregistrement des données dans un fichier \*.csv
        """
        filepath = os.path.join(self.path_doc, 'none')
        (path,
         oki) = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QWidget(),
                                                      'Backup Configuration',
                                                      filepath,
                                                      'CSV(*.csv)')
        if oki:
            self.data = self.data.append({'data_acc': self.data_acc,
                                          'data_gyro': self.data_gyro,
                                          'data_ori': self.data_ori,
                                          'data_emg': self.data_emg},
                                         ignore_index=True)
            try:
                self.data_tot = self.data.to_csv(path, mode='w', header=None)
            except PermissionError:
                QtWidgets.QMessageBox.warning(QtWidgets.QWidget(),
                                              "Enregistrement annulé",
                                              ("Accès refusé : vérifiez que"
                                               "le fichier que vous voulez "
                                               "écraser n'est pas ouvert."),
                                              QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(QtWidgets.QWidget(),
                                          "Enregistrement annulé",
                                          ("Les données n'ont pas été "
                                           "enregistrées."),
                                          QtWidgets.QMessageBox.Ok)

    def closeEvent(self, event):
        """
        ajoute une boite de dialogue pour confirmation de fermeture
        """
        result = QtGui.QMessageBox.question(self,
                                            "Confirm Exit...",
                                            "Do you want to exit ?",
                                            (QtGui.QMessageBox.Yes |
                                             QtGui.QMessageBox.No))
        if result == QtGui.QMessageBox.Yes:
            # permet d'ajouter du code pour fermer proprement
            self.hub.stop()
            self.enregistrement()
            event.accept()

        else:
            event.ignore()


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    WIN = MainWindow()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    # attention, l'utilisation de la méthode hub.run oblige un appel à chaque
    # fois que l'on souhaite récupérer des données
    # run_in_background lance dans un thread à part la communication
    # avec un myo
