import sqlite3
import os
import sys

# Ścieżka docelowa na VPS (domyślna)
vps_db_path = "/var/lib/docker/volumes/creator-hub-n8n_data/_data/aura_ai_directory.sqlite"
local_db_path = "./aura_ai_directory.sqlite"

# Określenie, której ścieżki użyć
if os.path.exists(os.path.dirname(vps_db_path)):
    db_path = vps_db_path
    print(f"[*] Wykryto środowisko VPS. Używam bazy docelowej: {db_path}")
else:
    db_path = local_db_path
    print(f"[*] Nie znaleziono katalogu wolumenu Docker. Tworzę bazę lokalną do testów: {db_path}")

# Nawiązanie połączenia z bazą danych
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Tworzenie tabel, jeśli nie istnieją (zgodnie ze standardem ufortyfikowanym)
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    rating REAL CHECK(rating >= 4.5 AND rating <= 5.0),
    pricing_type TEXT CHECK(pricing_type IN ('Free', 'Freemium', 'Paid', 'Free Trial')),
    badge TEXT CHECK(badge IN ('Featured', 'Trending', 'Popular', 'New')),
    description TEXT NOT NULL,
    official_url TEXT NOT NULL,
    category_id INTEGER,
    FOREIGN KEY(category_id) REFERENCES categories(id)
);
""")

# 2. Inicjalizacja 6 klastrów kategorii
categories = [
    (1, "Chatbot"),
    (2, "Writing"),
    (3, "Productivity"),
    (4, "Marketing"),
    (5, "Design"),
    (6, "Video & Audio")
]

for cat_id, cat_name in categories:
    cursor.execute("INSERT OR REPLACE INTO categories (id, name) VALUES (?, ?);", (cat_id, cat_name))

# 3. Definicja 120 ufortyfikowanych narzędzi AI (dokładnie po 20 narzędzi na każdy z 6 klastrów)
tools_data = [
    # === CLUSTER 1: Chatbot (IDs: 1) ===
    (1, "ChatGPT", "chatgpt", 4.9, "Freemium", "Featured", "OpenAI's flagship conversational AI model powered by GPT-4.", "https://chatgpt.com", 1),
    (2, "Claude", "claude", 4.9, "Freemium", "Featured", "Anthropic's advanced conversational AI with deep reasoning capabilities.", "https://claude.ai", 1),
    (3, "Coze", "coze", 4.7, "Freemium", "Popular", "ByteDance's powerful platform for building and deploying custom AI chatbots.", "https://www.coze.com", 1),
    (4, "Chatbase", "chatbase", 4.6, "Paid", "Trending", "Build a custom GPT chatbot trained on your data and embed it on your website.", "https://www.chatbase.co", 1),
    (5, "Chatfuel", "chatfuel", 4.5, "Paid", "Popular", "Leading no-code chatbot builder for Facebook Messenger, Instagram, and WhatsApp.", "https://chatfuel.com", 1),
    (6, "Dialogflow", "dialogflow", 4.6, "Freemium", "Popular", "Google's conversational AI development suite for enterprise-grade voice and chat bots.", "https://cloud.google.com/dialogflow", 1),
    (7, "Landbot", "landbot", 4.5, "Freemium", "New", "Conversational chatbot builder that transforms static web pages into engaging chats.", "https://landbot.io", 1),
    (8, "ManyChat", "manychat", 4.7, "Freemium", "Popular", "Automate interactive conversations across Instagram, WhatsApp, and Facebook.", "https://manychat.com", 1),
    (9, "Tidio", "tidio", 4.6, "Freemium", "Popular", "Customer service platform with AI-powered Lyro chatbot for instant support.", "https://www.tidio.com", 1),
    (10, "Poe", "poe", 4.7, "Freemium", "Trending", "Quora's multi-bot aggregator platform to converse with various LLMs instantly.", "https://poe.com", 1),
    (11, "Character.ai", "character-ai", 4.8, "Free", "Trending", "Engaging conversational bots with diverse personalities and advanced memory.", "https://character.ai", 1),
    (12, "CustomGPT", "customgpt", 4.6, "Paid", "Featured", "Build secure, private enterprise chatbots using your own documents and PDFs.", "https://customgpt.ai", 1),
    (13, "Voiceflow", "voiceflow", 4.8, "Freemium", "Featured", "Design, prototype, and build production-ready conversational AI agents collaboratively.", "https://www.voiceflow.com", 1),
    (14, "Botpress", "botpress", 4.7, "Freemium", "Popular", "The next-generation, developer-friendly conversational AI platform.", "https://botpress.com", 1),
    (15, "IBM Watson Assistant", "watson-assistant", 4.5, "Freemium", "Popular", "Enterprise conversation AI platform built to deliver fast, accurate answers across channels.", "https://www.ibm.com/watson", 1),
    (16, "LiveChat AI", "livechat-ai", 4.5, "Paid", "New", "Automate customer support with custom-trained AI chatbots for instant replies.", "https://livechat.ai", 1),
    (17, "Kore.ai", "kore-ai", 4.6, "Paid", "Popular", "Secure, scalable enterprise conversational AI platform for voice and digital channels.", "https://kore.ai", 1),
    (18, "Rasa", "rasa", 4.6, "Free", "Popular", "Open-source machine learning framework for building highly customized chat assistants.", "https://rasa.com", 1),
    (19, "Inbenta", "inbenta", 4.5, "Paid", "New", "Conversational AI and semantic search platform built on patented technology.", "https://www.inbenta.com", 1),
    (20, "Ada", "ada", 4.7, "Paid", "Featured", "Automated customer service software that resolves VIP inquiries instantly in any language.", "https://www.ada.cx", 1),

    # === CLUSTER 2: Writing (IDs: 2) ===
    (21, "Copy.ai", "copy-ai", 4.7, "Freemium", "Popular", "Advanced AI copywriter built for high-converting marketing campaigns and sales.", "https://www.copy.ai", 2),
    (22, "Jasper", "jasper", 4.8, "Paid", "Featured", "Enterprise-grade generative AI platform for on-brand content and blogs.", "https://www.jasper.ai", 2),
    (23, "Grammarly", "grammarly", 4.9, "Freemium", "Popular", "AI-powered writing assistant and comprehensive, real-time grammar editor.", "https://www.grammarly.com", 2),
    (24, "QuillBot", "quillbot", 4.8, "Freemium", "Popular", "Leading paraphraser, summarizer, and vocabulary expansion tool.", "https://quillbot.com", 2),
    (25, "Notion AI", "notion-ai", 4.7, "Paid", "Featured", "Integrated AI assistant to write, summarize, and edit directly within Notion.", "https://www.notion.so/product/ai", 2),
    (26, "Hypotenuse AI", "hypotenuse-ai", 4.6, "Paid", "Trending", "Generate SEO-optimized blog posts and e-commerce descriptions automatically.", "https://www.hypotenuse.ai", 2),
    (27, "Writesonic", "writesonic", 4.7, "Freemium", "Trending", "Generative AI writing tool optimized for high-ranking SEO content.", "https://writesonic.com", 2),
    (28, "Rytr", "rytr", 4.6, "Freemium", "Popular", "Affordable and fast AI writing assistant for landing pages, emails, and ads.", "https://rytr.me", 2),
    (29, "Sudowrite", "sudowrite", 4.8, "Paid", "Featured", "The ultimate AI-powered companion designed for fiction writers and novelists.", "https://www.sudowrite.com", 2),
    (30, "Wordtune", "wordtune", 4.7, "Freemium", "Popular", "AI rewriter that clarifies sentences, alters tones, and refines wording.", "https://www.wordtune.com", 2),
    (31, "Frase", "frase", 4.6, "Paid", "Trending", "SEO content writing and optimization tool to help you outline and write easily.", "https://www.frase.io", 2),
    (32, "Surfer SEO Writer", "surferseo-writer", 4.8, "Paid", "Featured", "Real-time semantic SEO guidelines inside an interactive text editor.", "https://surferseo.com", 2),
    (33, "ProWritingAid", "prowritingaid", 4.7, "Freemium", "Popular", "Comprehensive manuscript, style, and grammar editing assistant.", "https://prowritingaid.com", 2),
    (34, "Copysmith", "copysmith", 4.5, "Paid", "New", "Enterprise-grade AI product description generator built for e-commerce.", "https://copysmith.ai", 2),
    (35, "WordAI", "wordai", 4.5, "Paid", "Popular", "Smart automatic rewriter that translates sentences into completely new phrasing.", "https://wordai.com", 2),
    (36, "Ginger Software", "ginger", 4.5, "Freemium", "Popular", "Intelligent writing correction assistant and productivity tool.", "https://www.gingersoftware.com", 2),
    (37, "Hemingway Editor", "hemingway", 4.6, "Free", "Popular", "Visual app that highlights passive voice, complex adverbs, and hard sentences.", "https://hemingwayapp.com", 2),
    (38, "Neuroflash", "neuroflash", 4.7, "Freemium", "New", "Europe's leading marketing copy generator optimized for regional tone.", "https://neuroflash.com", 2),
    (39, "Article Forge", "article-forge", 4.5, "Paid", "New", "Generate full SEO articles based on keywords using advanced deep learning.", "https://www.articleforge.com", 2),
    (40, "ContentBot", "contentbot", 4.6, "Paid", "Trending", "Advanced workflow automation and AI copy platform for content marketers.", "https://contentbot.ai", 2),

    # === CLUSTER 3: Productivity (IDs: 3) ===
    (41, "Perplexity", "perplexity", 4.9, "Freemium", "Featured", "Conversational AI answers engine that provides clean, cited live web answers.", "https://www.perplexity.ai", 3),
    (42, "Taskade", "taskade", 4.8, "Freemium", "Featured", "AI-powered workspace for team productivity, notes, and interactive mind mapping.", "https://www.taskade.com", 3),
    (43, "Microsoft Copilot", "copilot", 4.8, "Freemium", "Popular", "Official AI companion integrated directly across Windows and Office 365.", "https://copilot.microsoft.com", 3),
    (44, "Phind", "phind", 4.8, "Free", "Trending", "Generative AI search engine built specifically for rapid developer coding help.", "https://www.phind.com", 3),
    (45, "Replit Ghostwriter", "replit-ghostwriter", 4.7, "Paid", "Featured", "In-context AI companion that helps write and debug code directly in Replit.", "https://replit.com", 3),
    (46, "Cursor", "cursor", 4.9, "Freemium", "Trending", "The AI-first fork of VS Code designed for lightning-fast software development.", "https://www.cursor.com", 3),
    (47, "Otter.ai", "otter-ai", 4.7, "Freemium", "Popular", "Automated real-time voice transcription, summaries, and action items.", "https://otter.ai", 3),
    (48, "Notion", "notion", 4.9, "Freemium", "Popular", "Sovereign-class workspace combining databases, wikis, and structured notes.", "https://www.notion.so", 3),
    (49, "Fireflies.ai", "fireflies", 4.7, "Freemium", "Popular", "Record, transcribe, and search across your team's live calls and meetings.", "https://fireflies.ai", 3),
    (50, "Todoist", "todoist", 4.8, "Freemium", "Popular", "Intelligent task manager with NLP-driven quick-add and automatic scheduling.", "https://todoist.com", 3),
    (51, "ClickUp AI", "clickup-ai", 4.7, "Paid", "Featured", "Project management suite with automated task creation and documentation AI.", "https://clickup.com", 3),
    (52, "Grammarly GO", "grammarly-go", 4.7, "Freemium", "New", "Context-aware personal AI helper that drafts emails and revises text.", "https://www.grammarly.com/ai", 3),
    (53, "ChatGPT Search", "chatgpt-search", 4.8, "Freemium", "New", "OpenAI's official live web search layer with conversational indexing.", "https://chatgpt.com", 3),
    (54, "Tabnine", "tabnine", 4.6, "Freemium", "Popular", "Secure local and cloud code completion for professional developers.", "https://www.tabnine.com", 3),
    (55, "Obsidian", "obsidian", 4.9, "Free", "Popular", "Local Markdown knowledge base with a vast ecosystem of community AI plugins.", "https://obsidian.md", 3),
    (56, "Mem.ai", "mem-ai", 4.6, "Paid", "New", "The world's first personalized, self-organizing workspace powered by AI.", "https://mem.ai", 3),
    (57, "Lindy.ai", "lindy-ai", 4.6, "Freemium", "Trending", "Build autonomous AI employees that handle operations, emails, and CRM tasks.", "https://www.lindy.ai", 3),
    (58, "Slid", "slid", 4.5, "Freemium", "New", "One-click educational video and PDF screenshot and note-taking assistant.", "https://slid.co", 3),
    (59, "PDF24", "pdf24", 4.9, "Free", "Popular", "100% free, secure offline and online PDF tools with OCR and signing.", "https://tools.pdf24.org", 3),
    (60, "Alfred", "alfred", 4.8, "Free", "Popular", "Award-winning productivity launcher for macOS with automated SRE workflows.", "https://www.alfredapp.com", 3),

    # === CLUSTER 4: Marketing (IDs: 4) ===
    (61, "Semrush", "semrush", 4.8, "Paid", "Featured", "Industry-standard SEO, market research, and competitive intelligence suite.", "https://www.semrush.com", 4),
    (62, "AdCreative.ai", "adcreative", 4.7, "Paid", "Trending", "Generate conversion-focused ad banners and creatives in a few seconds.", "https://www.adcreative.ai", 4),
    (63, "Pencil", "pencil", 4.6, "Paid", "Featured", "Generate and test optimized high-velocity video ads for social commerce.", "https://www.trypencil.com", 4),
    (64, "VidIQ", "vidiq", 4.7, "Freemium", "Popular", "Leading analytics and SEO optimization suite designed for YouTube creators.", "https://vidiq.com", 4),
    (65, "SurferSEO", "surferseo", 4.8, "Paid", "Featured", "SEO content optimization tool that audits pages and analyzes SERPs.", "https://surferseo.com", 4),
    (66, "Jasper Campaigns", "jasper-campaigns", 4.7, "Paid", "Popular", "Generate complete marketing campaigns with matching assets in one go.", "https://www.jasper.ai", 4),
    (67, "TubeBuddy", "tubebuddy", 4.6, "Freemium", "Popular", "Advanced browser extension for YouTube SEO, tags, and bulk management.", "https://www.tubebuddy.com", 4),
    (68, "Copy.ai Brand Voice", "copyai-brandvoice", 4.7, "Paid", "Featured", "Scale content marketing with a precise and fully aligned brand voice.", "https://www.copy.ai", 4),
    (69, "Flick", "flick", 4.6, "Freemium", "Popular", "All-in-one social media scheduler, copywriting, and hashtag researcher.", "https://www.flick.social", 4),
    (70, "Ocoya", "ocoya", 4.5, "Paid", "Trending", "Design, write, and schedule social media content 10x faster with AI.", "https://www.ocoya.com", 4),
    (71, "Brand24", "brand24", 4.7, "Paid", "Featured", "Social media listening and real-time brand reputation tracking platform.", "https://brand24.com", 4),
    (72, "Feedly", "feedly", 4.6, "Freemium", "Popular", "AI-powered market intelligence feed that filters news and tracking topics.", "https://feedly.com", 4),
    (73, "MarketMuse", "marketmuse", 4.6, "Paid", "Featured", "Automated content planning and keyword authority auditing software.", "https://www.marketmuse.com", 4),
    (74, "BuzzSumo", "buzzsumo", 4.6, "Paid", "Popular", "Discover the best performing content and find top niche influencers.", "https://buzzsumo.com", 4),
    (75, "Writesonic SEO", "writesonic-seo", 4.6, "Freemium", "New", "One-click generator for SEO-optimized articles based on competing URLs.", "https://writesonic.com", 4),
    (76, "Mutiny", "mutiny", 4.7, "Paid", "Featured", "No-code website personalization and conversion rate optimizer for B2B.", "https://www.mutinyhq.com", 4),
    (77, "Smartly.io", "smartly-io", 4.6, "Paid", "Popular", "Automated social media advertising and campaign optimization platform.", "https://www.smartly.io", 4),
    (78, "Synthesia Marketing", "synthesia-mktg", 4.7, "Paid", "Trending", "Create personalized video campaigns using lifelike synthetic AI presenters.", "https://www.synthesia.io", 4),
    (79, "HubSpot AI", "hubspot-ai", 4.7, "Freemium", "Popular", "Inbound marketing software with embedded AI content and email generation.", "https://www.hubspot.com", 4),
    (80, "Anyword", "anyword", 4.7, "Paid", "Featured", "AI copywriter with a predictive performance score to forecast ad results.", "https://anyword.com", 4),

    # === CLUSTER 5: Design (IDs: 5) ===
    (81, "Midjourney", "midjourney", 4.9, "Paid", "Featured", "Highest fidelity image generation engine operating via Web and Discord.", "https://www.midjourney.com", 5),
    (82, "DALL-E 3", "dall-e-3", 4.8, "Freemium", "Popular", "OpenAI's latest image model, famous for following complex prompts.", "https://openai.com/dall-e-3", 5),
    (83, "Canva", "canva", 4.9, "Freemium", "Popular", "Simple online graphics design suite backed by Magic Studio AI features.", "https://www.canva.com", 5),
    (84, "Krea", "krea", 4.7, "Freemium", "Trending", "Real-time AI canvas, instant upscaling, and generative image styling.", "https://www.krea.ai", 5),
    (85, "Recraft", "recraft", 4.8, "Freemium", "Featured", "Infinite vector graphics and icon set generator for UI designers.", "https://www.recraft.ai", 5),
    (86, "Ideogram", "ideogram", 4.8, "Freemium", "Trending", "Famous for drawing perfect letters and fonts inside generated images.", "https://ideogram.ai", 5),
    (87, "Framer", "framer", 4.8, "Freemium", "Featured", "Sovereign web builder that turns interactive designs into live websites.", "https://www.framer.com", 5),
    (88, "Figma", "figma", 4.9, "Freemium", "Popular", "Industry-standard UI/UX software with integrated AI design plugins.", "https://www.figma.com", 5),
    (89, "Photopea", "photopea", 4.8, "Free", "Popular", "100% free, advanced browser-based alternative to Adobe Photoshop.", "https://www.photopea.com", 5),
    (90, "GIMP", "gimp", 4.6, "Free", "Popular", "Powerful open-source GNU Image Manipulation Program for raster art.", "https://www.gimp.org", 5),
    (91, "Looka", "looka", 4.6, "Freemium", "Popular", "Instantly design a custom brand logo and cohesive marketing assets.", "https://looka.com", 5),
    (92, "Adobe Firefly", "firefly", 4.7, "Freemium", "Popular", "Commercially safe generative AI models integrated into Creative Cloud.", "https://www.adobe.com/products/firefly", 5),
    (93, "Photoroom", "photoroom", 4.8, "Freemium", "Popular", "Industry-leading automated background remover and product shot generator.", "https://www.photoroom.com", 5),
    (94, "Leonardo.ai", "leonardo-ai", 4.8, "Freemium", "Trending", "Create high-end visual assets, models, and textures with creative control.", "https://leonardo.ai", 5),
    (95, "Runway Gen-2", "runway-gen2", 4.7, "Freemium", "Featured", "Revolutionary text-to-image and image-to-video AI generation engine.", "https://runwayml.com", 5),
    (96, "Spline", "spline", 4.8, "Freemium", "Trending", "Collaborative 3D design software with AI-assisted object generation.", "https://spline.design", 5),
    (97, "Khroma", "khroma", 4.6, "Free", "Popular", "Personalized AI color combinations, palettes, and typography helper.", "https://khroma.co", 5),
    (98, "Remove.bg", "remove-bg", 4.8, "Freemium", "Popular", "Single-click instant background removal with high-precision edge cutout.", "https://www.remove.bg", 5),
    (99, "Vectary", "vectary", 4.6, "Freemium", "New", "Browser-based 3D modeling tool with interactive AR and AI integrations.", "https://www.vectary.com", 5),
    (100, "Gamma", "gamma", 4.8, "Freemium", "Featured", "Create beautiful presentations, web landing pages, and docs in seconds.", "https://gamma.app", 5),

    # === CLUSTER 6: Video & Audio (IDs: 6) ===
    (101, "ElevenLabs", "elevenlabs", 4.9, "Freemium", "Featured", "Unbelievably realistic AI voice generator and text-to-speech engine.", "https://elevenlabs.io", 6),
    (102, "HeyGen", "heygen", 4.8, "Paid", "Featured", "Create professional business videos with hyper-realistic AI avatars.", "https://www.heygen.com", 6),
    (103, "Descript", "descript", 4.8, "Freemium", "Popular", "Text-based video and audio editing that makes cutting video as easy as doc.", "https://www.descript.com", 6),
    (104, "Fliki", "fliki", 4.7, "Freemium", "Trending", "Turn blogs, summaries, and text articles into videos with AI voices.", "https://fliki.ai", 6),
    (105, "Suno", "suno", 4.9, "Freemium", "Featured", "Create fully-produced studio-quality vocal tracks and songs from text.", "https://suno.com", 6),
    (106, "Runway", "runway", 4.8, "Freemium", "Featured", "Professional creative tool with text-to-video and advanced motion brush.", "https://runwayml.com", 6),
    (107, "Veed.io", "veed", 4.7, "Freemium", "Popular", "Simple online video editing platform with automated subtitles and cuts.", "https://www.veed.io", 6),
    (108, "DaVinci Resolve", "davinci", 4.9, "Free", "Popular", "Hollywood-grade offline video editing, color grading, and fusion effects.", "https://www.blackmagicdesign.com", 6),
    (109, "OBS Studio", "obs", 4.9, "Free", "Popular", "The ultimate open-source screen recording and live streaming studio.", "https://obsproject.com", 6),
    (110, "Udio", "udio", 4.8, "Freemium", "Trending", "Next-gen generative AI music application capable of full musical scores.", "https://www.udio.com", 6),
    (111, "Adobe Podcast", "adobe-podcast", 4.7, "Freemium", "Popular", "Browser-based audio enhancement tool that makes mic sound like studio.", "https://podcast.adobe.com", 6),
    (112, "Synthesia", "synthesia", 4.8, "Paid", "Featured", "Enterprise video generator powered by deepfake AI avatar presenters.", "https://www.synthesia.io", 6),
    (113, "Opus Clip", "opus-clip", 4.7, "Freemium", "Trending", "Repurpose long webinars and podcasts into viral TikToks and YouTube Shorts.", "https://www.opus.pro", 6),
    (114, "Riverside.fm", "riverside", 4.8, "Freemium", "Popular", "Local remote recording studio delivering uncompressed 4K video and audio.", "https://riverside.fm", 6),
    (115, "Podcastle", "podcastle", 4.7, "Freemium", "Popular", "All-in-one web platform for high-quality audio recording and podcasting.", "https://podcastle.ai", 6),
    (116, "Murf.ai", "murf", 4.7, "Paid", "Popular", "Studio-quality AI voice generator built for corporate presentations.", "https://murf.ai", 6),
    (117, "Lovo.ai", "lovo", 4.6, "Paid", "New", "Next-gen AI voiceover platform and award-winning speech synthesizer.", "https://lovo.ai", 6),
    (118, "Soundraw", "soundraw", 4.6, "Paid", "Trending", "Generate royalty-free background tracks matching your video's mood.", "https://soundraw.io", 6),
    (119, "Pictory", "pictory", 4.6, "Paid", "New", "Automatically extract high-value clips from your video files using AI.", "https://pictory.ai", 6),
    (120, "InVideo", "invideo", 4.7, "Freemium", "Popular", "Turn scripts and prompt workflows into polished videos with templates.", "https://invideo.io", 6)
]

# 4. Wstrzykiwanie danych do tabeli ai_tools
for row in tools_data:
    cursor.execute("""
    INSERT OR REPLACE INTO ai_tools (
        tool_number, name, slug, rating, pricing_type, badge, description, official_url, category_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, row)

# Zatwierdzenie transakcji
conn.commit()

# 5. Weryfikacja poprawności (Pomiary SRE)
cursor.execute("SELECT count(*) FROM ai_tools;")
total_count = cursor.fetchone()[0]

print("\n=== 🎉 PROCES ZASILANIA BAZY DANYCH ZAKOŃCZONY SUKCESEM! ===")
print(f"[*] Plik bazy danych: {os.path.abspath(db_path)}")
print(f"[*] Łączna liczba kategorii w tabeli 'categories': 6")
print(f"[*] Łączna liczba narzędzi w tabeli 'ai_tools': {total_count} / 120")
print("============================================================\n")

# Zamknięcie połączenia
conn.close()
