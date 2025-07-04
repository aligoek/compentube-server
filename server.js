// server.js
require('dotenv').config({ path: './.env' }); // <-- CRITICAL FIX: Load .env from the root directory
const express = require('express');
const cors = require('cors');
const session = require('express-session');
const { OAuth2Client } = require('google-auth-library');
const { spawn } = require('child_process');
const ytdl = require('ytdl-core');

const app = express();
const port = process.env.PORT || 5000;

// --- Configuration ---
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const GOOGLE_PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT_ID;
const SESSION_SECRET = process.env.SESSION_SECRET;

console.log("--- Server Configuration ---");
console.log("GOOGLE_CLIENT_ID loaded:", !!GOOGLE_CLIENT_ID);
console.log("GOOGLE_CLIENT_SECRET loaded:", !!GOOGLE_CLIENT_SECRET);
console.log("SESSION_SECRET loaded:", !!SESSION_SECRET);
console.log("--------------------------");


if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET || !SESSION_SECRET || !GOOGLE_PROJECT_ID) {
    console.error("FATAL ERROR: Missing Google or Session credentials in .env file. Please check that server.js is loading the .env file correctly and all variables are set.");
    process.exit(1);
}

// --- Middleware Setup ---
app.use(cors({
    origin: 'https://compentube.top', // Frontend'inizin canlı adresi
    credentials: true,
}));
app.use(express.json());
app.use(session({
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: true, // Render HTTPS kullandığı için bu gereklidir.
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000, // 24 saat
        sameSite: 'None' // Çapraz site isteklerinde çerezin gönderilmesini sağlar.
    }
}));

// --- Google OAuth Client ---
// Google'ın kodu yönlendireceği URI
const redirectUri = `https://compentube-server.onrender.com/api/auth/google/callback`; // Render backend URL'niz

console.log("Initializing OAuth2Client with this exact Redirect URI: \"" + redirectUri + "\"");

const oAuth2Client = new OAuth2Client(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    redirectUri
);

// --- Authentication Middleware ---
const isAuthenticated = (req, res, next) => {
    if (req.session.tokens) {
        return next();
    }
    res.status(401).json({ message: 'User not authenticated.' });
};

// --- Authentication Routes ---

// Bu rota, Google'dan gelen GET isteğini yakalayacak ve token değişimini yapacak.
app.get('/api/auth/google/callback', async (req, res) => {
    const code = req.query.code; // Kodu URL sorgu parametrelerinden al
    console.log('--- Google Callback Start ---');
    console.log("Received authorization code from Google redirect:", code ? "YES" : "NO");

    if (!code) {
        console.error("Authorization code is missing in the redirect request.");
        // Kod yoksa, frontend'e hata mesajıyla geri yönlendir
        // Hata durumunda yönlendirme güncellendi
        return res.redirect(`https://compentube.top?error=auth_failed&message=${encodeURIComponent('Authorization code missing.')}`);
    }

    try {
        console.log("Exchanging authorization code for tokens...");
        const { tokens } = await oAuth2Client.getToken(code);
        console.log("Tokens received successfully.");

        req.session.tokens = tokens; // Tokenları oturuma kaydet

        // Kullanıcı bilgilerini almak için id_token'ı doğrula
        const ticket = await oAuth2Client.verifyIdToken({
            idToken: tokens.id_token,
            audience: GOOGLE_CLIENT_ID,
        });
        const payload = ticket.getPayload();
        const user = {
            name: payload.name,
            email: payload.email,
            picture: payload.picture,
        };
        req.session.user = user; // Kullanıcı bilgilerini oturuma kaydet

        // *** BURADAKİ DEĞİŞİKLİK: Oturumu manuel olarak kaydetmeyi zorla ***
        req.session.user = user; // Kullanıcı bilgilerini oturuma kaydet

        console.log("Attempting to save session...");
        req.session.save((err) => {
            if (err) {
                console.error("ERROR: Failed to save session:", err);
                // Hata durumunda frontend'e hata mesajıyla geri yönlendir
                return res.redirect(`https://compentube.top?error=auth_failed&message=${encodeURIComponent('Session save failed.')}`);
            }
            console.log(`SUCCESS: User ${user.email} authenticated and session saved.`);
            // Oturum başarıyla kaydedildikten sonra yönlendirme yap
            console.log("Redirecting to frontend...");
            res.redirect('https://compentube.top');
        });
        console.log("req.session.save() called. Response will be sent after session save callback.");

        // --- Değişiklik Sonu ---

    } catch (error) {
        console.error('--- HATA DETAYLARI: Google Kimlik Doğrulama Token Değişimi ---');
        console.error('Genel Hata Mesajı:', error.message);
        console.error('Hata Stack Trace:', error.stack);

        if (error.response) {
            console.error('Google API Yanıt Detayları:');
            console.error('   HTTP Durum Kodu (status):', error.response.status);
            console.error('   Yanıt Verisi (data):', error.response.data);
        } else if (error.request) {
            console.error('İstek Yapıldı, Yanıt Alınamadı (Ağ Hatası Olabilir):');
            console.error('   İstek Nesnesi:', error.request);
        } else {
            console.error('İstek Ayarlanırken Hata Oluştu:', error.config);
        }
        // Hata durumunda frontend'e hata mesajıyla geri yönlendir
        res.redirect(`https://compentube.top?error=auth_failed&message=${encodeURIComponent(error.message || 'Authentication failed on server.')}`);
    }
});

// Eski app.post('/api/auth/google') rotası artık gerekli değil ve kaldırılmalı veya yorum satırı yapılmalı.
// Çünkü frontend artık kodu doğrudan backend'e POST etmiyor, Google doğrudan backend'e GET ile yönlendiriyor.
/*
app.post('/api/auth/google', async (req, res) => {
    const { code } = req.body;
    console.log("Received authorization code from client.");

    if (!code) {
        console.error("Authorization code is missing in the request.");
        return res.status(400).json({ message: 'Authorization code is missing.' });
    }
    try {
        console.log("Exchanging authorization code for tokens...");
        const { tokens } = await oAuth2Client.getToken(code);
        console.log("Tokens received successfully.");

        req.session.tokens = tokens;

        const ticket = await oAuth2Client.verifyIdToken({
            idToken: tokens.id_token,
            audience: GOOGLE_CLIENT_ID,
        });
        const payload = ticket.getPayload();
        const user = {
            name: payload.name,
            email: payload.email,
            picture: payload.picture,
        };
        req.session.user = user;

        console.log(`User ${user.email} authenticated and session created.`);
        res.status(200).json({ user });
    } catch (error) {
        console.error('--- HATA DETAYLARI: Google Kimlik Doğrulama Token Değişimi ---');
        console.error('Genel Hata Mesajı:', error.message);
        console.error('Hata Stack Trace:', error.stack);

        if (error.response) {
            console.error('Google API Yanıt Detayları:');
            console.error('   HTTP Durum Kodu (status):', error.response.status);
            console.error('   HTTP Durum Metni (statusText):', error.response.statusText);
            console.error('   Yanıt Başlıkları (headers):', error.response.headers);
            console.error('   Yanıt Verisi (data):', error.response.data);
            
            if (error.response.data && typeof error.response.data === 'object') {
                if (error.response.data.error) {
                    console.error('   Google API Hata Kodu:', error.response.data.error);
                }
                if (error.response.data.error_description) {
                    console.error('   Google API Hata Açıklaması:', error.response.data.error_description);
                }
                if (error.response.data.message) {
                    console.error('   Google API Ek Mesaj:', error.response.data.message);
                }
            }
        } else if (error.request) {
            console.error('İstek Yapıldı, Yanıt Alınamadı (Ağ Hatası Olabilir):');
            console.error('   İstek Nesnesi:', error.request);
        } else {
            console.error('İstek Ayarlanırken Hata Oluştu:', error.config);
        }

        console.error('--- HATA DETAYLARI SONU ---');
        res.status(500).json({ message: 'Kimlik doğrulama sunucu tarafında başarısız oldu. Lütfen logları kontrol edin.' });
    }
});
*/

app.get('/api/auth/status', (req, res) => {
    if (req.session.user) {
        console.log(`Auth status check: User ${req.session.user.email} is logged in.`);
        res.status(200).json({ loggedIn: true, user: req.session.user });
    } else {
        console.log("Auth status check: No user in session.");
        res.status(200).json({ loggedIn: false });
    }
});

app.post('/api/auth/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ message: 'Could not log out.' });
        }
        res.clearCookie('connect.sid');
        console.log('User logged out and session destroyed.');
        res.status(200).json({ message: 'Logged out successfully.' });
    });
});


// --- Main API Route ---

const getVideoId = (url) => {
    try {
        return ytdl.getVideoID(url);
    } catch (e) {
        const regex = /(?:https?:\/\/)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=|embed\/|v\/|shorts\/)?([\w-]{11})/;
        const match = url.match(regex);
        if (match && match[1]) return match[1];
        throw new Error('Invalid or unsupported YouTube URL format.');
    }
};

app.post('/api/summarize', isAuthenticated, async (req, res) => {
    const { youtubeLink, language, length } = req.body;
    if (!youtubeLink || !language || !length) {
        return res.status(400).json({ message: 'Missing required parameters.' });
    }

    try {
        const videoId = getVideoId(youtubeLink);
        console.log(`[User: ${req.session.user.email}] Starting summarization for Video ID: ${videoId}`);

        oAuth2Client.setCredentials(req.session.tokens);

        const transcriptPromise = new Promise((resolve, reject) => {
            const pythonProcess = spawn('python', ['get_transcript.py', videoId]);
            let pythonOutput = '', pythonError = '';
            pythonProcess.stdout.on('data', (data) => pythonOutput += data.toString());
            pythonProcess.stderr.on('data', (data) => pythonError += data.toString());
            pythonProcess.on('close', (code) => {
                if (code === 0 && pythonOutput.trim()) {
                    console.log('Transcript fetched successfully.');
                    resolve(pythonOutput.trim());
                } else {
                    console.error(`Python script error: ${pythonError}`);
                    reject(new Error('Could not retrieve transcript.'));
                }
            });
        });

        const videoDetailsPromise = async () => {
            const url = `https://www.googleapis.com/youtube/v3/videos?id=${videoId}&part=snippet`;
            const response = await oAuth2Client.request({ url });
            const data = response.data;
            if (data.items && data.items.length > 0) {
                const snippet = data.items[0].snippet;
                console.log('Video details fetched successfully.');
                return {
                    id: videoId,
                    title: snippet.title,
                    channel: snippet.channelTitle,
                    channelId: snippet.channelId,
                    thumbnail: snippet.thumbnails.high?.url || snippet.thumbnails.default?.url,
                };
            }
            throw new Error('Video details not found.');
        };

        const [transcript, videoDetails] = await Promise.all([transcriptPromise, videoDetailsPromise()]);

        const lengthInstruction = length === 'Short'
            ? 'Provide a concise summary of 9-10 sentences.'
            : 'Provide a detailed and comprehensive summary. Use bullet points for key takeaways and bold important terms.';

        const prompt = `Analyze the following YouTube video transcript and create a summary based on the user's requirements.\n\nTranscript:\n---\n${transcript}\n---\n\nUser Requirements:\n1. Summary Length: ${length}. ${lengthInstruction}\n2. Output Language: ${language}.\n3. Format: Use Markdown for clear formatting. Start with a title.`;

        console.log('Generating summary with Gemini...');
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`;
        const geminiResponse = await oAuth2Client.request({
            url: geminiUrl,
            method: 'POST',
            data: { contents: [{ parts: [{ text: prompt }] }] },
        });

        const summaryText = geminiResponse.data.candidates[0].content.parts[0].text;
        console.log('Gemini summary generated.');

        res.json({ success: true, summary: summaryText, videoDetails });

    } catch (error) {
        console.error('Error during summarization process:', error.response?.data?.error || error.message);
        res.status(500).json({ message: error.message || 'An internal server error occurred.' });
    }
});

app.listen(port, () => {
    console.log(`Backend server running at http://localhost:${port}`);
});
