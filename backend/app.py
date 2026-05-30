from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Naveen oda Backend Working da!"

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json
    name = data.get("name")
    email = data.get("email") 
    message = data.get("message")
    
    print("=== PUTHU MESSAGE ===")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Message: {message}")
    print("====================")
    
    return jsonify({
        "status": "success", 
        "msg": f"Thanks {name}, un message kedaichiduchu!"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import logging

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email Configuration from Environment Variables
GMAIL_USER = os.environ.get('GMAIL_USER', 'your-email@gmail.com')
GMAIL_PASS = os.environ.get('GMAIL_PASS', 'your-app-password')
RECIPIENT_EMAIL = 'naveens34567@gmail.com'

# Home Route - Test Backend
@app.route('/')
def home():
    """
    Root endpoint to check if backend is running
    Returns: Welcome message with timestamp
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Home route accessed at {current_time}")
    return jsonify({
        "status": "success",
        "message": "Naveen oda Backend Working da!",
        "timestamp": current_time,
        "server": "Flask Production Server"
    })

# Contact Form Route
@app.route('/contact', methods=['POST'])
def contact():
    """
    Contact form endpoint - receives data from frontend
    Accepts: JSON with name, email, phone, message
    Returns: Success/Error JSON response
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                "status": "error", 
                "message": "No data received"
            }), 400
        
        # Extract form fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', 'Not provided').strip()
        message = data.get('message', '').strip()
        
        # Validation
        if not name or not email or not message:
            logger.warning(f"Missing fields: name={bool(name)}, email={bool(email)}, message={bool(message)}")
            return jsonify({
                "status": "error",
                "message": "Name, Email and Message are required fields"
            }), 400
        
        # Email validation basic check
        if '@' not in email or '.' not in email:
            logger.warning(f"Invalid email format: {email}")
            return jsonify({
                "status": "error",
                "message": "Please provide a valid email address"
            }), 400
        
        # Log the submission
        logger.info(f"New contact form submission from: {name} ({email}) - Phone: {phone}")
        
        # Create email body
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_body = f"""

        NEW CONTACT FORM SUBMISSION

        
        Submission Time: {timestamp}
        
        Contact Details:

        Full Name: {name}
        Email Address: {email}
        Phone Number: {phone}
        
        Message:

        {message}

        This email was sent from your Portfolio Website
        Backend: https://portfolio-website-accs.onrender.com

        """
        
        # Send email
        email_sent = send_email(name, email, phone, email_body)
        
        if email_sent:
            logger.info(f"Email sent successfully to {RECIPIENT_EMAIL}")
            return jsonify({
                "status": "success",
                "message": "Your message has been sent successfully! I'll get back to you soon.",
                "data": {
                    "name": name,
                    "email": email,
                    "phone": phone
                }
            }), 200
        else:
            logger.error("Failed to send email")
            return jsonify({
                "status": "error",
                "message": "Failed to send email. Please try again later."
            }), 500
            
    except Exception as e:
        logger.error(f"Error in contact route: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred. Please try again."
        }), 500

def send_email(sender_name, sender_email, sender_phone, message_body):
    """
    Send email using Gmail SMTP
    Args:
        sender_name: Name of person contacting
        sender_email: Email of person contacting  
        sender_phone: Phone number - 9342926928 etc
        message_body: Full email content
    Returns: Boolean - True if sent, False if failed
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f'Portfolio Contact: {sender_name} - {sender_phone}'
        msg['Reply-To'] = sender_email
        
        # Attach body
        msg.attach(MIMEText(message_body, 'plain'))
        
        # Connect to Gmail SMTP Server
        logger.info("Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            logger.info("SMTP login successful")
            
            # Send email
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
            logger.info(f"Email sent from {sender_email} with phone {sender_phone}")
            return True
            
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed. Check GMAIL_USER and GMAIL_PASS")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in send_email: {str(e)}")
        return False

# Health Check Route
@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "Portfolio Backend",
        "version": "2.0"
    }), 200

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Route not found",
        "error": "404"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "status": "error", 
        "message": "Internal server error",
        "error": "500"
    }), 500

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)