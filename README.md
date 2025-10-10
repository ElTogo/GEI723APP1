La première couche du réseau est ControlStimuliExterne.

Elle sert à affecter les entré désiré selon les stimuli des capteurs sur les flancs du robots.

Elle se connecte par la sortie des capteurs par taux de décharge, et se connecte au entré de StateMachine





Les deux dernière couches du réseau sont ControlHorizontal et ControlVertical. Ils sont mis en commun dans UnitaryLegControl pour instancier via des objets. 

Elles servent à controler les actuateurs des jambes de l'hexapod, en actionnant des fléchisseur et des extenseur verticaux et horizontaux.

Elle se connecte à la sortie de Decoder, et se connecte au actuateurs selon en encodage par taux de décharge.

Les codes unitaires servent à la visualisation du fonctionnement, la classe sert à instancier le code N fois dans un système.

