import re
from typing import Dict, Any, List

class LegacyParser:
    """
    Simplified Regex-based parser for COBOL for the context optimization prototype.
    Extracts Divisions, Sections, Paragraphs, and Statements.
    """
    def __init__(self):
        # Basic patterns for COBOL structure
        self.division_pattern = re.compile(r"^\s*([A-Z\-]+)\s+DIVISION\.", re.IGNORECASE | re.MULTILINE)
        self.paragraph_pattern = re.compile(r"^\s*([A-Z0-9\-]+)\.\s*$", re.MULTILINE)
        self.compute_pattern = re.compile(r"^\s*COMPUTE\s+(.*?)$", re.IGNORECASE | re.MULTILINE)
        self.call_pattern = re.compile(r"^\s*CALL\s+['\"](.*?)['\"]", re.IGNORECASE | re.MULTILINE)
        self.move_pattern = re.compile(r"^\s*MOVE\s+(.*?)\s+TO\s+(.*?)$", re.IGNORECASE | re.MULTILINE)

    def parse(self, source_code: str) -> Dict[str, Any]:
        """Parse source code and return a simplified AST and metadata."""
        tree = {
            "divisions": [],
            "paragraphs": [],
            "computations": [],
            "calls": [],
            "moves": []
        }
        
        # Extract divisions
        for match in self.division_pattern.finditer(source_code):
            tree["divisions"].append(match.group(1))
            
        # Extract paragraphs (can act as function blocks in COBOL)
        for match in self.paragraph_pattern.finditer(source_code):
            para_name = match.group(1).strip()
            if para_name not in ["PROCEDURE", "DATA", "ENVIRONMENT", "IDENTIFICATION"]:
                tree["paragraphs"].append(para_name)
                
        # Extract COMPUTATION statements
        for match in self.compute_pattern.finditer(source_code):
            tree["computations"].append(match.group(1).strip())
            
        # Extract CALL statements (dependencies)
        for match in self.call_pattern.finditer(source_code):
            tree["calls"].append(match.group(1).strip())
            
        # Extract MOVES
        for match in self.move_pattern.finditer(source_code):
            tree["moves"].append({"from": match.group(1).strip(), "to": match.group(2).strip()})

        metadata = {
            "has_procedure": "PROCEDURE" in tree["divisions"],
            "has_data": "DATA" in tree["divisions"],
            "dependency_count": len(tree["calls"])
        }
        
        return {
            "ast": tree,
            "metadata": metadata,
            "raw": source_code
        }
