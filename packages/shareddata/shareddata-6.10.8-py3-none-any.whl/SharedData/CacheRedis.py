import pandas as pd
import numpy as np
import time
import os
import queue
from redis import Redis
from redis.cluster import RedisCluster, ClusterNode
from redis.asyncio import Redis as RedisAsync
from redis.asyncio.cluster import RedisCluster as RedisClusterAsync
from redis.asyncio.cluster import ClusterNode as ClusterNodeAsync
from typing import Set, Dict
import bson
import asyncio

from datetime import datetime, timezone

from SharedData.Logger import Logger
from SharedData.Database import DATABASE_PKEYS

class CacheRedis:
    def __init__(self, database, period, source, tablename, user='master'):
        """Initialize RedisCluster connection."""
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.user = user

        self.path = f'{user}/{database}/{period}/{source}/cache/{tablename}'
        self.data = {}                
        self.queue = asyncio.Queue()
        self._flush_task = None
        self._flush_lock = asyncio.Lock()        
        self.pkeycolumns = DATABASE_PKEYS[database]
        self.mtime = datetime(1970,1,1, tzinfo=timezone.utc)

        if not 'REDIS_CLUSTER_NODES' in os.environ:
            raise Exception('REDIS_CLUSTER_NODES not defined')
        startup_nodes = []
        for node in os.environ['REDIS_CLUSTER_NODES'].split(','):
            startup_nodes.append( (node.split(':')[0], int(node.split(':')[1])) )
        if len(startup_nodes)>1:
            startup_nodes = [ClusterNode(node[0], int(node[1])) 
                             for node in startup_nodes]
            self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=False)            
            self.redis_async = RedisClusterAsync(startup_nodes=startup_nodes, decode_responses=False)
        else:
            node = startup_nodes[0]
            host, port = node[0], int(node[1])
            self.redis = Redis(host=host, port=port, decode_responses=False)
            self.redis_async = RedisAsync(host=host, port=port, decode_responses=False)

        self.header = CacheHeader(self)

        if not self.header['cache->counter']:
            self.header['cache->counter'] = 0
                
    def __getitem__(self, pkey):
        if not isinstance(pkey, str):
            raise Exception('pkey must be a string')
        if '#' in pkey:
            raise Exception('pkey cannot contain #')
        _bson = self.redis.get(self.get_hash(pkey))
        if _bson is None:
            return {}
        value = bson.BSON.decode(_bson)        
        self.data[pkey] = value
        return value
    
    def get(self, pkey):        
        return self.__getitem__(pkey)
    
    def mget(self, pkeys: list[str]) -> list[dict]:
        """
        Retrieve multiple entries from Redis in a single call.

        :param pkeys: List of primary keys (as strings)
        :return: List of decoded dicts (empty dict if missing)
        """
        if len(pkeys) == 0:
            return []
        if not isinstance(pkeys, list):
            raise Exception('pkeys must be a list of strings')
        if any('#' in pkey for pkey in pkeys):
            raise Exception('pkeys cannot contain #')        
        redis_keys = [self.get_hash(pkey) for pkey in pkeys]
        vals = self.redis.mget(redis_keys)
        result = []
        for pkey, _bson in zip(pkeys, vals):
            if _bson is None:
                result.append({})
            else:
                value = bson.BSON.decode(_bson)
                self.data[pkey] = value
                result.append(value)
        return result

    def load(self) -> dict:
        """Load all data from Redis into the cache dictionary using mget for efficiency."""        
        pkeys = self.list_keys('*')
        self.mget(pkeys)
        return self.data

    def get_pkey(self, value):
        key_parts = [
            str(value[col])
            for col in self.pkeycolumns
            if col in ['symbol','portfolio','tag']
        ]        
        return ','.join(key_parts)

    def get_hash(self, pkey: str) -> str:
        """
        Return the full Redis key for a given pkey, using a hash tag for cluster slot affinity.
        All keys with the same path will map to the same slot.
        """
        return f"{{{self.path}}}:{pkey}"
     
    def list_keys(self, keyword = '*', count=None):
        # keys look like {self.path}:pkey
        pattern = f"{{{self.path}}}:{keyword}"
        result = []
        if count is None:
            for key in self.redis.scan_iter(match=pattern):
                # Extract pkey part after colon
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                # {user/db/period/source/cache/table}:pkey            
                parts = key.split(':', 1)
                if len(parts) > 1:
                    result.append(parts[1])
        else:
            for key in self.redis.scan_iter(match=pattern,count=count):
                # Extract pkey part after colon
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                # {user/db/period/source/cache/table}:pkey            
                parts = key.split(':', 1)
                if len(parts) > 1:
                    result.append(parts[1])

        return result

    def __setitem__(self, pkey, new_value):                        
        if pkey in self.data:
            self.data[pkey] = self.recursive_update(self.data[pkey],new_value)
        else:
            self.data[pkey] = new_value
        _bson = bson.BSON.encode(self.data[pkey])
        self.redis.set(self.get_hash(pkey), _bson)        
    
    def recursive_update(self, original, updates):
        """
        Recursively update the original dictionary with updates from the new dictionary,
        preserving unmentioned fields at each level of depth.
        """
        for key, value in updates.items():
            if isinstance(value, dict):
                # Get existing nested dictionary or use an empty dict if not present
                original_value = original.get(key, {})
                if isinstance(original_value, dict):
                    # Merge recursively
                    original[key] = self.recursive_update(original_value, value)
                else:
                    # Directly assign if original is not a dict
                    original[key] = value
            else:
                # Non-dict values are directly overwritten
                original[key] = value
        return original

    def set(self, new_value, pkey=None):
        if pkey is None:
            pkey = self.get_pkey(new_value)
        self.__setitem__(pkey, new_value)        

    async def async_set(self, new_value):
        """
        Asynchronously set a message in the cache and signal the queue.

        Raises:
            Exception: 
        """        
        async with self._flush_lock:
            if self._flush_task is None or self._flush_task.done():
                self._flush_task = asyncio.create_task(self.async_flush_loop())
        await self.queue.put(new_value)
            
    async def async_flush_loop(self) -> None:
        """Flush the queue to Redis asynchronously."""        
        try:
            while True:            
                flush_pkeys = set()
                
                new_value = await self.queue.get()
                pkey = self.get_pkey(new_value)
                flush_pkeys.add(pkey)
                if pkey in self.data:
                    self.data[pkey] = self.recursive_update(self.data[pkey], new_value)
                else:
                    self.data[pkey] = new_value
                                
                # Keep draining the queue until empty
                while not self.queue.empty():
                    new_value = await self.queue.get()
                    pkey = self.get_pkey(new_value)
                    flush_pkeys.add(pkey)
                    if pkey in self.data:
                        self.data[pkey] = self.recursive_update(self.data[pkey], new_value)
                    else:
                        self.data[pkey] = new_value
                                    
                with self.redis_async.pipeline() as pipe:
                    for pkey in flush_pkeys:
                        rhash = self.get_hash(pkey)
                        _bson = bson.BSON.encode(self.data[pkey])
                        pipe.set(rhash, _bson)                        
                    await pipe.execute()
                await self.header.async_incrby("cache->counter", len(flush_pkeys))
        except Exception as e:
            Logger.error(f"Error in async_flush_loop: {e}")

    def __delitem__(self, pkey: str):
        """Delete a header key."""
        self.redis.delete(self.get_hash(pkey))

    def clear(self):
        """Clear the cache."""        
        delkeys =self.list_keys()
        for key in delkeys:
            self.redis.delete(key)
        self.data = {}
    
    def __iter__(self):
        for key in self.list_keys():
            yield key
       

class CacheHeader():    
    """
    A dict-like interface for cached headers stored in Redis.
    Supports basic mapping operations: get, set, delete, iterate.
    """
    def __init__(self, cache):
        self.cache = cache

    def get_hash(self, pkey: str) -> str:
        return f"{{{self.cache.path}}}#{pkey}"

    def __getitem__(self, pkey: str):
        """Retrieve a header value by key."""
        val = self.cache.redis.get(self.get_hash(pkey))
        return val

    def __setitem__(self, pkey: str, value):
        """Set a header value by key."""
        self.cache.redis.set(self.get_hash(pkey), value)

    def __delitem__(self, pkey: str):
        """Delete a header key."""
        self.cache.redis.delete(self.get_hash(pkey))

    def __iter__(self):
        """Iterate over header keys."""
        pattern = f"{{{self.cache.path}}}#*"
        for key in self.cache.redis.scan_iter(match=pattern):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            _, header_key = key_str.split('#', 1)
            yield header_key
    
    def incrby(self, field, value):
        _pkey = self.get_hash(field)
        self.cache.redis.incrby(_pkey,value)
    
    async def async_incrby(self, field, value):
        _pkey = self.get_hash(field)
        await self.cache.redis_async.incrby(_pkey,value)
    
    def list_keys(self, keyword = '*', count=None):
        # keys look like {self.path}:pkey
        pattern = f"{{{self.cache.path}}}#{keyword}"
        result = []
        if count is None:
            for key in self.cache.redis.scan_iter(match=pattern):
                # Extract pkey part after colon
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                # {user/db/period/source/cache/table}:pkey            
                parts = key.split('#', 1)
                if len(parts) > 1:
                    result.append(parts[1])
        else:
            for key in self.cache.redis.scan_iter(match=pattern,count=count):
                # Extract pkey part after colon
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                # {user/db/period/source/cache/table}:pkey            
                parts = key.split('#', 1)
                if len(parts) > 1:
                    result.append(parts[1])

        return result
