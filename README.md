🎯 Virtual Mouse 

✨ Description
Virtual Mouse Controller (VMC) est un projet innovant permettant de contrôler votre souris uniquement avec vos mains, via webcam 🖐️💻.
Plus besoin de souris physique : déplacez le curseur, cliquez, scrollez et verrouillez votre écran grâce à des gestes naturels.
L’application est conçue pour être fluide, réactive, et avec une interface moderne et esthétique 🎨.
🚀 Fonctionnalités principales
Détection en temps réel avec MediaPipe Hands
Suivi fluide du curseur grâce à un filtre de Kalman 1D
Clic gauche/droit, scroll vertical, lock d’écran via gestes
Interface PyQt6 moderne, thème sombre, dégradés animés 🌈
Optimisé pour Mac et Windows (fichiers .app et .exe à venir)
Compatibilité multi-main (gauche/droite)
🖐️ Gestes supportés
Geste	Action
🖖 Index levé (main droite)	Déplacer le curseur
🤏 Pincement main droite	Clic gauche
🤏 Pincement main gauche	Clic droit
✊ Poing droit	Scroll bas
✊ Poing gauche	Scroll haut
🖕 Majeur levé	Lock / Fermer application active
✋ Tous doigts fermés	Scroll automatique si stable
✅ Chaque geste a été calibré pour fluidité et précision, avec un dead zone et lissage via Kalman.
🖥️ Interface
Fenêtre compacte et moderne : 400x450px
Vidéo webcam intégrée avec bordure arrondie et ombre
Dégradé animé en arrière-plan 🌈
Boutons Start/Stop avec icône et animation
Labels d’information pour les gestes avec tooltip
Footer discret pour copyright
📸 Screenshots
(À ajouter : prenez quelques captures d’écran de l’interface en action)
Exemple du curseur contrôlé avec la main
Menu et info gestes visibles
Animation du dégradé
⚙️ Installation
Prérequis
Python ≥ 3.11 🐍
Modules nécessaires :
pip install opencv-python mediapipe pyautogui PyQt6 numpy
Lancer le projet
python main.py
⚠️ Mac Users : autorisez l’accès à la webcam et aux commandes souris dans Préférences Système → Sécurité et confidentialité → Accessibilité.
🖱️ Version compilée
Une version prête à l’emploi sera prochainement disponible :
Mac : VirtualMouse.app 🍏
Windows : VirtualMouse.exe 🪟
🔗 Téléchargement prévu sur le site officiel VMC (à venir).
⚙️ Configuration avancée
Ajustez la sensibilité non-linéaire dans main.py via la fonction sensibilité_non_lin()
Modifiez les paramètres Kalman pour lisser plus ou moins le curseur
Personnalisez le delay du clic et le dead zone pour votre confort
💡 Astuces d’utilisation
Placez-vous dans un environnement bien éclairé 🌞
Gardez vos mains visibles et stables devant la caméra
Patientez 1-2 secondes pour que le curseur se stabilise
Évitez de couvrir la caméra pour des mouvements précis
👨‍💻 Auteur
Mascret Clément
Passionné d’IA et de UX gestuelle
Projet open-source avec vision innovation et accessibilité ✨
🤝 Contribution
Contributions bienvenues !
Signalez des bugs 🐛
Proposez des nouveaux gestes ou animations ✨
Partagez vos améliorations sur GitHub
📜 License
Ce projet est sous MIT License
Libre de l’utiliser, modifier et partager, mention obligatoire de l’auteur.
🔜 Roadmap
✅ Détection curseur et clics
✅ Scroll vertical
✅ Lock avec majeur levé
🔜 Versions .app et .exe
🔜 Gestes avancés (drag & drop, zoom, multi-curseurs)
🔜 Interface multi-langue 🌍
🏷️ Tags
#VirtualMouse #HandTracking #Gestures #PyQt6 #MediaPipe #Python #OpenSource #VMC
