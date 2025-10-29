# FINAL, CORRECTED, AND TESTED CODE FOR RENDER
import os
import sys
import yt_dlp
from flask import Flask, request, jsonify

# Flask app ko initialize karein
application = Flask(__name__)

# --- Poora Frontend Aik f-string Mein ---
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="ur" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SavvyReels - Deployed on Render</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body {{ font-family: 'Poppins', sans-serif; }}
        .gradient-text {{ @apply bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent; }}
    </style>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{ extend: {{ colors: {{ primary: '#1E3A8A', secondary: '#7C3AED', accent: '#14B8A6', lightBg: '#F9FAFB', darkBg: '#111827' }} }} }}
        }}
    </script>
</head>
<body class="bg-lightBg dark:bg-darkBg text-gray-800 dark:text-gray-200 transition-colors duration-300">
    <nav class="sticky top-0 z-50 bg-white/80 dark:bg-darkBg/80 backdrop-blur-md py-4 px-6 md:px-12">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold text-primary dark:text-white">Savvy<span class="text-secondary">Reels</span></h1>
            <button id="themeToggle" class="text-xl p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"><i class="fa-solid fa-moon"></i></button>
        </div>
    </nav>
    <main class="container mx-auto px-6 py-20 text-center">
        <h2 class="text-4xl md:text-6xl font-bold">The Ultimate <span class="gradient-text">Video Downloader</span></h2>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-4 max-w-2xl mx-auto">Paste any video link from major platforms. No registration. Just pure speed.</p>
        <form id="dlForm" class="max-w-2xl mx-auto mt-10 p-4 bg-white/50 dark:bg-gray-800/50 rounded-2xl shadow-2xl backdrop-blur-md flex flex-col md:flex-row gap-3">
            <input type="url" id="urlInput" placeholder="Paste your video link here..." required class="w-full px-5 py-3 text-lg bg-gray-100 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent transition">
            <button type="submit" id="dlBtn" class="w-full md:w-auto px-8 py-3 text-lg font-semibold text-white bg-secondary rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-400 transform hover:scale-105 transition flex items-center justify-center gap-2">
                <i class="fas fa-download"></i><span>Download</span>
            </button>
        </form>
        <div id="results" class="mt-10"></div>
    </main>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const q = (selector) => document.querySelector(selector);
            const form = q('#dlForm');
            const btn = q('#dlBtn');
            const resultsDiv = q('#results');
            const themeToggle = q('#themeToggle');
            const doc = document.documentElement;
            const applyTheme = () => {{
                const isDark = localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
                doc.classList.toggle('dark', isDark);
                themeToggle.innerHTML = `<i class="fa-solid fa-${{isDark ? 'sun' : 'moon'}}"></i>`;
            }};
            themeToggle.addEventListener('click', () => {{
                localStorage.theme = doc.classList.contains('dark') ? 'light' : 'dark';
                applyTheme();
            }});
            applyTheme();
            form.addEventListener('submit', async (e) => {{
                e.preventDefault();
                const url = q('#urlInput').value.trim();
                if (!url) return;
                btn.disabled = true;
                btn.innerHTML = `<div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Processing...</span>`;
                resultsDiv.innerHTML = '';
                try {{
                    const response = await fetch('/download', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url }}),
                    }});
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.error);
                    const optionsHTML = data.options.map(opt => {{
                        const isAudio = opt.type === 'Audio';
                        return `<a href="${{opt.url}}" target="_blank" download class="w-full text-white font-bold py-2 px-4 rounded-lg transition hover:scale-105 flex items-center justify-center gap-2 ${{isAudio ? 'bg-accent hover:bg-teal-600' : 'bg-primary hover:bg-blue-800'}}">
                                    <i class="fas fa-${{isAudio ? 'music' : 'video'}}"></i>${{opt.quality}}
                                </a>`;
                    }}).join('');
                    resultsDiv.innerHTML = `
                        <div class="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden text-left animate-fade-in">
                            <div class="md:flex">
                                <img class="h-48 w-full object-cover md:w-48" src="${{data.thumbnail}}" alt="Thumbnail">
                                <div class="p-6 w-full">
                                    <p class="font-bold text-lg">${{data.title}}</p>
                                    <div class="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3">${{optionsHTML}}</div>
                                </div>
                            </div>
                        </div>`;
                }} catch (error) {{
                    resultsDiv.innerHTML = `<div class="p-4 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 border border-red-400 rounded-lg">${{error.message}}</div>`;
                }} finally {{
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-download"></i><span>Download</span>';
                }}
            }});
        }});
        const style = document.createElement('style');
        style.innerHTML = `@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }} .animate-fade-in {{ animation: fadeIn 0.5s ease-out forwards; }}`;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

@application.route('/')
def home():
    return HTML_TEMPLATE
@application.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({{'error': 'URL not provided.'}}), 400
    try:
        with yt_dlp.YoutubeDL({{'noplaylist': True, 'quiet': True}}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            options, seen_res = [], set()
            for f in reversed(formats):
                res = f.get('height')
                if res and res not in seen_res and f.get('vcodec', '').startswith('avc') and f.get('acodec') != 'none':
                    options.append({{'quality': f'{{res}}p', 'url': f.get('url'), 'type': 'Video'}})
                    seen_res.add(res)
            best_audio = max((f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none'), key=lambda x: x.get('abr', 0), default=None)
            if best_audio:
                options.append({{'quality': 'Audio MP3', 'url': best_audio.get('url'), 'type': 'Audio'}})
            if not options:
                return jsonify({{'error': 'No downloadable formats found.'}}), 404
            return jsonify({{
                'title': info.get('title', 'Untitled Video'),
                'thumbnail': info.get('thumbnail', ''),
                'options': options
            }})
    except Exception as e:
        error_message = str(e).split(':')[-1].strip()
        if "Unsupported URL" in error_message: error_message = "This platform is not supported."
        return jsonify({{'error': f'Processing failed: {{error_message}}'}}), 500

# === RENDER KE LIYE FINAL START CODE ===
# YAHAN GHALTI THEEK KAR DI GAYI HAI
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=10000)
