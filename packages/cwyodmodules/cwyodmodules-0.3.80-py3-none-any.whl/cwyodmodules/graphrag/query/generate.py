from ..llm.llm import generate_response
from .graph_search import local_query_graph, global_query_graph
from .vector_search import _similarity_search
from ..database.base import get_db, for_notebook
from ..database.models import Chunk
from .utils import (
    separate_by_rank,
    get_nodes,
    get_text_from_nodes,
    get_all_connected_nodes,
    get_final_text,
    get_context_from_db,
    process_chunks,
    get_node_by_id,
    get_node_from_chunk,
)
from ..llm.query_generation import (
    generate_query_from_question_prompt,
    generate_response_from_context_prompt,
)
import asyncio
from typing import List, Dict, Tuple, Any, Set
from collections import defaultdict
import networkx as nx
import pandas as pd


async def _local_query(
    query: str, top_k: int, max_nodes: int=3, order_range: int=5
) -> Tuple[str | None, List[str], Dict[str, Dict[str, Any]], List[str]]:
    
    db = next(get_db())
    nodes, keywords = await local_query_graph(query=query, top_k=top_k, order_range=order_range)
    chunk_texts: List[str] = []
    for chunk_id in nodes:
        if len(chunk_texts) >= max_nodes:
            break
        chunk_texts.append(
            db.get(Chunk, chunk_id).text
        )
        
    context = "\n".join(chunk_texts)
    response = await generate_response(context=context, query=query)
    db.close()
    return response, chunk_texts, nodes, keywords


async def _global_query(
    query: str, top_k: int, max_nodes: int=3, alpha: float=0.7
) -> Tuple[str | None, List[str], Dict[str, Dict[str, Any]], List[str]]:
    
    db = next(get_db())
    chunks, keywords = await global_query_graph(query=query, top_k=top_k, alpha=alpha, edge_nodes=max_nodes)
    chunk_texts: List[str] = []
    for chunk_id in chunks:
        chunk_texts.append(
            db.get(Chunk, chunk_id).text
        )

    context = "\n".join(chunk_texts)
    response = await generate_response(context=context, query=query)
    db.close()
    return response, chunk_texts, chunks, keywords


async def _hybrid_query(query: str, top_k: int, max_nodes: int=3, alpha: float=0.7, order_range: int=5
) -> Tuple[str | None, List[str], Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]], Set[str]]:
    db = next(get_db())
    local_query_task = asyncio.create_task(local_query_graph(query=query, top_k=top_k, order_range=order_range))
    global_query_task = asyncio.create_task(global_query_graph(query=query, top_k=top_k, alpha=alpha, edge_nodes=max_nodes))
    
    (local_nodes, local_keywords), (global_chunks, global_keywords) = await asyncio.gather(*[local_query_task, global_query_task])
    chunk_texts: List[str] = []
    
    seen_ids = set()
    for chunk_id in local_nodes:
        if len(chunk_texts) >= max_nodes:
            break
        seen_ids.add(chunk_id)
        chunk_texts.append(
            db.get(Chunk, chunk_id).text
        )
        
    for chunk_id in global_chunks:
        if chunk_id in seen_ids: continue
        chunk_texts.append(
            db.get(Chunk, chunk_id).text
        )
        
    context = "\n".join(chunk_texts)
    response = await generate_response(context=context, query=query)
    db.close()
    return response, chunk_texts, (global_chunks, local_nodes), set(local_keywords + global_keywords)

    
async def _naive_rag(query: str, top_k: int) -> Tuple[str, List[str]]:
    db = next(get_db())
    nodes = await _similarity_search(text=query, table='chunk', top_k=top_k)
    chunk_texts: List[str] = []
    for (node, _) in nodes:
        chunk_texts.append(
            node.text
        )
    context = "\n".join(chunk_texts)
    response = await generate_response(context=context, query=query)
    db.close()
    return response, chunk_texts