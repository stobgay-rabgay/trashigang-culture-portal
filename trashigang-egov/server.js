const express = require('express');
const session = require('express-session');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

app.use(session({
    secret: 'dzongkhag_secret_key_123',
    resave: false,
    saveUninitialized: false
}));

// In-memory user database (or file-backed array)
const users = [];

// Configure Multer for Signature Uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = 'public/uploads';
        if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});
const upload = multer({ storage });

// Register Route
app.post('/api/register', (req, res) => {
    const { username, password, official_name, jurisdiction } = req.body;
    
    const existingUser = users.find(u => u.username.toLowerCase() === username.toLowerCase());
    if (existingUser) {
        return res.status(400).send('User already exists. <a href="/login.html">Click here to Login</a>');
    }

    const newUser = { username, password, official_name, jurisdiction, signature_path: '' };
    users.push(newUser);

    // Auto-login after registration
    req.session.user = newUser;
    res.redirect('/dashboard.html');
});

// Login Route
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    const user = users.find(u => u.username.trim().toLowerCase() === username.trim().toLowerCase() && u.password === password);

    if (!user) {
        return res.status(401).send('Invalid Username or Password. <a href="/login.html">Try Again</a>');
    }

    req.session.user = user;
    res.redirect('/dashboard.html');
});

// Fetch Active Session User Data
app.get('/api/user-data', (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    res.json(req.session.user);
});

// Logout Route
app.get('/api/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login.html');
});

// Upload Signature
app.post('/api/upload-signature', upload.single('signature'), (req, res) => {
    if (!req.session.user) return res.status(401).send('Unauthorized');
    if (req.file) {
        req.session.user.signature_path = '/uploads/' + req.file.filename;
        const target = users.find(u => u.username === req.session.user.username);
        if (target) target.signature_path = req.session.user.signature_path;
    }
    res.redirect('/dashboard.html');
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
