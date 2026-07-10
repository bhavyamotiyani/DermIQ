from app.models import db, Product
from textblob import TextBlob
from sqlalchemy import or_

class RecommendationService:
    @staticmethod
    def get_expert_advice(skin_type, concerns):
        """
        Maps skin type and concerns to recommended ingredients, contraindications, and clinical protocol.
        """
        advice_map = {
            'acne': {
                'use': ['Salicylic Acid', 'Niacinamide', 'Zinc PCA'],
                'avoid': ['Isopropyl Myristate', 'Coconut Oil', 'Lanolin'],
                'protocol': 'Acne & Sebum Control'
            },
            'dryness': {
                'use': ['Hyaluronic Acid', 'Ceramides', 'Glycerin', 'Squalane'],
                'avoid': ['Denatured Alcohol', 'Alcohol Denat', 'Sodium Lauryl Sulfate (SLS)'],
                'protocol': 'Barrier Repair & Deep Hydration'
            },
            'dark spots': {
                'use': ['Vitamin C', 'Alpha Arbutin', 'Kojic Acid', 'Glycolic Acid'],
                'avoid': ['Fragrance', 'Essential Oils'],
                'protocol': 'Hyper-Pigmentation Correction'
            },
            'aging': {
                'use': ['Retinol', 'Peptides', 'Coenzyme Q10', 'Niacinamide'],
                'avoid': ['Harsh Physical Scrubs', 'Drying Alcohols'],
                'protocol': 'Collagen Restoration & Anti-Aging'
            },
            'redness': {
                'use': ['Centella Asiatica (Cica)', 'Panthenol', 'Allantoin'],
                'avoid': ['Synthetic Fragrance', 'Parfum', 'Physical Exfoliant Scrubs'],
                'protocol': 'Soothing & Skin Recovery'
            },
            'pores': {
                'use': ['Niacinamide', 'Salicylic Acid (BHA)', 'Clay'],
                'avoid': ['Heavy Comedogenic Silicones', 'Heavy Waxes'],
                'protocol': 'Pore Refining & Texture Smoothing'
            }
        }

        use_ingredients = set()
        avoid_ingredients = set()
        protocols = []

        # Process each concern
        if concerns:
            for concern in concerns:
                c_lower = concern.lower().strip()
                if c_lower in advice_map:
                    use_ingredients.update(advice_map[c_lower]['use'])
                    avoid_ingredients.update(advice_map[c_lower]['avoid'])
                    protocols.append(advice_map[c_lower]['protocol'])

        # Process skin type considerations
        st_lower = (skin_type or '').lower().strip()
        if st_lower == 'sensitive':
            use_ingredients.update(['Panthenol', 'Allantoin', 'Ceramides'])
            avoid_ingredients.update(['Fragrance', 'Parfum', 'Denatured Alcohol', 'Alcohol Denat'])
            protocols.append('Sensitive Skin Protection')
        elif st_lower == 'dry':
            use_ingredients.update(['Hyaluronic Acid', 'Ceramides', 'Squalane'])
            avoid_ingredients.update(['Salicylic Acid', 'Drying Alcohols'])
            protocols.append('Intense Nourishment')
        elif st_lower == 'oily':
            use_ingredients.update(['Salicylic Acid', 'Niacinamide'])
            avoid_ingredients.update(['Heavy Mineral Oils', 'Comedogenic Butters'])
            protocols.append('Sebum Regulation')

        # Defaults if empty
        if not use_ingredients:
            use_ingredients = {'Niacinamide', 'Hyaluronic Acid', 'Glycerin'}
        if not avoid_ingredients:
            avoid_ingredients = {'Harsh Sulfates', 'Synthetic Dyes'}
        if not protocols:
            protocols = ['General Skin Balance Regimen']

        return {
            'protocol': ' & '.join(list(set(protocols))[:2]),
            'to_use': list(use_ingredients)[:3],
            'to_avoid': list(avoid_ingredients)[:3]
        }

    @staticmethod
    def calculate_compatibility_score(user_skin_type, user_concerns, user_sensitivity, product):
        """
        Calculates compatibility score (0-100) based on:
          1. Skin Type Match (35 pts)
          2. Concern Match (30 pts)
          3. Ingredient Check (25 pts)
          4. Rating & Sentiment Polarity (10 pts)
        """
        score = 0.0
        
        # --- 1. Skin Type Match (35 Points) ---
        user_st = (user_skin_type or 'normal').lower().strip()
        prod_suit = (product.suitable_for or 'all').lower().strip()
        
        if prod_suit == 'all' or user_st in prod_suit:
            score += 35.0
        elif user_st == 'combination' and ('oily' in prod_suit or 'dry' in prod_suit):
            score += 25.0
        elif user_st == 'sensitive' and 'sensitive' not in prod_suit:
            score += 15.0  # Safe but not optimized
        else:
            score += 10.0  # Default low match

        # --- 2. Skin Concern Match (30 Points) ---
        prod_concerns = [c.lower().strip() for c in (product.concerns or '').split(',') if c.strip()]
        if user_concerns:
            matched_concerns = 0
            for concern in user_concerns:
                c_lower = concern.lower().strip()
                if c_lower in prod_concerns:
                    matched_concerns += 1
            if matched_concerns > 0:
                score += (matched_concerns / len(user_concerns)) * 30.0
            else:
                score += 10.0  # Neutral match
        else:
            score += 15.0  # Neutral score if user hasn't specified concerns

        # --- 3. Ingredient Check (25 Points) ---
        advice = RecommendationService.get_expert_advice(user_skin_type, user_concerns)
        prod_ingredients = (product.ingredients or '').lower()
        
        ingredient_pts = 0.0
        for ing in advice['to_use']:
            if ing.lower() in prod_ingredients:
                ingredient_pts += 10.0  # 10 pts per matched active ingredient
        
        score += min(25.0, ingredient_pts)
        
        # Apply contraindication penalty
        for ing_avoid in advice['to_avoid']:
            if ing_avoid.lower() in prod_ingredients:
                score -= 15.0  # Penalty for bad ingredients
                
        # Also apply user sensitivity preference check
        if user_sensitivity and user_sensitivity.lower() == 'sensitive':
            # Check for general irritants
            for irritant in ['alcohol denat', 'denatured alcohol', 'fragrance', 'parfum', 'sulfate']:
                if irritant in prod_ingredients:
                    score -= 10.0

        # --- 4. Rating & Sentiment Polarity (10 Points) ---
        # Rating (5 points)
        rating_val = product.rating or 4.0
        score += (rating_val / 5.0) * 5.0
        
        # Sentiment Polarity (5 points)
        blob = TextBlob(product.description or '')
        polarity = blob.sentiment.polarity # -1.0 to 1.0
        sentiment_score = ((polarity + 1.0) / 2.0) * 5.0
        score += sentiment_score

        # Bound score between 0 and 100
        return max(0.0, min(100.0, round(score, 1)))

    @classmethod
    def generate_routine(cls, user):
        """
        Compiles a personalized daily routine separated into Morning (Cleanser, Toner, Vitamin C Serum, Sunscreen)
        and Night (Cleanser, Toner, Treatment Serum, Moisturizer) optimized under the user's budget.
        """
        user_st = user.skin_type
        user_concerns = user.get_concerns()
        user_sensitivity = user.sensitivity
        user_budget = user.budget

        # Fetch products matching categories
        # 1. Cleansers
        cleanser_prods = Product.query.filter(Product.category.ilike('%Cleanser%')).all()
        # 2. Toners
        toner_prods = Product.query.filter(Product.category.ilike('%Toner%')).all()
        # 3. Serums (general pool for filtering and fallbacks)
        serums = Product.query.filter(Product.category.ilike('%Serum%')).all()
        
        # 4. Vitamin C Serums
        vit_c_serums = [p for p in serums if any(x in f"{p.name} {p.ingredients or ''} {p.description or ''}".lower() for x in ['vitamin c', 'ascorbic', 'c-ester', 'c-'])]
        if not vit_c_serums:
            vit_c_serums = serums
            
        # 5. Sunscreens
        sunscreen_prods = Product.query.filter(or_(Product.category.ilike('%Sunscreen%'), Product.category.ilike('%SPF%'), Product.name.ilike('%Sunscreen%'), Product.name.ilike('%SPF%'))).all()
        if not sunscreen_prods:
            sunscreen_prods = Product.query.all()
            
        # 6. Treatment Serums (BHA/Salicylic Acid for Acne/Pores/Oily, otherwise Retinol/Anti-Aging)
        is_oily_or_acne = any(x in [c.lower().strip() for c in user_concerns] for x in ['acne', 'pores']) or (user_st or '').lower() == 'oily'
        if is_oily_or_acne:
            treatment_serums = [p for p in serums if any(x in f"{p.name} {p.ingredients or ''} {p.description or ''}".lower() for x in ['salicylic', 'bha', 'acne', 'clarifying'])]
        else:
            treatment_serums = [p for p in serums if any(x in f"{p.name} {p.ingredients or ''} {p.description or ''}".lower() for x in ['retinol', 'aging', 'anti-aging', 'night'])]
        if not treatment_serums:
            treatment_serums = serums
            
        # 7. Moisturizers
        moisturizer_prods = Product.query.filter(Product.category.ilike('%Moisturizer%')).all()

        categories = ['Cleanser', 'Toner', 'Vitamin C Serum', 'Sunscreen', 'Treatment Serum', 'Moisturizer']
        raw_candidates = {
            'Cleanser': cleanser_prods,
            'Toner': toner_prods,
            'Vitamin C Serum': vit_c_serums,
            'Sunscreen': sunscreen_prods,
            'Treatment Serum': treatment_serums,
            'Moisturizer': moisturizer_prods
        }

        # Calculate scores and sort candidates
        candidates = {}
        all_products = Product.query.all()
        for cat in categories:
            scored_list = []
            for p in raw_candidates[cat]:
                if p not in scored_list:
                    score = cls.calculate_compatibility_score(user_st, user_concerns, user_sensitivity, p)
                    p.compatibility_score = score
                    scored_list.append(p)
            scored_list.sort(key=lambda x: x.compatibility_score, reverse=True)
            candidates[cat] = scored_list

            # Safe fallback if category is completely empty
            if not candidates[cat]:
                scored_fallback = []
                for p in all_products:
                    score = cls.calculate_compatibility_score(user_st, user_concerns, user_sensitivity, p)
                    p.compatibility_score = score
                    scored_fallback.append(p)
                scored_fallback.sort(key=lambda x: x.compatibility_score, reverse=True)
                candidates[cat] = scored_fallback

        # Optimize budget over 6 unique products
        # Limit search space to top 4 of each for speed (4^6 = 4096 loops)
        opt_limit = 4
        cleansers = candidates['Cleanser'][:opt_limit]
        toners = candidates['Toner'][:opt_limit]
        vit_cs = candidates['Vitamin C Serum'][:opt_limit]
        sunscreens = candidates['Sunscreen'][:opt_limit]
        treatment_serums = candidates['Treatment Serum'][:opt_limit]
        moisturizers = candidates['Moisturizer'][:opt_limit]

        selected_combination = None
        best_sum_score = -1.0

        for c in cleansers:
            for t in toners:
                for v in vit_cs:
                    for s in sunscreens:
                        for ts in treatment_serums:
                            for m in moisturizers:
                                total_price = c.price + t.price + v.price + s.price + ts.price + m.price
                                if total_price <= user_budget:
                                    sum_score = (c.compatibility_score + t.compatibility_score + 
                                                 v.compatibility_score + s.compatibility_score + 
                                                 ts.compatibility_score + m.compatibility_score)
                                    if sum_score > best_sum_score:
                                        best_sum_score = sum_score
                                        selected_combination = (c, t, v, s, ts, m)

        # Fallback: if no combination fits budget, find combination that minimizes budget overshoot
        if not selected_combination:
            cheapest_combination = None
            min_price = float('inf')
            for c in cleansers[:3]:
                for t in toners[:3]:
                    for v in vit_cs[:3]:
                        for s in sunscreens[:3]:
                            for ts in treatment_serums[:3]:
                                for m in moisturizers[:3]:
                                    total_price = c.price + t.price + v.price + s.price + ts.price + m.price
                                    if total_price < min_price:
                                        min_price = total_price
                                        cheapest_combination = (c, t, v, s, ts, m)
            selected_combination = cheapest_combination

        # Absolute fallback if lists were somehow empty
        if not selected_combination:
            selected_combination = (
                candidates['Cleanser'][0] if candidates['Cleanser'] else None,
                candidates['Toner'][0] if candidates['Toner'] else None,
                candidates['Vitamin C Serum'][0] if candidates['Vitamin C Serum'] else None,
                candidates['Sunscreen'][0] if candidates['Sunscreen'] else None,
                candidates['Treatment Serum'][0] if candidates['Treatment Serum'] else None,
                candidates['Moisturizer'][0] if candidates['Moisturizer'] else None
            )

        primary_cleanser = selected_combination[0]
        primary_toner = selected_combination[1]
        primary_vit_c = selected_combination[2]
        primary_sunscreen = selected_combination[3]
        primary_treatment_serum = selected_combination[4]
        primary_moisturizer = selected_combination[5]

        # Retrieve alternatives helper
        def get_products_list(cat, primary_product):
            if not primary_product:
                return candidates[cat][:3]
            alts = [p for p in candidates[cat] if p.id != primary_product.id]
            return [primary_product] + alts[:2]

        # Determine Treatment Serum Purpose based on selection
        ts_purpose = "Targets specific skin concerns with active ingredients overnight."
        if primary_treatment_serum:
            ts_name = primary_treatment_serum.name.lower()
            ts_ing = (primary_treatment_serum.ingredients or '').lower()
            if 'salicylic' in ts_name or 'salicylic' in ts_ing or 'bha' in ts_name or 'bha' in ts_ing:
                ts_purpose = "Exfoliates pores, refines skin texture, and targets acne blemishes."
            elif 'retinol' in ts_name or 'retinol' in ts_ing or 'aging' in ts_name or 'aging' in ts_ing:
                ts_purpose = "Supports cell turnover, improves elasticity, and targets aging signs."

        # Compile final routines
        routine = {
            'morning': [
                {
                    'step': 1,
                    'category': 'Cleanser',
                    'purpose': 'Removes dirt, excess oil, and impurities accumulated overnight.',
                    'products': get_products_list('Cleanser', primary_cleanser)
                },
                {
                    'step': 2,
                    'category': 'Toner',
                    'purpose': 'Balances skin pH, refines pores, and preps skin.',
                    'products': get_products_list('Toner', primary_toner)
                },
                {
                    'step': 3,
                    'category': 'Vitamin C Serum',
                    'purpose': 'Brightens skin tone, fades dark spots, and provides antioxidant defense.',
                    'products': get_products_list('Vitamin C Serum', primary_vit_c)
                },
                {
                    'step': 4,
                    'category': 'Sunscreen',
                    'purpose': 'Shields skin from UV rays and prevents premature aging.',
                    'products': get_products_list('Sunscreen', primary_sunscreen)
                }
            ],
            'night': [
                {
                    'step': 1,
                    'category': 'Cleanser',
                    'purpose': 'Deeply cleanses to remove dirt, sebum, makeup, and daily pollutants.',
                    'products': get_products_list('Cleanser', primary_cleanser)
                },
                {
                    'step': 2,
                    'category': 'Toner',
                    'purpose': 'Hydrates, calms, and prepares skin for intensive overnight treatment.',
                    'products': get_products_list('Toner', primary_toner)
                },
                {
                    'step': 3,
                    'category': 'Treatment Serum',
                    'purpose': ts_purpose,
                    'products': get_products_list('Treatment Serum', primary_treatment_serum)
                },
                {
                    'step': 4,
                    'category': 'Moisturizer',
                    'purpose': 'Hydrates and seals in moisture to support skin barrier repair overnight.',
                    'products': get_products_list('Moisturizer', primary_moisturizer)
                }
            ]
        }
        return routine

    @classmethod
    def get_dermiq_analysis(cls, user_skin_type, user_concerns, user_sensitivity, user_budget, product):
        """
        Calculates a dynamic compatibility score (0-100) and returns detailed analysis report.
        """
        user_st = (user_skin_type or 'normal').lower().strip()
        prod_suit = (product.suitable_for or 'all').lower().strip()
        
        # 1. Skin Type Match (30 points)
        skin_type_matched = False
        if prod_suit == 'all' or user_st in prod_suit:
            skin_type_score = 30.0
            skin_type_matched = True
        elif user_st == 'combination' and ('oily' in prod_suit or 'dry' in prod_suit):
            skin_type_score = 20.0
            skin_type_matched = True
        elif user_st == 'sensitive' and 'sensitive' not in prod_suit:
            skin_type_score = 10.0
        else:
            skin_type_score = 5.0

        # 2. Concern Match (30 points)
        concern_score = 0.0
        concern_matched = False
        prod_concerns = [c.lower().strip() for c in (product.concerns or '').split(',') if c.strip()]
        if user_concerns:
            matched_count = 0
            for concern in user_concerns:
                c_lower = concern.lower().strip()
                if c_lower in prod_concerns:
                    matched_count += 1
            if matched_count > 0:
                concern_score = (matched_count / len(user_concerns)) * 30.0
                concern_matched = True
            else:
                concern_score = 5.0
        else:
            concern_score = 15.0 # Neutral

        # 3. Ingredient Compatibility (20 points)
        ingredient_score = 0.0
        ingredients_matched = False
        advice = cls.get_expert_advice(user_skin_type, user_concerns)
        prod_ingredients = (product.ingredients or '').lower()
        
        use_matches = 0
        for ing in advice['to_use']:
            if ing.lower() in prod_ingredients:
                use_matches += 1
                ingredient_score += 10.0
        
        if use_matches > 0:
            ingredients_matched = True
        
        ingredient_score = min(20.0, ingredient_score)
        
        # Penalty for contraindications
        avoid_matches = 0
        for ing_avoid in advice['to_avoid']:
            if ing_avoid.lower() in prod_ingredients:
                ingredient_score -= 10.0
                avoid_matches += 1
        
        # User sensitivity checks
        if user_sensitivity and user_sensitivity.lower() == 'sensitive':
            for irritant in ['alcohol denat', 'denatured alcohol', 'fragrance', 'parfum', 'sulfate']:
                if irritant in prod_ingredients:
                    ingredient_score -= 5.0
                    
        ingredient_score = max(0.0, min(20.0, ingredient_score))

        # 4. Budget Compatibility (20 points)
        budget_matched = False
        if product.price <= user_budget:
            budget_score = 20.0
            budget_matched = True
        else:
            budget_score = max(0.0, 20.0 * (user_budget / product.price))
            if budget_score >= 10.0:
                budget_matched = True

        total_score = round(skin_type_score + concern_score + ingredient_score + budget_score, 1)
        total_score = max(0.0, min(100.0, total_score))

        # Confidence Level
        if total_score >= 80:
            confidence = "High"
        elif total_score >= 55:
            confidence = "Medium"
        else:
            confidence = "Low"

        # Reason Generation
        matches = []
        if skin_type_matched: matches.append("skin type")
        if concern_matched: matches.append("concerns")
        if ingredients_matched: matches.append("ingredient preferences")
        if budget_matched: matches.append("budget")

        if len(matches) == 4:
            reason = "Recommended because this product matches your skin type, concerns, ingredient preferences, and budget."
        elif len(matches) >= 2:
            reason = f"Recommended because this product matches your {', '.join(matches[:-1])} and {matches[-1]}."
        elif len(matches) == 1:
            reason = f"Suitable because this product matches your {matches[0]}, though it may not align with other profile markers."
        else:
            reason = "This product has low compatibility with your profile but is available as a general skincare option."

        return {
            'score': int(total_score),
            'confidence': confidence,
            'reason': reason,
            'skin_type': user_skin_type.title() if user_skin_type else 'Normal',
            'concerns': [c.title() for c in user_concerns] if user_concerns else ['General Health']
        }
