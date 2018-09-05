# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 18:12:10 2018

Ce code permet de récupérer un maximum d'informations issues d'un myo arm

@author: chalgand
"""

from collections import deque
from threading import Lock
import myo


class MyListener(myo.DeviceListener):
    """
    classe en écoute d'un myo
    """
    def __init__(self, queue_size=8):
        self.lock = Lock()  # verrouille le thread pour lecture des donnees
        # création de listes optimisées pour seulement ajouter des éléments
        self.emg_data_queue = deque(maxlen=queue_size)
        self.orientation_data_queue = deque(maxlen=queue_size)
        self.acceleration_data_queue = deque(maxlen=queue_size)
        self.gyroscope_data_queue = deque(maxlen=queue_size)
        self.rssi_data_queue = deque(maxlen=100)
        # initialisation d'attribut
        self.pose = myo.Pose.rest  # pose quelconque
        self.connected = False  # non connecté
        self.battery_level = 100  # niveau de batterie maximal
        self.emg_enabled = False  # on acquiert pas les EMG
        self.locked = False  # myo non vérouillé
        self.rssi = None  # aucune valeur de force du signal bluetooth
        self.emg = None  # données null des emg
        self.device_name = None  # pas de nom du myo
        self.device = None
        self.myo_firmware = None
        self.arm = None
        self.x_direction = None

    def on_paired(self, event):
        """
        méthode appelée si le myo est appareillé
        """
        if __name__ == '__main__':
            print('paired')
        else:
            pass

    def on_unpaired(self, event):
        """
        méthode appelée si le myo n'est plus appareillé
        """
        if __name__ == '__main__':
            print('unpaired')
        else:
            pass

    def on_connected(self, event):
        """
        méthode appelé si le myo est connecté
        """
        self.device = event.device  # sauvegarde de l'instance au myo arm
        event.device.unlock()  # demande de desappareiller
        event.device.lock()  # demande d'appareiller (génère des vibrations)
        event.device.stream_emg(True)  # lance l'acquisition des emg
        self.connected = True  # mise à jour du flag de connection du myo
        self.device_name = event.device_name  # on récupère le petit nom du myo
        # on récupère également le numéro du firmware (non exploité dans l'UI)
        self.myo_firmware = '.'.join(map(str, event.firmware_version[:-1]))

    def on_disconnected(self, event):
        """
        méthode appelée si le myo est déconnecté
        """
        self.connected = False  # flag mis à jour

    def on_arm_synced(self, event):
        """
        méthode appelé si un bras est synchronisé
        pas vraiment compris !!!
        """
        self.arm = event.arm  # informe de la latéralité du bras détecté
        # informe de l'orientation du bracelet
        # (vers le poignet ou vers le coude)
        self.x_direction = event.x_direction
        if __name__ == '__main__':
            print(self.x_direction)
        else:
            pass

    def on_arm_unsynced(self, event):
        """
        méthode appelée si le bras est désynchronisé
        pas vraiment compris !!!
        """
        if __name__ == '__main__':
            print(f'arm unsynced : {event.arm}')
        else:
            pass

    def on_unlocked(self, event):
        """
        méthode appelée si le myo est dévérouillé
        """
        self.locked = False  # flag mis à jour

    def on_locked(self, event):
        """
        méthode appelée si le myo est vérouillé
        """
        self.locked = True  # flag mis à jour

    def on_pose(self, event):
        """
        méthode appelée dès qu'une pose gestuelle est reconnue

            a) Spread
            b) Fist
            c) Wave in
            d) Wave out
            e) Double Tap
            f) Rest
        """
        self.pose = event.pose  # attribut mis à jour

    def on_orientation(self, event):
        """
        méthode appelée pour récupérer

            a) orientation
            b) gyroscope
            c) accéléromètre
            d) associé à un timestamp
        """
        with self.lock:
            self.orientation_data_queue.append((event.timestamp,
                                                event.orientation))
            self.gyroscope_data_queue.append((event.timestamp,
                                              event.gyroscope))
            self.acceleration_data_queue.append((event.timestamp,
                                                 event.acceleration))

    def on_rssi(self, event):
        """
        méthode appelée suite à la réponse d'une requête "request_rssi()"
        """
        with self.lock:
            # mise à jour de la liste
            self.rssi_data_queue.append(-event.rssi)

    def on_battery_level(self, event):
        """
        méthode appelée dès que le niveau de batterie évolue
        """
        self.battery_level = event.battery_level  # mise à jour de l'attribut

    def on_emg(self, event):
        """
        méthode appelée pour réceptionner les données EMG
        avec son timestamp
        """
        with self.lock:
            self.emg_data_queue.append((event.timestamp,
                                        event.emg))

    def on_warmup_completed(self, event):
        """
        méthode appelée quand le myo arm est "chaud"

        c'est à partir de ce moment que les données sont les plus stables
        mais ça reste à vérifier

        pas vraiment pris en compte dans ce code (à faire évoluer)
        """
        event.device.stream_emg(True)  # lancement de l'acquisition EMG
        self.emg_enabled = True  # mise à jour du flag

    def get_emg_data(self):
        """
        méthode pour récupérer les données EMGs
        """
        with self.lock:
            return list(self.emg_data_queue)

    def get_orientation_data(self):
        """
        méthode pour récupérer les données d'orientation
        """
        with self.lock:
            return list(self.orientation_data_queue)

    def get_gyroscope_data(self):
        """
        méthode pour récupérer les données du gyroscope
        """
        with self.lock:
            return list(self.gyroscope_data_queue)

    def get_acceleration_data(self):
        """
        méthode pour récupérer les données de l'accéléromètre
        """
        with self.lock:
            return list(self.acceleration_data_queue)


if __name__ == '__main__':
    # permet de tester sans interface graphique
    import os
    from time import sleep
    myo.init(sdk_path=os.path.join('..',
                                   os.getcwd(),
                                   'myo-sdk-win-0.9.0'))
    HUB = myo.Hub()
    LISTENER = MyListener()
    with HUB.run_in_background(LISTENER.on_event):
        while True:
            print(LISTENER.emg_data_queue)
            sleep(0.02)
