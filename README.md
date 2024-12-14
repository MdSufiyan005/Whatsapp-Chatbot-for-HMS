# HMS WhatsApp Bot for Appointment Booking and Hospital Information

This project is a WhatsApp chatbot for a Hospital Management System (HMS) that helps patients book appointments and retrieve information about the hospital's services. It uses the Twilio API for WhatsApp messaging, Groq API for hospital management, and optional Airtable for an online SQL database.

---

### **Steps to Set Up the Project on Your System (Windows)**

Follow these instructions to set up the project on your local machine:

#### **Step 1: Download Ngrok**
Ngrok is a tool that creates a secure tunnel to your localhost, enabling your local server to be accessible from the web.
- Download Ngrok from [ngrok.com](https://ngrok.com/download).
- Extract the downloaded file to a folder of your choice.

#### **Step 2: Set Up an Account on Twilio**
Twilio is used for sending WhatsApp messages through the WhatsApp API.
- Create an account on [Twilio](https://www.twilio.com/).
- Follow their instructions to get a WhatsApp sandbox number and an API key. You will need the Twilio credentials (Account SID, Auth Token) for connecting the bot with WhatsApp.

#### **Step 3: Get Access to a Free API from Groq**
Groq is used for managing the hospital data and integrating it with the chatbot.
- Sign up on [Groq](https://groq.io/) to get free API access.
- Obtain the API key to connect Groq to the project.

#### **Step 4: Optional - Set Up Airtable as an Online SQL Database**
If you want to store patient or hospital data online, you can use Airtable as a database:
- Sign up on [Airtable](https://airtable.com/).
- Create a base (database) for storing data, such as appointments and hospital services.
- Get the API key from Airtable and note down the database details.

#### **Step 5: Create a Virtual Environment**
It's recommended to set up a virtual environment for Python projects to keep dependencies isolated.
- Open the command prompt or terminal and run the following commands:
    ```bash
    python -m venv venv
    ```
    This will create a virtual environment named `venv`.

#### **Step 6: Install All Modules/Dependencies**
Once the virtual environment is set up, install all necessary dependencies listed in the `requirements.txt` file. This file contains all the Python libraries required to run the project.
- Activate the virtual environment:
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
- Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

#### **Step 7: Run the Project**
Now, you're ready to run the project.
- Run the Python script to start the bot:
    ```bash
    python run.py
    ```
- In a separate terminal, start Ngrok to expose the local server to the internet:
    ```bash
    ngrok http 5000
    ```
    This will generate a public URL that you can use to connect to your local server.

#### **Step 8: Copy the Ngrok URL**
Once Ngrok is running, it will provide a public URL (something like `http://123456.ngrok.io`). Copy this URL.

#### **Step 9: Configure the Twilio WhatsApp Sandbox**
- Go to your [Twilio console](https://console.twilio.com/).
- Under the "Messaging" section, find "WhatsApp" and configure the sandbox.
- Paste the Ngrok URL (e.g., `http://123456.ngrok.io`) into the "Webhook URL" field under the "Messages" -> "WhatsApp" settings.
  
#### **Step 10: Start Messaging**
- Now that everything is set up, you can start interacting with the bot. Send a WhatsApp message to the sandbox number from your WhatsApp, and the bot will respond based on the functionalities you have programmed (e.g., appointment booking, getting hospital info).

---

### **Summary**

To set up the **HMS WhatsApp Bot** on your system, you'll need to:
1. Download and set up Ngrok to expose your local server.
2. Set up Twilio for WhatsApp messaging.
3. Optionally, set up Groq and Airtable for API access and data storage.
4. Install the required Python libraries in a virtual environment.
5. Run the bot and connect it to Twilio using the Ngrok URL.

Once set up, you can easily interact with the bot via WhatsApp to book appointments and receive hospital information.