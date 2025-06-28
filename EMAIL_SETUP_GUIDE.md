# 📧 Email Setup Guide for Newsletter Agent MCP

## 🔧 Gmail SMTP Authentication Fix

The error you're seeing is because Gmail no longer accepts regular passwords for SMTP authentication. You need to use an **App Password** instead.

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification**
3. Enable 2-Step Verification if not already enabled

### Step 2: Generate an App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** as the app
3. Select **Other (Custom name)** and name it "Newsletter Agent"
4. Click **Generate**
5. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### Step 3: Update Environment Variables
Replace your current email password with the App Password:

```bash
# Current (incorrect)
EMAIL_PASSWORD=P@ssw0rd_121525

# New (correct) - use the 16-character App Password
EMAIL_PASSWORD=abcd efgh ijkl mnop
```

### Step 4: Test the Configuration
After updating the environment variables, restart your backend server and try sending a newsletter again.

## 🚀 Alternative Email Providers

If you prefer not to use Gmail, here are other options:

### Option 1: Outlook/Hotmail
```bash
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USER=your-email@outlook.com
EMAIL_PASSWORD=your-password
```

### Option 2: Yahoo Mail
```bash
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USER=your-email@yahoo.com
EMAIL_PASSWORD=your-app-password
```

### Option 3: ProtonMail
```bash
EMAIL_HOST=127.0.0.1
EMAIL_PORT=1025
EMAIL_USER=your-email@protonmail.com
EMAIL_PASSWORD=your-password
```

## 🔍 Troubleshooting

### Common Issues:
1. **"Username and Password not accepted"** → Use App Password for Gmail
2. **"Connection timeout"** → Check firewall settings
3. **"SSL certificate error"** → The code handles this automatically

### Testing Email Configuration:
```bash
# Test with curl
curl -X POST http://localhost:8000/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "your-test-email@example.com"}'
```

## 📝 Environment Variables Reference

```bash
# Required for Gmail
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-gmail@gmail.com
EMAIL_PASSWORD=your-16-char-app-password

# Optional
EMAIL_FROM=your-gmail@gmail.com  # Defaults to EMAIL_USER
```

## ✅ Success Indicators

When email is working correctly, you should see:
- ✅ "Email sent successfully to [email]" in logs
- ✅ Newsletter arrives in inbox with proper formatting
- ✅ No authentication errors

## 🆘 Still Having Issues?

1. **Check logs** for specific error messages
2. **Verify App Password** is exactly 16 characters
3. **Test with a different email provider**
4. **Ensure 2FA is enabled** on Google account
5. **Check spam folder** for test emails

---

**Note**: For production use, consider using dedicated email services like SendGrid, Mailgun, or AWS SES for better deliverability and features. 