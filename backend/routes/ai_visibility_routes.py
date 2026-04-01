"""AI Visibility analysis route - Analyze URL for AI visibility and SEO insights"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId
import httpx
from bs4 import BeautifulSoup
import os
import logging

router = APIRouter(prefix="/api/ai-visibility", tags=["AI Visibility"])

db = None

def set_database(database):
    global db
    db = database

class UrlAnalysisRequest(BaseModel):
    url: str

async def scrape_url(url: str) -> dict:
    """Scrape basic information from a URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')][:5]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')][:10]
        
        # Count various elements
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        links = soup.find_all('a', href=True)
        internal_links = [l for l in links if not l['href'].startswith('http') or url in l['href']]
        external_links = [l for l in links if l['href'].startswith('http') and url not in l['href']]
        
        # Schema/structured data
        schema_scripts = soup.find_all('script', type='application/ld+json')
        
        # Text content
        body_text = soup.get_text(separator=' ', strip=True)[:3000]
        
        return {
            "title": title.get_text(strip=True) if title else "No title found",
            "meta_description": meta_desc['content'] if meta_desc and meta_desc.get('content') else "No meta description",
            "meta_keywords": meta_keywords['content'] if meta_keywords and meta_keywords.get('content') else "None",
            "h1_tags": h1_tags,
            "h2_tags": h2_tags,
            "total_images": len(images),
            "images_without_alt": len(images_without_alt),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "has_structured_data": len(schema_scripts) > 0,
            "word_count": len(body_text.split()),
            "body_text_preview": body_text[:1000]
        }
    except Exception as e:
        logging.error(f"Scraping error for {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not scrape URL: {str(e)}")

async def analyze_with_llm(scraped_data: dict, url: str) -> str:
    """Use Google Gemini 2.0 Flash to analyze the scraped data - Deep Report with retry"""
    from google import genai
    from google.genai import types
    import asyncio
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    system_instruction = """You are an expert SEO strategist and AI visibility analyst with deep knowledge of search engine algorithms, AI-powered search (Google SGE, Bing Copilot, Perplexity, ChatGPT Browse), and content optimization. 

You produce comprehensive, professional-grade audit reports that are data-driven, actionable, and cite real industry sources. Your reports are thorough — minimum one full page of detailed analysis covering every aspect of the website's SEO health and AI discoverability."""

    prompt = f"""Produce a COMPREHENSIVE and DETAILED AI Visibility & SEO Deep Audit Report for the following website. The report must be thorough (minimum one full page), professionally structured, and include citations to authoritative sources.

=== WEBSITE DATA ===
URL: {url}
Title: {scraped_data['title']}
Meta Description: {scraped_data['meta_description']}
Keywords: {scraped_data['meta_keywords']}
H1 Tags: {', '.join(scraped_data['h1_tags']) if scraped_data['h1_tags'] else 'None found'}
H2 Tags: {', '.join(scraped_data['h2_tags'][:8]) if scraped_data['h2_tags'] else 'None found'}
Total Images: {scraped_data['total_images']} (Missing Alt Text: {scraped_data['images_without_alt']})
Internal Links: {scraped_data['internal_links']}, External Links: {scraped_data['external_links']}
Has Structured Data (JSON-LD): {scraped_data['has_structured_data']}
Word Count: {scraped_data['word_count']}
Content Preview: {scraped_data['body_text_preview'][:800]}
=== END DATA ===

Return the analysis as a JSON object with these exact keys:
{{
  "overall_score": <number 0-100>,
  "seo_score": <number 0-100>,
  "ai_visibility_score": <number 0-100>,
  "content_quality_score": <number 0-100>,
  "technical_seo_score": <number 0-100>,
  "summary": "<A detailed 4-5 sentence executive summary of the site's overall SEO and AI visibility health>",
  "detailed_analysis": "<A comprehensive multi-paragraph deep analysis (minimum 800 words) covering: 1) On-Page SEO Assessment (title tags, meta descriptions, heading hierarchy, keyword usage, content depth), 2) Technical SEO Evaluation (structured data, page speed indicators, mobile-friendliness signals, internal linking structure, crawlability), 3) AI Visibility & Discoverability (how well the site is optimized for AI-powered search engines like Google SGE, Bing Copilot, Perplexity AI, and ChatGPT Browse — covering entity recognition, factual accuracy, structured data for AI, content formatting for snippet extraction), 4) Content Quality Assessment (E-E-A-T signals, content depth, uniqueness, readability), 5) Competitive Positioning (where this site likely stands vs industry benchmarks). Use paragraph breaks with double newlines for readability.>",
  "strengths": ["<detailed strength 1>", "<detailed strength 2>", "<detailed strength 3>", "<detailed strength 4>", "<detailed strength 5>"],
  "improvements": ["<specific actionable improvement 1>", "<improvement 2>", "<improvement 3>", "<improvement 4>", "<improvement 5>", "<improvement 6>"],
  "ai_recommendations": ["<specific recommendation for AI search visibility 1>", "<recommendation 2>", "<recommendation 3>", "<recommendation 4>", "<recommendation 5>"],
  "keyword_suggestions": ["<keyword 1>", "<keyword 2>", "<keyword 3>", "<keyword 4>", "<keyword 5>", "<keyword 6>", "<keyword 7>", "<keyword 8>"],
  "citations": [
    {{"source": "<Source name e.g. Google Search Central>", "url": "<URL>", "context": "<How this source is relevant>"}},
    {{"source": "<Source name>", "url": "<URL>", "context": "<Relevance>"}},
    {{"source": "<Source name>", "url": "<URL>", "context": "<Relevance>"}},
    {{"source": "<Source name>", "url": "<URL>", "context": "<Relevance>"}},
    {{"source": "<Source name>", "url": "<URL>", "context": "<Relevance>"}}
  ]
}}

IMPORTANT: Return ONLY valid JSON. No markdown code fences. Ensure the detailed_analysis field contains a thorough multi-paragraph report."""

    max_retries = 3
    last_error = None
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                max_output_tokens=8192,
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            logging.warning(f"Gemini attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if "api key" in error_msg or "permission" in error_msg or "invalid" in error_msg:
                raise HTTPException(status_code=401, detail="Gemini API key is invalid or expired. Please check your API key.")
            if "resource_exhausted" in error_msg or "quota" in error_msg or "429" in error_msg:
                raise HTTPException(status_code=429, detail="Gemini API quota exceeded. Please check your Google AI Studio plan and billing details at https://ai.google.dev/gemini-api/docs/rate-limits")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 * (attempt + 1))
    
    raise HTTPException(status_code=503, detail="AI analysis temporarily unavailable. Please try again in a moment.")

@router.post("/analyze")
async def analyze_url(request: UrlAnalysisRequest, user_id: str = Depends(get_current_user_id)):
    """Analyze a URL for AI visibility and SEO insights"""
    
    # Check plan limits for AI Visibility
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = user.get("plan", "Starter")
    trial_active = user.get("trial_ends_at") and user["trial_ends_at"] > datetime.utcnow()
    
    if plan == "Starter" and not trial_active:
        # Starter plan (post-trial): 1 analysis per month
        from datetime import timedelta
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        usage_count = await db.ai_visibility_analyses.count_documents({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": month_start}
        })
        if usage_count >= 1:
            raise HTTPException(
                status_code=403,
                detail="AI_VISIBILITY_LIMIT_REACHED: Starter plan allows 1 AI Visibility analysis per month. Upgrade to Business Pro for unlimited analyses."
            )
    
    url = request.url.strip()
    if not url.startswith('http'):
        url = 'https://' + url
    
    # Scrape the URL
    try:
        scraped_data = await scrape_url(url)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Scraping failed for {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not access or scrape the URL. Please check the URL is correct and accessible.")
    
    # Analyze with LLM (has built-in retry)
    try:
        llm_response = await analyze_with_llm(scraped_data, url)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"LLM analysis failed for {url}: {str(e)}")
        raise HTTPException(status_code=503, detail="AI analysis temporarily unavailable. Please try again in a moment.")
    
    # Parse LLM response as JSON
    import json
    try:
        # Clean response - remove markdown code fences if present
        clean_response = llm_response.strip()
        if clean_response.startswith('```'):
            clean_response = clean_response.split('\n', 1)[1]
            clean_response = clean_response.rsplit('```', 1)[0]
        analysis = json.loads(clean_response)
    except json.JSONDecodeError:
        analysis = {
            "overall_score": 0,
            "seo_score": 0,
            "ai_visibility_score": 0,
            "content_quality_score": 0,
            "technical_seo_score": 0,
            "summary": llm_response[:500],
            "strengths": [],
            "improvements": [],
            "ai_recommendations": [],
            "keyword_suggestions": []
        }
    
    # Add scraped metadata
    analysis["scraped_data"] = {
        "title": scraped_data["title"],
        "meta_description": scraped_data["meta_description"],
        "total_images": scraped_data["total_images"],
        "images_without_alt": scraped_data["images_without_alt"],
        "internal_links": scraped_data["internal_links"],
        "external_links": scraped_data["external_links"],
        "has_structured_data": scraped_data["has_structured_data"],
        "word_count": scraped_data["word_count"]
    }
    
    # Save to DB
    analysis_doc = {
        "user_id": ObjectId(user_id),
        "url": url,
        "analysis": analysis,
        "created_at": datetime.utcnow()
    }
    await db.ai_visibility_analyses.insert_one(analysis_doc)
    
    return {"success": True, "url": url, "analysis": analysis}

@router.get("/history")
async def get_analysis_history(user_id: str = Depends(get_current_user_id)):
    """Get previous AI visibility analyses"""
    analyses = await db.ai_visibility_analyses.find(
        {"user_id": ObjectId(user_id)},
        {"_id": 0, "user_id": 0}
    ).sort("created_at", -1).to_list(20)
    
    for a in analyses:
        if "created_at" in a:
            a["created_at"] = a["created_at"].isoformat()
    
    return {"analyses": analyses}
