# 🏥 HMS WhatsApp Bot & Admin Dashboard

A complete **Hospital Management System (HMS)** solution combining a **WhatsApp chatbot** for patients and an intuitive **Admin Web Dashboard** for hospital staff. The bot enables appointment booking and hospital information retrieval via WhatsApp using the **Twilio API**, while the dashboard provides full administrative capabilities like managing appointments, records, and inventory.

---

## 🚀 Features

### 🤖 WhatsApp Chatbot (Patient Interface)
- 📅 Book appointments with doctors  
- ℹ️ Get hospital service information  
- 🔍 Check appointment status  
- 🧾 Access general FAQs  
- 💬 Powered by Twilio + Groq API  

### 🖥️ Admin Web Dashboard
- 👩‍⚕️ Manage doctors (Add/Edit/Delete)  
- 🗓️ View & manage patient appointments  
- 🧪 Add & manage medical records  
- 📦 Inventory management (Add/Edit/Delete stock items)  
- 👤 Patient profile management  
- 📊 Dashboard overview with quick stats (appointments, doctors, inventory)  

---

## 🛠️ Tech Stack

| Component              | Technology                         |
|------------------------|-------------------------------------|
| 💬 Chatbot             | Python, Flask, Twilio API, Groq API |
| 🗃️ Optional DB         | MySQL (online SQL-style storage) |
| 🌐 Admin Dashboard     | HTML, CSS, JavaScript, Flask Backend |
| 🔁 Integration         | REST APIs (Groq, Twilio) |
| 🔓 Tunneling (Localhost Exposure) | Ngrok                          |

---

## 🧰 Setup Instructions (Windows)

### 🔧 Prerequisites
Ensure you have:
- Python 3.x installed  
- A Twilio account  
- Groq API access  
- (Optional) Airtable account  

---

### ⚙️ Step-by-Step Installation

#### 🌀 1. Download & Set Up Ngrok
[🔗 Download Ngrok](https://ngrok.com/download) and extract it.  
> Ngrok exposes your local server to the web for Twilio integration.

---

#### 📞 2. Register on Twilio
- Sign up on [Twilio](https://www.twilio.com/)  
- Get your **WhatsApp sandbox** credentials:
  - ✅ Account SID  
  - ✅ Auth Token  
  - ✅ Sandbox Number  

---

#### 🧠 3. Get Free Groq API Access
- Visit [Groq](https://groq.com/)  
- Create an account and get your **API key**

---


---

#### 🧪 4. Create Virtual Environment
```bash
python -m venv venv
````

---

#### 🧬 5. Activate the Environment

```bash
venv\Scripts\activate
```

---

#### 📦 7. Install Project Dependencies

```bash
pip install -r requirements.txt
```

---

#### 🚀 8. Run the Bot

```bash
python run.py
```

---

#### 🌐 9. Start Ngrok

```bash
ngrok http 5000
```
#### 🌐 9. Start the web dashboard

```bash
cd hms
```
```bash
python app.py
```

Copy the URL provided (e.g., `http://abc123.ngrok.io`)

---

#### 🧷 10. Connect to Twilio Sandbox

* Go to [Twilio Console](https://console.twilio.com/)
* Navigate to **Messaging → WhatsApp**
* Paste the Ngrok URL as the webhook

---

#### 💬 11. Start Messaging on WhatsApp!

Send a message to your Twilio sandbox number to interact with the bot.

---

## 🖥️ Admin Dashboard Overview

Once the bot is running, you can also access the **Admin Web Dashboard** to manage hospital operations.

### 📂 Modules Included:

* **Appointments** → View, Add, Edit, Delete
* **Medical Records** → Upload lab reports, patient history
* **Inventory** → Manage medicines, equipment, stock alerts
* **Patients** → Access, update or remove patient records
* **Dashboard Stats** → View key metrics in real-time

---

