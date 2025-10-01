🎯 Virtual Mouse Controller (VMC)
<p align="center"> <img src="https://i.imgur.com/2jvQ9Mh.png" alt="VMC Demo" width="600"/> </p>
✨ Description
Virtual Mouse Controller (VMC) est un logiciel révolutionnaire qui vous permet de contrôler votre souris uniquement avec vos mains 🖐️💻.
Avec VMC :
Déplacez le curseur avec votre index levé
Effectuez un clic gauche/droit par pincement
Scrollez verticalement avec un poing fermé
Verrouillez l’écran avec le majeur levé 🖕
Le tout avec une interface moderne, animations fluides, et dégradés colorés 🌈.
<details> <summary>🚀 Fonctionnalités principales</summary>
🔹 Détection en temps réel avec MediaPipe Hands
🔹 Suivi fluide du curseur via un filtre de Kalman 1D
🔹 Gestes intelligents pour clics, scroll et lock
🔹 Interface PyQt6 moderne, thème sombre et animations
🔹 Compatible Mac et Windows (fichiers .app et .exe bientôt disponibles)
🔹 Optimisé pour multi-main (gauche/droite)
</details>
<details> <summary>🖐️ Gestes supportés</summary>
Geste	Action
🖖 Index levé (main droite)	Déplacer le curseur
🤏 Pincement main droite	Clic gauche
🤏 Pincement main gauche	Clic droit
✊ Poing droit	Scroll bas
✊ Poing gauche	Scroll haut
🖕 Majeur levé	Lock / Fermer application active
✋ Tous doigts fermés	Scroll automatique si main stable
</details>
<details> <summary>🖥️ Interface</summary>
Fenêtre compacte : 400x450px
Vidéo webcam intégrée avec bordure arrondie et ombre
Dégradé animé en arrière-plan 🌈
Boutons Start/Stop avec icône et animation
Labels et info gestes interactifs 💡
Footer discret avec copyright
</details>
<details> <summary>📸 Screenshots</summary>
(Ajoutez vos images ici)
Curseur contrôlé par la main
Menu et info gestes visibles
Animation du dégradé
<p align="center"> <img src="https://i.imgur.com/k7b5aF5.png" width="400"/> <img src="https://i.imgur.com/9bC9m7p.png" width="400"/> </p> </details>
<details> <summary>⚙️ Installation</summary>
Prérequis
Python ≥ 3.11 🐍
Modules nécessaires :
pip install opencv-python mediapipe pyautogui PyQt6 numpy
Lancer le projet
python main.py
⚠️ Mac Users : autorisez l’accès à la webcam et aux commandes souris dans Préférences Système → Sécurité et confidentialité → Accessibilité.
</details>
<details> <summary>🖱️ Version compilée</summary>
Prochainement disponible :
Mac : VirtualMouse.app 🍏
Windows : VirtualMouse.exe 🪟
🔗 Téléchargement prévu sur notre site officiel VMC (à venir).
</details>
<details> <summary>⚙️ Configuration avancée</summary>
Ajustez la sensibilité non-linéaire via sensibilité_non_lin()
Modifiez les paramètres Kalman pour lisser plus ou moins le curseur
Personnalisez le delay du clic et le dead zone pour votre confort
</details>
<details> <summary>💡 Astuces</summary>
Placez-vous dans un environnement bien éclairé 🌞
Gardez vos mains visibles et stables devant la caméra
Patientez 1-2 secondes pour stabiliser le curseur
Évitez de couvrir la caméra pour des mouvements précis
</details>
<details> <summary>👨‍💻 Auteur</summary>
Mascret Clément
Passionné par l’IA et l’interaction naturelle ordinateur-utilisateur
Projet open-source ✨
</details>
<details> <summary>🤝 Contribution</summary>
Contributions bienvenues :
🐛 Signalez des bugs
✨ Proposez de nouveaux gestes ou animations
📂 Partagez vos améliorations sur GitHub
</details>
<details> <summary>📜 License</summary>
Ce projet est sous MIT License
Libre d’utilisation, modification et partage, mention obligatoire de l’auteur.
</details>
<details> <summary>🔜 Roadmap</summary>
✅ Détection curseur et clics
✅ Scroll vertical
✅ Lock avec majeur levé
🔜 Versions .app et .exe
🔜 Gestes avancés : drag & drop, zoom, multi-curseurs
🔜 Interface multi-langue 🌍
</details>
🏷️ Tags
#VirtualMouse #HandTracking #Gestures #PyQt6 #MediaPipe #Python #OpenSource #VMC
