# DermIQ

DermIQ is an AI-powered skincare intelligence platform that analyzes skin conditions to provide personalized product recommendations. It features a complete product catalog, shopping cart, secure Razorpay integration, and a comprehensive admin dashboard.

## Features
- AI-powered skin analysis
- Personalized skincare recommendations
- Product catalog
- Shopping cart & checkout
- Razorpay payment integration
- User profile & order history
- Admin dashboard
- Responsive UI

## Tech Stack
| Component | Technology |
| :--- | :--- |
| Backend | Python, Flask, SQLAlchemy |
| Database | MySQL |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Payment Gateway | Razorpay |

## Installation

```bash
git clone https://github.com/bhavyamotiyani/DermIQ.git
cd DermIQ
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python init_mysql.py
python run.py
```

## Deployment on Render + Aiven (Recommended Free Option)

This setup uses **Render** to host the Flask application and **Aiven** to host a free MySQL database.

### 1. Set Up the MySQL Database (Aiven)
1. Sign up for a free account at [Aiven.io](https://aiven.io/).
2. Create a new **MySQL** database service and choose the **Free Tier**.
3. Once the service is running, find the **Connection Parameters** in your Aiven console and note down the host, port, username, password, and database name (`defaultdb`).

### 2. Initialize the Database Schema
Before launching on Render, run the initialization script locally to connect to your remote database and create the tables:
1. Temporarily configure your local `.env` file with the Aiven connection parameters:
   ```env
   DB_USER=avnadmin
   DB_PASSWORD=your_aiven_password
   DB_HOST=mysql-xxxxxx.aivencloud.com
   DB_PORT=your_aiven_port
   DB_NAME=defaultdb
   ```
2. Run the initialization script in your local terminal:
   ```bash
   python init_mysql.py
   ```
3. Once successful, change your local `.env` file credentials back to `localhost` so you don't overwrite your cloud database during local testing.

### 3. Deploy the Flask App (Render)
1. Sign up for a free account on [Render](https://render.com/) and connect your GitHub account.
2. Click **New +** > **Web Service** and select your `DermIQ` repository.
3. Configure the service:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn run:app`
   * **Plan**: `Free`
4. Go to the **Environment** tab on Render and click **Add Environment Variable** to add your Aiven database credentials and Razorpay keys:
   * `DB_USER` = `avnadmin`
   * `DB_PASSWORD` = `your_aiven_password`
   * `DB_HOST` = `mysql-xxxxxx.aivencloud.com`
   * `DB_PORT` = `your_aiven_port`
   * `DB_NAME` = `defaultdb`
   * `SECRET_KEY` = `your_custom_secret_key`
   * `RAZORPAY_KEY_ID` = `your_razorpay_key_id`
   * `RAZORPAY_KEY_SECRET` = `your_razorpay_key_secret`
5. Click **Save Changes**. Render will trigger a build and deploy your application.


