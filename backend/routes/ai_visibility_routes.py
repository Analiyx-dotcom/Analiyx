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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, verify=False) as client:
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
    """Use GPT-5.2 via emergentintegrations to analyze the scraped data"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM key not configured")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"ai-visibility-{datetime.utcnow().timestamp()}",
        system_message="""You are an expert SEO and AI visibility analyst. Analyze the provided website data and return a structured JSON analysis. Be specific, data-driven, and actionable. Return ONLY valid JSON with no markdown formatting."""
    )
    chat.with_model("openai", "gpt-5.2")
    
    prompt = f"""Analyze this website for AI visibility and SEO performance:

URL: {url}
Title: {scraped_data['title']}
Meta Description: {scraped_data['meta_description']}
Keywords: {scraped_data['meta_keywords']}
H1 Tags: {', '.join(scraped_data['h1_tags']) if scraped_data['h1_tags'] else 'None'}
H2 Tags: {', '.join(scraped_data['h2_tags'][:5]) if scraped_data['h2_tags'] else 'None'}
Images: {scraped_data['total_images']} (without alt: {scraped_data['images_without_alt']})
Internal Links: {scraped_data['internal_links']}, External Links: {scraped_data['external_links']}
Has Structured Data: {scraped_data['has_structured_data']}
Word Count: {scraped_data['word_count']}
Content Preview: {scraped_data['body_text_preview'][:500]}

Return analysis as JSON with these exact keys:
{{
  "overall_score": <number 0-100>,
  "seo_score": <number 0-100>,
  "ai_visibility_score": <number 0-100>,
  "content_quality_score": <number 0-100>,
  "technical_seo_score": <number 0-100>,
  "summary": "<2 sentence summary>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>", "<improvement 4>"],
  "ai_recommendations": ["<how to improve AI discoverability 1>", "<recommendation 2>", "<recommendation 3>"],
  "keyword_suggestions": ["<keyword 1>", "<keyword 2>", "<keyword 3>", "<keyword 4>", "<keyword 5>"]
}}"""
    
    user_message = UserMessage(text=prompt)
    response = await chat.send_message(user_message)
    return response

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
    scraped_data = await scrape_url(url)
    
    # Analyze with LLM
    llm_response = await analyze_with_llm(scraped_data, url)
    
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
