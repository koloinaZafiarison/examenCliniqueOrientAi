# Guide de Configuration et Lancement - OrientAi (Backend & Frontend)

Ce guide décrit l'ensemble des étapes nécessaires pour configurer, lancer et exécuter le projet **OrientAi** (Backend FastAPI et Frontend Next.js) sous Windows (PowerShell).

---

## 1. Configuration et Lancement du Backend (FastAPI)

1. Ouvrez un terminal PowerShell et placez-vous à la racine du projet :
   ```powershell
   cd D:\Koloina\examenCliniqueOrientAi
   ```

2. Créez et activez l'environnement virtuel Python :
   ```powershell
   python -m venv backend/venv
   .\backend\venv\Scripts\Activate.ps1
   ```

3. Installez les dépendances Python :
   ```powershell
   python -m pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```

4. Créez un fichier **`backend/.env`** (encodé en UTF-8) avec le contenu suivant :
   ```env
   GEMINI_API_KEY=votre_cle_api_gemini
   GEMINI_MODEL=gemini-3.5-flash-lite
   DATABASE_URL=postgresql://postgres:votre_mot_de_passe@localhost:5432/OrientAi
   ```
   *(Assurez-vous que la base de données `OrientAi` existe dans votre instance PostgreSQL).*

5. Lancez le serveur FastAPI via Uvicorn :
   ```powershell
   cd backend
   python -m uvicorn app:app --reload
   ```
   * **API Backend :** `http://127.0.0.1:8000`
   * **Documentation Swagger :** `http://127.0.0.1:8000/docs`

---

## 2. Configuration et Lancement du Frontend (Next.js)

1. Ouvrez un **nouveau terminal PowerShell** et placez-vous dans le dossier frontend :
   ```powershell
   cd D:\Koloina\examenCliniqueOrientAi\frontend
   ```

2. Installez les dépendances Node.js (via `pnpm`) :
   ```powershell
   pnpm install
   ```

3. Créez (si nécessaire) un fichier **`frontend/.env.local`** pour pointer vers le backend :
   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
   ```

4. Lancez le serveur de développement frontend :
   ```powershell
   pnpm dev
   ```
   * **Interface Frontend :** `http://127.0.0.1:3000`
