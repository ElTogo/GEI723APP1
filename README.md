La première couche du réseau est ControlStimuliExterne.

Elle sert à affecter les entré désiré selon les stimuli des capteurs sur les flancs du robots.

Elle se connecte par la sortie des capteurs par taux de décharge, et se connecte au entré de StateMachine

La deuxième partie du réseau sert à choisir la séquence de la locomotion. En d'autre mots, la state machine. 

La couche States représente les nœuds du graphe avec compétition winner-take-all via inhibition mutuelle. Un seul état reçoit un courant actif élevé, les autres restent inactifs. 
Elle se connecte aux synapses directionnelles en entrée et à Motor en sortie.

La couche CPG génère des impulsions rythmiques périodiques pour maintenir l'activité de l'état actif entre les transitions. 
Seul le CPG correspondant à l'état actif est activé, se connecte à States pour créer une excitation continue.

La couche Motor décode chaque état en patron moteur spécifique de douze bits via connectivité fixe selon une table de correspondance prédéfinie. 
Dynamique rapide pour réagir immédiatement aux changements d'états, reçoit de States par taux de décharge.

Les synapses directionnelles créent quatre chemins possibles selon la topologie du graphe à quatorze nœuds. 
Elles sont activées seulement si les commandes correspondantes dépassent un seuil défini, permettant les transitions contrôlées entre états adjacents.

Le Timer génère des signaux de tick périodiques qui déclenchent les transitions à intervalles réguliers en envoyant un boost à tous les états. 
Les commandes directionnelles montent instantanément et décroissent exponentiellement pour créer des fenêtres temporelles d'activation des chemins.

Les deux dernière couches du réseau sont ControlHorizontal et ControlVertical. Ils sont mis en commun dans UnitaryLegControl pour instancier via des objets. 

Elles servent à controler les actuateurs des jambes de l'hexapod, en actionnant des fléchisseur et des extenseur verticaux et horizontaux.

Elle se connecte à la sortie de Decoder, et se connecte au actuateurs selon en encodage par taux de décharge.

Les codes unitaires servent à la visualisation du fonctionnement, la classe sert à instancier le code N fois dans un système.

