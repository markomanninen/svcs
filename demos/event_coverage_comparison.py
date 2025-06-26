#!/usr/bin/env python3
"""
Event Coverage Comparison - Legacy vs New System
=================================================

Direct comparison using the same test data from comprehensive_language_test.py
to see how the new modular system performs on the legacy test cases.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import both systems
from svcs_multilang import MultiLanguageAnalyzer  # Legacy system
from svcs.semantic_analyzer import SVCSModularAnalyzer  # New modular system

def get_test_files():
    """Get the test files from comprehensive_language_test.py"""
    
    # PHP Test Files
    php_before = '''<?php
namespace App\\Services;

use App\\Models\\User;
use Psr\\Log\\LoggerInterface;

/**
 * Basic user service
 */
class UserService {
    private $logger;
    const VERSION = "1.0";
    
    public function __construct(LoggerInterface $logger) {
        $this->logger = $logger;
    }
    
    public function createUser($name, $email) {
        $user = new User();
        $user->name = $name;
        $user->email = $email;
        return $user;
    }
    
    public function validateEmail($email) {
        return filter_var($email, FILTER_VALIDATE_EMAIL);
    }
}
?>'''

    php_after = '''<?php
namespace App\\Enterprise\\Services\\Advanced;

use App\\Models\\User;
use App\\Models\\Profile;
use App\\Repositories\\UserRepository;
use App\\Validators\\EmailValidator;
use App\\Events\\UserCreated;
use App\\Traits\\Loggable;
use Psr\\Log\\LoggerInterface;
use Illuminate\\Support\\Facades\\Event;

/**
 * Advanced enterprise user service with comprehensive features
 * 
 * @implements UserServiceInterface
 * @uses Loggable
 */
class AdvancedUserService implements UserServiceInterface {
    use Loggable;
    
    private LoggerInterface $logger;
    private UserRepository $userRepository;
    private EmailValidator $emailValidator;
    
    const VERSION = "2.0";
    const MAX_BATCH_SIZE = 1000;
    
    public function __construct(
        LoggerInterface $logger,
        UserRepository $userRepository,
        EmailValidator $emailValidator
    ) {
        $this->logger = $logger;
        $this->userRepository = $userRepository;
        $this->emailValidator = $emailValidator;
    }
    
    public function createUser(string $name, string $email, array $metadata = []): User {
        $this->validateUserData($name, $email);
        
        $user = new User();
        $user->name = $name;
        $user->email = $email;
        $user->metadata = $metadata;
        $user->created_at = now();
        
        $savedUser = $this->userRepository->save($user);
        
        Event::dispatch(new UserCreated($savedUser));
        $this->logActivity('user_created', $savedUser->id);
        
        return $savedUser;
    }
    
    public function createUserBatch(array $users): array {
        $createdUsers = [];
        foreach (array_chunk($users, self::MAX_BATCH_SIZE) as $batch) {
            foreach ($batch as $userData) {
                $createdUsers[] = $this->createUser(
                    $userData['name'],
                    $userData['email'],
                    $userData['metadata'] ?? []
                );
            }
        }
        return $createdUsers;
    }
    
    public function validateUserData(string $name, string $email): void {
        if (empty($name)) {
            throw new InvalidArgumentException('Name cannot be empty');
        }
        
        if (!$this->emailValidator->validate($email)) {
            throw new InvalidArgumentException('Invalid email format');
        }
    }
    
    public function validateEmail(string $email): bool {
        return $this->emailValidator->validate($email);
    }
    
    private function logActivity(string $action, int $userId): void {
        $this->logger->info("User action: {$action}", [
            'user_id' => $userId,
            'timestamp' => time(),
            'service' => self::class
        ]);
    }
}

interface UserServiceInterface {
    public function createUser(string $name, string $email, array $metadata = []): User;
    public function validateEmail(string $email): bool;
}
?>'''

    # JavaScript Test Files
    js_before = '''const express = require('express');

function createServer() {
    const app = express();
    
    app.get('/users', (req, res) => {
        res.json({users: []});
    });
    
    return app;
}

module.exports = {createServer};'''

    js_after = '''const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const {body, validationResult} = require('express-validator');

class UserService {
    constructor(database, logger) {
        this.db = database;
        this.logger = logger;
        this.cache = new Map();
    }
    
    async getUsers(page = 1, limit = 10) {
        const cacheKey = `users_${page}_${limit}`;
        
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        try {
            const users = await this.db.users.findMany({
                skip: (page - 1) * limit,
                take: limit,
                orderBy: {createdAt: 'desc'}
            });
            
            this.cache.set(cacheKey, users);
            this.logger.info(`Retrieved ${users.length} users`);
            
            return users;
        } catch (error) {
            this.logger.error('Failed to retrieve users:', error);
            throw new Error('Database query failed');
        }
    }
    
    async createUser(userData) {
        const validationErrors = validationResult(userData);
        if (!validationErrors.isEmpty()) {
            throw new Error('Validation failed');
        }
        
        return await this.db.users.create({
            data: {
                ...userData,
                createdAt: new Date()
            }
        });
    }
}

function createAdvancedServer(database, logger) {
    const app = express();
    const userService = new UserService(database, logger);
    
    // Security middleware
    app.use(helmet());
    app.use(cors({
        origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
        credentials: true
    }));
    
    // Rate limiting
    const limiter = rateLimit({
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100 // limit each IP to 100 requests per windowMs
    });
    app.use(limiter);
    
    app.use(express.json({limit: '1mb'}));
    
    // Enhanced users endpoint
    app.get('/users', async (req, res) => {
        try {
            const page = parseInt(req.query.page) || 1;
            const limit = parseInt(req.query.limit) || 10;
            
            const users = await userService.getUsers(page, limit);
            
            res.json({
                users,
                pagination: {
                    page,
                    limit,
                    total: users.length
                }
            });
        } catch (error) {
            logger.error('Error fetching users:', error);
            res.status(500).json({error: 'Internal server error'});
        }
    });
    
    // New user creation endpoint
    app.post('/users', [
        body('name').isLength({min: 2}).trim(),
        body('email').isEmail().normalizeEmail()
    ], async (req, res) => {
        try {
            const user = await userService.createUser(req.body);
            res.status(201).json({user});
        } catch (error) {
            logger.error('Error creating user:', error);
            res.status(400).json({error: error.message});
        }
    });
    
    return app;
}

module.exports = {
    createServer: createAdvancedServer,
    UserService
};'''

    # Python Test Files  
    python_before = '''import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self, item):
        self.data.append(item)
        return len(self.data)
'''

    python_after = '''import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from functools import wraps, lru_cache

# Enhanced imports and dependencies
import pandas as pd
import numpy as np
from prometheus_client import Counter, Histogram, generate_latest

# Metrics and monitoring
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests')
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')

@dataclass
class ProcessingConfig:
    """Configuration for data processing operations."""
    batch_size: int = 100
    max_workers: int = 4
    timeout: float = 30.0
    retry_attempts: int = 3
    cache_ttl: int = 300
    processing_strategies: List[str] = field(default_factory=lambda: ['parallel', 'batch'])

class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@asynccontextmanager
async def performance_monitor(operation_name: str):
    """Context manager for monitoring operation performance."""
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        logging.info(f"{operation_name} completed in {duration:.2f}s")

async def fetch_data_async(
    url: str, 
    session: aiohttp.ClientSession,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Asynchronously fetch data from a URL with enhanced error handling.
    
    Args:
        url: The URL to fetch data from
        session: aiohttp session for making requests
        headers: Optional HTTP headers
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing the response data
        
    Raises:
        DataValidationError: If the response is invalid
        aiohttp.ClientError: If the request fails
    """
    async with performance_monitor(f"fetch_data: {url}"):
        try:
            async with session.get(
                url, 
                headers=headers or {}, 
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                if not isinstance(data, dict):
                    raise DataValidationError("Response must be a dictionary")
                
                return data
                
        except aiohttp.ClientError as e:
            logging.error(f"HTTP request failed for {url}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error fetching {url}: {e}")
            raise DataValidationError(f"Failed to fetch data: {str(e)}")

class AdvancedDataProcessor:
    """
    Advanced data processor with async operations, caching, and monitoring.
    
    Features:
    - Asynchronous data processing
    - Configurable batch processing
    - Built-in caching with TTL
    - Comprehensive error handling
    - Performance monitoring
    - Thread pool for CPU-intensive tasks
    """
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        self.data: List[Dict[str, Any]] = []
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
    
    @lru_cache(maxsize=128)
    def _get_cache_key(self, url: str, params: str = "") -> str:
        """Generate a cache key for the given URL and parameters."""
        return f"{url}:{hash(params)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid based on TTL."""
        if cache_key not in self.cache_timestamps:
            return False
        
        age = time.time() - self.cache_timestamps[cache_key]
        return age < self.config.cache_ttl
    
    @retry_on_failure(max_attempts=3)
    async def fetch_and_process(
        self, 
        urls: List[str], 
        transform_func: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from multiple URLs and optionally transform it.
        
        Args:
            urls: List of URLs to fetch
            transform_func: Optional function to transform each response
            
        Returns:
            List of processed data dictionaries
        """
        if not self.session:
            raise RuntimeError("Processor must be used as async context manager")
            
        tasks = []
        for url in urls:
            cache_key = self._get_cache_key(url)
            
            if self._is_cache_valid(cache_key):
                self.logger.info(f"Using cached data for {url}")
                continue
                
            task = asyncio.create_task(
                fetch_data_async(url, self.session, timeout=self.config.timeout)
            )
            tasks.append((url, task))
        
        results = []
        for url, task in tasks:
            try:
                data = await task
                
                if transform_func:
                    # Run CPU-intensive transform in thread pool
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(
                        self.executor, transform_func, data
                    )
                
                cache_key = self._get_cache_key(url)
                self.cache[cache_key] = data
                self.cache_timestamps[cache_key] = time.time()
                
                results.append(data)
                
            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")
                continue
        
        return results
    
    async def process_batch(
        self, 
        items: List[Any], 
        processor_func: callable
    ) -> List[Any]:
        """
        Process items in batches using the configured batch size.
        
        Args:
            items: Items to process
            processor_func: Function to process each batch
            
        Returns:
            List of processed results
        """
        results = []
        
        for i in range(0, len(items), self.config.batch_size):
            batch = items[i:i + self.config.batch_size]
            
            try:
                async with performance_monitor(f"batch_{i}"):
                    batch_result = await processor_func(batch)
                    results.extend(batch_result)
                    
            except Exception as e:
                self.logger.error(f"Batch processing failed at index {i}: {e}")
                continue
                
        return results
    
    def process_sync(self, item: Any) -> int:
        """
        Legacy synchronous processing method for backwards compatibility.
        
        Args:
            item: Item to process
            
        Returns:
            Current length of processed data
        """
        if not isinstance(item, dict):
            item = {"data": item, "processed_at": time.time()}
            
        self.data.append(item)
        return len(self.data)
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        return {
            "total_items": len(self.data),
            "cache_size": len(self.cache),
            "config": {
                "batch_size": self.config.batch_size,
                "max_workers": self.config.max_workers,
                "cache_ttl": self.config.cache_ttl
            },
            "performance_metrics": {
                "request_count": REQUEST_COUNT._value._value,
                "avg_duration": REQUEST_DURATION._sum._value / max(REQUEST_DURATION._count._value, 1)
            }
        }

# Factory function for backwards compatibility
def create_processor(config: ProcessingConfig = None) -> AdvancedDataProcessor:
    """Create a new AdvancedDataProcessor instance."""
    return AdvancedDataProcessor(config)

# Legacy compatibility
DataProcessor = AdvancedDataProcessor
fetch_data = fetch_data_async
'''

    return {
        'php': {'before': php_before, 'after': php_after},
        'javascript': {'before': js_before, 'after': js_after},
        'python': {'before': python_before, 'after': python_after}
    }

def test_legacy_system(test_files):
    """Test the legacy system with the same files."""
    print("🏛️ LEGACY SYSTEM TEST")
    print("=" * 40)
    
    analyzer = MultiLanguageAnalyzer()
    total_events = 0
    all_event_types = set()
    results = {}
    
    for lang, files in test_files.items():
        print(f"\n🔍 Testing {lang.upper()}")
        print("-" * 20)
        
        # Analyze with legacy system (filename, before_content, after_content)
        filename = f"test.{lang}"
        events = analyzer.analyze_file_changes(filename, files['before'], files['after'])
        
        event_types = set(event['event_type'] if isinstance(event, dict) else event.event_type for event in events)
        results[lang] = {
            'events': len(events),
            'types': len(event_types),
            'type_list': sorted(event_types)
        }
        
        total_events += len(events)
        all_event_types.update(event_types)
        
        print(f"📈 Events: {len(events)}")
        print(f"🎯 Types: {len(event_types)}")
        for event_type in sorted(event_types):
            if events and isinstance(events[0], dict):
                count = sum(1 for e in events if e['event_type'] == event_type)
            else:
                count = sum(1 for e in events if e.event_type == event_type)
            print(f"   • {event_type}: {count}")
                
    print(f"\n📊 LEGACY TOTAL: {total_events} events, {len(all_event_types)} types")
    return results, total_events, len(all_event_types)

def test_new_system(test_files):
    """Test the new modular system with the same files."""
    print("\n🚀 NEW MODULAR SYSTEM TEST")
    print("=" * 40)
    
    analyzer = SVCSModularAnalyzer()
    total_events = 0
    all_event_types = set()
    results = {}
    
    for lang, files in test_files.items():
        print(f"\n🔍 Testing {lang.upper()}")
        print("-" * 20)
        
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{lang}', delete=False) as before_file:
            before_file.write(files['before'])
            before_path = before_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{lang}', delete=False) as after_file:
            after_file.write(files['after'])
            after_path = after_file.name
        
        try:
            # Read file contents
            with open(before_path, 'r') as f:
                before_content = f.read()
            with open(after_path, 'r') as f:
                after_content = f.read()
                
            # Analyze with new system (returns list of dicts)
            events_data = analyzer.analyze_file_changes(after_path, before_content, after_content)
            
            # Convert to event objects for compatibility
            from types import SimpleNamespace
            events = []
            for event_dict in events_data:
                event = SimpleNamespace()
                event.event_type = event_dict.get('event_type', 'unknown')
                event.confidence = event_dict.get('confidence', 1.0)
                event.layer = event_dict.get('layer', 'unknown')
                events.append(event)
            
            event_types = set(event.event_type for event in events)
            results[lang] = {
                'events': len(events),
                'types': len(event_types),
                'type_list': sorted(event_types)
            }
            
            total_events += len(events)
            all_event_types.update(event_types)
            
            print(f"📈 Events: {len(events)}")
            print(f"🎯 Types: {len(event_types)}")
            for event_type in sorted(event_types):
                count = sum(1 for e in events if e.event_type == event_type)
                print(f"   • {event_type}: {count}")
                
        finally:
            # Cleanup
            os.unlink(before_path)
            os.unlink(after_path)
    
    print(f"\n📊 NEW TOTAL: {total_events} events, {len(all_event_types)} types")
    return results, total_events, len(all_event_types)

def main():
    """Run the direct comparison test."""
    print("⚖️ DIRECT EVENT COVERAGE COMPARISON")
    print("=" * 60)
    print("Using identical test data for both systems")
    
    test_files = get_test_files()
    
    # Test both systems
    legacy_results, legacy_total, legacy_types = test_legacy_system(test_files)
    new_results, new_total, new_types = test_new_system(test_files)
    
    # Comparison
    print(f"\n📊 COMPARISON SUMMARY")
    print("=" * 30)
    
    for lang in ['php', 'javascript', 'python']:
        legacy_events = legacy_results[lang]['events'] 
        new_events = new_results[lang]['events']
        
        legacy_types_count = legacy_results[lang]['types']
        new_types_count = new_results[lang]['types']
        
        print(f"\n{lang.upper()}:")
        print(f"  Legacy:  {legacy_events} events, {legacy_types_count} types")
        print(f"  New:     {new_events} events, {new_types_count} types")
        print(f"  Diff:    {new_events - legacy_events:+d} events, {new_types_count - legacy_types_count:+d} types")
    
    print(f"\nOVERALL:")
    print(f"  Legacy:  {legacy_total} events, {legacy_types} types")
    print(f"  New:     {new_total} events, {new_types} types")
    print(f"  Diff:    {new_total - legacy_total:+d} events, {new_types - legacy_types:+d} types")
    
    # Analysis
    print(f"\n🎯 ANALYSIS:")
    if new_total >= legacy_total:
        print("✅ New system matches or exceeds legacy event detection")
    else:
        print("⚠️  New system detects fewer total events")
        print(f"   Difference: {legacy_total - new_total} fewer events")
    
    if new_types >= legacy_types:
        print("✅ New system has equal or better event type diversity")
    else:
        print("⚠️  New system has fewer event types")
        
    # Show unique types in each system
    legacy_all_types = set()
    new_all_types = set()
    
    for lang_data in legacy_results.values():
        legacy_all_types.update(lang_data['type_list'])
        
    for lang_data in new_results.values():
        new_all_types.update(lang_data['type_list'])
    
    legacy_only = legacy_all_types - new_all_types
    new_only = new_all_types - legacy_all_types
    
    if legacy_only:
        print(f"\n📝 Event types ONLY in legacy system ({len(legacy_only)}):")
        for event_type in sorted(legacy_only):
            print(f"   • {event_type}")
    
    if new_only:
        print(f"\n📝 Event types ONLY in new system ({len(new_only)}):")
        for event_type in sorted(new_only):
            print(f"   • {event_type}")

if __name__ == "__main__":
    main()
