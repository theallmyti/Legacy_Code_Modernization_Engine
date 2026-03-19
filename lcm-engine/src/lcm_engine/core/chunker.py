from typing import List, Dict, Any
from .parser import LegacyParser
import re

class SemanticChunker:
    """
    Breaks down parsed code into semantic chunks (e.g. paragraphs in COBOL).
    """
    def __init__(self, parser: LegacyParser):
        self.parser = parser

    def chunk(self, source_code: str, file_name: str = "unknown") -> List[Dict[str, Any]]:
        """
        Chunk by COBOL divisions and paragraphs to preserve semantic meaning.
        Returns a list of chunk dictionaries.
        """
        parse_result = self.parser.parse(source_code)
        chunks = []
        
        # For simplicity, let's chunk by paragraphs which are similar to functions in COBOL
        # If no paragraphs, we chunk the whole file.
        paragraphs = parse_result["ast"].get("paragraphs", [])
        
        if not paragraphs:
            # Fallback to whole file chunk
            chunks.append({
                "id": f"{file_name}_module",
                "type": "module",
                "name": file_name,
                "content": source_code,
                "dependencies": parse_result["ast"].get("calls", []),
                "metadata": parse_result["metadata"]
            })
            return chunks

        # Try to slice the source code by paragraph headers
        lines = source_code.split("\n")
        current_chunk_name = f"{file_name}_globals"
        current_chunk_content = []
        
        for line in lines:
            # Check if line is a paragraph header
            is_header = False
            for p in paragraphs:
                if re.match(rf"^\s*{p}\.\s*$", line):
                    # Save old chunk
                    if current_chunk_content:
                        chunks.append(self._create_chunk(current_chunk_name, current_chunk_content, parse_result))
                    # Start new chunk
                    current_chunk_name = p
                    current_chunk_content = [line]
                    is_header = True
                    break
            
            if not is_header:
                current_chunk_content.append(line)
                
        # Append the last chunk
        if current_chunk_content:
            chunks.append(self._create_chunk(current_chunk_name, current_chunk_content, parse_result))
            
        return chunks

    def _create_chunk(self, name: str, lines: List[str], parse_result: Dict) -> Dict[str, Any]:
        content = "\n".join(lines)
        
        # Simple local dependency extraction
        local_calls = []
        for call in parse_result["ast"]["calls"]:
            if f"CALL '{call}'" in content or f'CALL "{call}"' in content:
                local_calls.append(call)
                
        return {
            "id": name,
            "type": "paragraph" if name != "globals" else "module",
            "name": name,
            "content": content,
            "dependencies": local_calls,
            "metadata": {"length": len(content)}
        }
