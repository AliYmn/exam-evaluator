def get_image_prompt(title: str, image_type: str, language: str = "en") -> str:
    if language == "tr":
        if image_type == "blog":
            return (
                f"'{title}' başlığını temsil eden, sağlıklı yaşam, iyi hissetme ve beslenme temalarını çağrıştıran, profesyonel ve yüksek kaliteli bir konsept görseli. "
                + "Metin, filigran veya insan yüzü olmasın. Temiz, modern ve canlı bir tarz kullan."
            )
        elif image_type == "recipe":
            return (
                f"'{title}' adlı yemeği iştah açıcı, sağlıklı ve şık bir şekilde sunan profesyonel bir yemek fotoğrafı tarzında görsel. "
                + "Metin, filigran veya insan olmasın. Doğal ışık ve temiz arka plan kullan."
            )
        else:
            return f"'{title}' başlığını temsil eden yaratıcı ve yüksek kaliteli bir görsel. Metin, filigran veya insan olmasın."
    else:
        if image_type == "blog":
            return (
                f"A professional, high-quality conceptual image representing '{title}'. "
                + "The image should evoke themes of healthy lifestyle, wellness, and nutrition. "
                + "No text, no watermarks, no people. Use a clean, modern, and vibrant style."
            )
        elif image_type == "recipe":
            return (
                f"A professional food photography style image of '{title}'. "
                + "The dish should look appetizing, healthy, and beautifully plated. "
                + "No text, no watermarks, no people. Use natural lighting and a clean background."
            )
        else:
            return f"A creative, high-quality image representing '{title}'. No text, no watermarks, no people."


def get_blog_prompt_en(recent_titles):
    prompt = (
        "Use at least one relevant emoji in every major section, heading, or tip. Emojis should enhance explanation, illustrate steps, and make the content visually engaging. For example: 🥗, 💪, 🍽️, 🕒.\n\n"
        "Choose a fresh, captivating, and reader-focused topic in the areas of intermittent fasting, nutrition, or overall wellness. "
        "You may explore—but are not limited to—topics like:\n"
        "- Intermittent fasting methods (16/8, OMAD, 5:2, etc.)\n"
        "- Latest scientific studies in nutrition and fasting (cite 2023–2025)\n"
        "- Health effects (benefits & risks) of intermittent fasting\n"
        "- Nutrition myths vs. facts\n"
        "- Roles of macro/micronutrients\n"
        "- Gut health and microbiome science\n"
        "- Meal timing, eating windows, and circadian rhythm\n"
        "- Practical, actionable advice for readers\n"
        "- Real-life success stories\n"
        "- Seasonal or trending nutrition topics\n\n"
        "Your blog post must include:\n"
        "1. A catchy, unique, and emoji-supported title\n"
        "2. Engaging introduction with at least one emoji\n"
        "3. Well-structured sections (H2/H3 headings)\n"
        "4. At least one emoji per section or step\n"
        "5. Actionable tips and real-life examples\n"
        "6. Research citations (2023–2025)\n"
        "7. Myth-busting or surprising facts\n"
        "8. Friendly, motivating, and clear style\n"
        "9. Summary or key takeaways, with an emoji\n"
        "10. Return the response in this JSON format:\n"
        "{\n"
        "    'title': 'Creative and appetizing blog title',\n"
        "    'content': 'Full blog content in Markdown (1000–1500 words)',\n"
        "    'summary': 'Brief summary (max 150 words)',\n"
        "    'category': 'Blog category (e.g., Nutrition, Intermittent Fasting)',\n"
        "    'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']\n"
        "}"
    )
    if recent_titles:
        prompt += (
            "\n\nRecently covered blog titles (avoid similar topics and don't use!):\n"
            + "\n".join(f"- {title}" for title in recent_titles)
            + "\nPlease do not repeat or closely mimic these."
        )
    return prompt


def get_blog_prompt_tr(recent_titles):
    prompt = (
        "Her ana bölümde, başlıkta ve önemli adımda uygun ve yaratıcı bir emoji kullan. Emojiler açıklamaları daha anlaşılır ve dikkat çekici hale getirmeli. Örneğin: 🥗, 💪, 🍽️, 🕒.\n\n"
        "Aralıklı oruç (intermittent fasting), sağlıklı beslenme veya beslenme bilimiyle ilgili özgün, güncel ve dikkat çekici bir konu seç. "
        "Aşağıdaki konu başlıkları ilham verebilir:\n"
        "- Aralıklı oruç türleri (16/8, 5:2, OMAD vb.)\n"
        "- 2023–2025 yılları arasında yayınlanan güncel bilimsel çalışmalar\n"
        "- Aralıklı orucun faydaları ve olası riskleri\n"
        "- Sağlıklı beslenmenin temel ilkeleri ve yaygın yanlışlar\n"
        "- Makro/mikro besinlerin rolleri\n"
        "- Bağırsak sağlığı ve mikrobiyota\n"
        "- Öğün zamanlaması ve sirkadiyen ritim\n"
        "- Pratik, uygulanabilir öneriler\n"
        "- Gerçek yaşamdan başarı hikâyeleri\n"
        "- Mevsimsel veya popüler beslenme konuları\n\n"
        "Blog yazısı şunları içermeli:\n"
        "1. Yaratıcı, dikkat çekici ve emojili bir başlık\n"
        "2. Giriş bölümünde en az bir emoji\n"
        "3. H2/H3 başlıklarla iyi yapılandırılmış bölümler\n"
        "4. Her bölümde veya önemli adımda en az bir emoji\n"
        "5. Uygulanabilir öneriler ve gerçek örnekler\n"
        "6. Bilimsel kaynaklar (2023–2025)\n"
        "7. Efsane çürütme veya şaşırtıcı bilgiler\n"
        "8. Samimi, motive edici ve anlaşılır bir anlatım\n"
        "9. Özet veya ana çıkarımlar, emojili\n"
        "10. Return the response in this JSON format:\n"
        "{\n"
        "    'title': 'Yaratıcı ve iştah açıcı blog başlığı',\n"
        "    'content': 'Markdown formatında 1000–1500 kelimelik tam blog içeriği',\n"
        "    'summary': 'Kısa özet (en fazla 150 kelime)',\n"
        "    'category': 'Kategori (Beslenme, Aralıklı Oruç vb.)',\n"
        "    'tags': ['etiket1', 'etiket2', 'etiket3', 'etiket4', 'etiket5']\n"
        "}"
    )
    if recent_titles:
        prompt += (
            "\n\nSon yazılan başlıklar (bu konulardan kaçın ve kullanma!):\n"
            + "\n".join(f"- {title}" for title in recent_titles)
            + "\nBu başlıklara benzer içerikler üretme."
        )
    return prompt


def get_recipe_prompt_en(recent_titles=None):
    prompt = (
        "Use at least one relevant emoji in every major section, step, or tip. Emojis should enhance explanation, illustrate steps, and make the recipe visually engaging. For example: 🥗, 💪, 🍽️, 🕒.\n\n"
        "Create a unique, nutrient-rich recipe tailored for individuals who follow a healthy lifestyle — especially those doing intermittent fasting, working out, or eating clean. "
        "The recipe should be suitable for active people and those managing their weight, with a focus on high protein, low/moderate carbs, healthy fats, and whole ingredients.\n\n"
        "You may be inspired by styles such as:\n"
        "- Post-workout high-protein meals\n"
        "- Low-carb Mediterranean/Turkish-style bowls\n"
        "- Sugar-free and gluten-free healthy alternatives\n"
        "- Oven-baked or air-fried traditional recipes with a healthy twist\n"
        "- Energy-boosting breakfasts or clean snacks for athletes\n\n"
        "**Your recipe must include:**\n"
        "1. Accessible ingredients tailored to fitness and health 🥬\n"
        "2. A motivating backstory or inspiration (especially fitness or cultural relevance)\n"
        "3. Step-by-step clear instructions\n"
        "4. At least one emoji per step or section\n"
        "5. Nutritional facts (calories, protein, carbs, fat per serving)\n"
        "6. Best meal timing (e.g., post-workout, fast-breaking)\n"
        "7. Substitutes and allergy-friendly modifications\n"
        "8. Descriptive, encouraging tone 💪\n"
        "9. Visual/sensory descriptions (color, aroma, texture)\n"
        "10. Prep time, cook time, servings, storage tips\n"
        "11. A surprising nutrition tip or myth-busting fact\n"
        "12. Practical fitness-nutrition connection advice where possible\n"
        "13. Respond in this JSON format:\n"
        "{\n"
        "    'title': 'Creative, fitness-focused recipe title',\n"
        "    'content': 'Full Markdown content including intro, ingredients, steps, and nutritional info',\n"
        "    'summary': 'Brief summary (max 150 words)',\n"
        "    'category': 'Fitness Recipes',\n"
        "    'tags': ['fitness', 'high-protein', 'clean-eating', 'healthy-meal', 'nutrition']\n"
        "}"
    )
    if recent_titles:
        prompt += (
            "\n\nRecently generated recipe titles (avoid these):\n"
            + "\n".join(f"- {title}" for title in recent_titles)
            + "\nAvoid repetition and aim for unique content."
        )
    return prompt


def get_recipe_prompt_tr(recent_titles=None):
    prompt = (
        "Her ana bölümde, adımda ve ipucunda uygun ve yaratıcı bir emoji kullan. Emojiler açıklamaları daha anlaşılır ve dikkat çekici hale getirmeli. Örneğin: 🥗, 💪, 🍽️, 🕒.\n\n"
        "Spor yapanlar, diyet uygulayanlar veya sağlıklı beslenmeyi yaşam tarzı haline getirenler için özel, Türk mutfağı temelli bir tarif oluştur. "
        "Tarifin hem geleneksel Türk yemeklerinden esinlenmeli, hem de yüksek protein, düşük karbonhidrat, sağlıklı yağ ve dengeli kalori değerleri sunmalı.\n\n"
        "Aşağıdaki alanlar ilham verebilir:\n"
        "- Spor sonrası toparlanmayı destekleyen yüksek proteinli tarifler\n"
        "- Karbonhidratı dengelenmiş hafif Türk yemekleri\n"
        "- Glütensiz, düşük yağlı veya şekersiz versiyonlar\n"
        "- Fırında veya haşlama yöntemleriyle pişirilen klasikler\n"
        "- Diyet dostu kahvaltılıklar, atıştırmalıklar veya öğünler\n\n"
        "**Tarifin içermesi gerekenler:**\n"
        "1. Sporcular ve sağlıklı beslenen bireyler için uygun, ulaşılabilir malzemeler 🥗\n"
        "2. Türk mutfağına özgü kültürel bağlantı veya kişisel ilham kaynağı\n"
        "3. Adım adım net hazırlanış aşamaları\n"
        "4. Her adımda veya ana bölümde en az bir emoji\n"
        "5. Kalori ve makro besin değerleri (protein, karbonhidrat, yağ)\n"
        "6. Spor öncesi veya sonrası için uygun öğün zamanı önerisi\n"
        "7. Alerji dostu ve kişiselleştirilebilir versiyonlar\n"
        "8. Samimi ve açıklayıcı bir anlatım 💪\n"
        "9. Görsel/sensörlük açıklamalar (renk, doku, aroma)\n"
        "10. Hazırlık süresi, pişirme süresi, porsiyon sayısı ve saklama önerileri\n"
        "11. Beslenme efsanesini çürüten veya şaşırtıcı bir bilgi\n"
        "12. İçerikte sağlıklı yaşamla bağ kuran bilinçli öneriler\n"
        "13. Yanıtını şu JSON formatında ver:\n"
        "{\n"
        "    'title': 'Sporcu ve sağlıklı yaşam odaklı tarif başlığı (Basliklarda Türk kelimesi bulunmasin)',\n"
        "    'content': 'Markdown formatında tam tarif içeriği',\n"
        "    'summary': 'Kısa özet (en fazla 150 kelime)',\n"
        "    'category': 'Sporcu Tarifleri',\n"
        "    'tags': ['fitness', 'protein', 'diyet', 'turk-mutfagi', 'saglikli-yasam']\n"
        "}"
    )
    if recent_titles:
        prompt += (
            "\n\nSon oluşturulan tarif başlıkları (bunlardan kaçın):\n"
            + "\n".join(f"- {title}" for title in recent_titles)
            + "\nBenzer içeriklerden kaçın ve özgün tarifler oluştur."
        )
    return prompt


def get_blog_system_content_en():
    return (
        "You are a professional content creator with deep expertise in health, nutrition, and intermittent fasting. "
        "You create informative, actionable, and inspiring blog posts backed by the latest science (2023–2025). "
        "Your style is direct, friendly, motivating, and relatable. Each blog post must be unique, include evidence, and offer practical steps. "
        "Avoid repetition. Use vivid language, real-life examples, and keep your tone fresh and empowering. "
        "Emojis must be used creatively and frequently in every major section, heading, and tip to enhance clarity, engagement, and visual appeal. For example: 🥗, 💪, 🍽️, 🕒."
    )


def get_blog_system_content_tr():
    return (
        "Sen sağlıklı yaşam, beslenme ve aralıklı oruç alanında uzman bir içerik üreticisisin. "
        "Her yazın güncel bilimsel kaynaklara (2023–2025) dayanmalı, özgün, bilgilendirici, uygulanabilir ve ilham verici olmalı. "
        "Tarzın samimi, motive edici ve anlaşılır olmalı. Her blog yazısı benzersiz, kanıta dayalı ve pratik öneriler içermeli. "
        "Tekrardan kaçın. Canlı bir dil kullan, gerçek örneklerle anlat ve okuyucuyu harekete geçir. "
        "Her ana bölümde, başlıkta ve önemli adımda emojiler yaratıcı ve sık şekilde kullanılmalı. Emojiler açıklamaları daha anlaşılır ve dikkat çekici hale getirmeli. Örneğin: 🥗, 💪, 🍽️, 🕒."
    )


def get_recipe_system_content_en():
    return (
        "You are a creative and health-focused recipe creator. "
        "Your recipes are always delicious, easy to follow, and adapted for intermittent fasting or healthy lifestyles. "
        "You highlight cultural stories, provide alternatives, and include nutritional insights. "
        "Your tone is inviting and descriptive. Each recipe should feel fresh, unique, and inspiring to try. "
        "Emojis must be used creatively and frequently in every major section, step, and tip to enhance clarity, engagement, and visual appeal. For example: 🥗, 💪, 🍽️, 🕒."
    )


def get_recipe_system_content_tr():
    return (
        "Sen aralıklı oruç ve sağlıklı yaşam odaklı tarifler konusunda uzman, yaratıcı bir tarif yazarı ve şefsin. "
        "Tariflerin besleyici, lezzetli, uygulanabilir ve özgün olmalı. "
        "Görsel detaylara, kültürel arka plana, malzeme alternatiflerine ve besin bilgilerine yer vermelisin. "
        "Okuyucuların kolayca uygulayabileceği netlikte ve samimiyette tarifler üretmelisin. "
        "Her ana bölümde, adımda ve önemli ipucunda emojiler yaratıcı ve sık şekilde kullanılmalı. Emojiler açıklamaları daha anlaşılır ve dikkat çekici hale getirmeli. Örneğin: 🥗, 💪, 🍽️, 🕒."
    )
