ML-narzędzia/hermes_agent.py
#!/usr/bin/env python3
# ═════════════════════════════════════════════════════════════
# IMPERIUM 7™ — HERMES AGENT
# Async AI agent with failover, retry logic, and circuit breaker
# ═════════════════════════════════════════════════════════════

import os
import sys
import json
import asyncio
import logging
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import httpx
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# ═════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class Config:
    PORT = int(os.getenv('PORT', 5000))
    WORKERS = int(os.getenv('WORKERS', 4))
    TIMEOUT = int(os.getenv('TIMEOUT', 300))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
    MODEL = os.getenv('MODEL', 'anthropic/claude-3.5-sonnet')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 16000))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    FAILOVER_ENABLED = os.getenv('FAILOVER_ENABLED', 'true').lower() == 'true'
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', 5))

# ═════════════════════════════════════════════════════════════
# MODELS & ENUMS
# ═════════════════════════════════════════════════════════════

class ModelProvider(str, Enum):
    OPENROUTER = 'openrouter'
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    GOOGLE = 'google'
    FALLBACK = 'fallback'

class AgentState(str, Enum):
    READY = 'ready'
    PROCESSING = 'processing'
    CIRCUIT_BROKEN = 'circuit_broken'
    DEGRADED = 'degraded'

class CompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = Config.MODEL
    max_tokens: Optional[int] = Config.MAX_TOKENS
    temperature: Optional[float] = Config.TEMPERATURE
    stream: Optional[bool] = False
    agent_mode: Optional[str] = 'standard'
    context: Optional[Dict[str, Any]] = {}

class CompletionResponse(BaseModel):
    id: str
    content: str
    tokens_used: int
    model: str
    provider: str
    latency_ms: float
    timestamp: str

# ═════════════════════════════════════════════════════════════
# CIRCUIT BREAKER
# ═════════════════════════════════════════════════════════════

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = AgentState.READY

    def record_success(self):
        self.failure_count = 0
        self.state = AgentState.READY

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = AgentState.CIRCUIT_BROKEN
            logger.warning(f'🔴 Circuit breaker activated (failures: {self.failure_count})')

    def can_execute(self) -> bool:
        if self.state == AgentState.READY:
            return True
        if self.state == AgentState.CIRCUIT_BROKEN:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed > self.timeout:
                logger.info('🟢 Circuit breaker reset')
                self.state = AgentState.READY
                self.failure_count = 0
                return True
            return False
        return True

# ═════════════════════════════════════════════════════════════
# MODEL PROVIDER FACTORY
# ═════════════════════════════════════════════════════════════

class ModelProviderFactory:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.circuit_breaker = CircuitBreaker(failure_threshold=Config.CIRCUIT_BREAKER_THRESHOLD)
        self.model_priorities = [
            'anthropic/claude-3.5-sonnet',
            'openai/gpt-4o',
            'google/gemini-1.5-pro',
        ]

    async def call_model(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = Config.MAX_TOKENS,
        temperature: float = Config.TEMPERATURE,
    ) -> Dict[str, Any]:
        """Call AI model with retry & failover logic."""
        model = model or Config.MODEL
        start_time = datetime.now()

        if not self.circuit_breaker.can_execute():
            logger.warning('⚠️ Circuit breaker open - using cached fallback')
            return await self._get_fallback_response(prompt)

        models_to_try = [model] + (self.model_priorities if Config.FAILOVER_ENABLED else [])

        for attempt, target_model in enumerate(models_to_try, 1):
            if attempt > Config.MAX_RETRIES:
                logger.error(f'❌ Max retries exceeded for prompt: {prompt[:50]}...')
                break

            try:
                logger.info(f'🚀 Attempt {attempt}/{Config.MAX_RETRIES} with model: {target_model}')
                response = await self._call_provider(target_model, prompt, max_tokens, temperature)
                self.circuit_breaker.record_success()
                latency = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(f'✅ Success with {target_model} ({latency:.0f}ms)')
                return {
                    'content': response.get('content'),
                    'tokens_used': response.get('tokens_used', 0),
                    'model': target_model,
                    'latency_ms': latency,
                }
            except Exception as e:
                self.circuit_breaker.record_failure()
                logger.warning(f'⚠️ Attempt {attempt} failed with {target_model}: {str(e)}')
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue

        # Fallback
        return await self._get_fallback_response(prompt)

    async def _call_provider(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """Call specific provider API."""
        if 'anthropic' in model:
            return await self._call_anthropic(prompt, max_tokens, temperature)
        elif 'openai' in model:
            return await self._call_openai(prompt, max_tokens, temperature)
        elif 'google' in model:
            return await self._call_google(prompt, max_tokens, temperature)
        elif 'openrouter' in model:
            return await self._call_openrouter(model, prompt, max_tokens, temperature)
        else:
            raise ValueError(f'Unknown model provider: {model}')

    async def _call_openrouter(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """Call OpenRouter API."""
        async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
            response = await client.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {Config.OPENROUTER_API_KEY}',
                    'HTTP-Referer': 'https://imperium.deputatai.com',
                    'X-Title': 'IMPERIUM-7-Hermes',
                },
                json={
                    'model': model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                'content': data['choices'][0]['message']['content'],
                'tokens_used': data['usage'].get('total_tokens', 0),
            }

    async def _call_anthropic(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API."""
        async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
            response = await client.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': Config.ANTHROPIC_API_KEY,
                    'anthropic-version': '2023-06-01',
                },
                json={
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': max_tokens,
                    'messages': [{'role': 'user', 'content': prompt}],
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                'content': data['content'][0]['text'],
                'tokens_used': data.get('usage', {}).get('output_tokens', 0),
            }

    async def _call_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """Call OpenAI GPT API."""
        async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {Config.OPENAI_API_KEY}'},
                json={
                    'model': 'gpt-4o',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                'content': data['choices'][0]['message']['content'],
                'tokens_used': data['usage'].get('total_tokens', 0),
            }

    async def _call_google(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """Call Google Gemini API."""
        async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
            response = await client.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={Config.GOOGLE_GEMINI_API_KEY}',
                json={
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {
                        'maxOutputTokens': max_tokens,
                        'temperature': temperature,
                    },
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                'content': data['candidates'][0]['content']['parts'][0]['text'],
                'tokens_used': 0,
            }

    async def _get_fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Get cached response or generic fallback."""
        prompt_hash = hash(prompt)
        cached = await self.redis.get(f'hermes:cache:{prompt_hash}')
        if cached:
            logger.info('📦 Using cached response')
            return json.loads(cached)
        logger.warning('⚠️ Using fallback response')
        return {
            'content': 'Service temporarily unavailable. Please try again later.',
            'tokens_used': 0,
            'model': 'fallback',
            'latency_ms': 0,
        }

# ═════════════════════════════════════════════════════════════
# FASTAPI APP
# ═════════════════════════════════════════════════════════════

app = FastAPI(
    title='IMPERIUM 7™ — Hermes Agent',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
)

redis_client: Optional[redis.Redis] = None
model_factory: Optional[ModelProviderFactory] = None

@app.on_event('startup')
async def startup_event():
    global redis_client, model_factory
    try:
        redis_client = await redis.from_url(Config.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info('✅ Redis connected')
    except Exception as e:
        logger.error(f'❌ Redis connection failed: {str(e)}')
        redis_client = None
    
    model_factory = ModelProviderFactory(redis_client)
    logger.info('🚀 Hermes Agent startup complete')

@app.on_event('shutdown')
async def shutdown_event():
    if redis_client:
        await redis_client.close()
        logger.info('✅ Redis disconnected')

@app.get('/health')
async def health():
    return {
        'status': 'ok',
        'service': 'hermes-agent',
        'version': '1.0.0',
        'circuit_breaker': model_factory.circuit_breaker.state.value if model_factory else 'unknown',
    }

@app.post('/complete')
async def complete(request: CompletionRequest, background_tasks: BackgroundTasks):
    """Generate completion with fallback & retry logic."""
    if not model_factory:
        raise HTTPException(status_code=503, detail='Service not ready')

    try:
        response = await model_factory.call_model(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        # Cache for fallback
        if redis_client:
            prompt_hash = hash(request.prompt)
            await redis_client.setex(f'hermes:cache:{prompt_hash}', 3600, json.dumps(response))
        
        return CompletionResponse(
            id=f'hermes_{datetime.now().timestamp()}',
            content=response['content'],
            tokens_used=response['tokens_used'],
            model=response['model'],
            provider=response['model'].split('/')[0],
            latency_ms=response['latency_ms'],
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f'❌ Completion failed: {traceback.format_exc()}')
        raise HTTPException(status_code=500, detail=f'Completion failed: {str(e)}')

@app.post('/complete/stream')
async def complete_stream(request: CompletionRequest):
    """Stream completion response."""
    async def generate():
        try:
            response = await model_factory.call_model(
                prompt=request.prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            content = response['content']
            for chunk in content.split():
                yield f'data: {json.dumps({"chunk": chunk})}\n\n'
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f'data: {json.dumps({"error": str(e)})}\n\n'

    return StreamingResponse(generate(), media_type='text/event-stream')

@app.post('/mode/foa')
async def mode_foa(request: CompletionRequest):
    """FOA-1 (Founder Operations Agent) mode."""
    foa_prompt = f'"""You are FOA-1 GOLD (Founder Operations Agent). Context: {request.context}\n\nTask: {request.prompt}\n\nRespond with operational clarity and business impact."""'
    return await complete(CompletionRequest(prompt=foa_prompt, **request.dict(exclude={'prompt'})))

@app.post('/mode/soa')
async def mode_soa(request: CompletionRequest):
    """SOA-1 (Strategic Operations Agent) mode."""
    soa_prompt = f'"""You are SOA-1 ULTRA (Strategic Orchestration Agent). Mode: CONSULT.\n\nContext: {request.context}\n\nTask: {request.prompt}\n\nProvide strategic analysis with risk assessment."""'
    return await complete(CompletionRequest(prompt=soa_prompt, **request.dict(exclude={'prompt'})))

@app.post('/mode/fusion')
async def mode_fusion(request: CompletionRequest):
    """Fusion Core (Multi-Model) mode."""
    fusion_prompt = f'"""You are FUSION-CORE orchestrating multiple AI agents.\n\nContext: {request.context}\n\nTask: {request.prompt}\n\nCoordinate FOA-1, SOA-1, TSA-1, SFA-1, OPA-1, OMA-1 responses."""'
    return await complete(CompletionRequest(prompt=fusion_prompt, **request.dict(exclude={'prompt'})))

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=Config.PORT,
        workers=Config.WORKERS,
        log_level=os.getenv('LOG_LEVEL', 'info').lower(),
    )
