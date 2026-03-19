from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from lcm_engine.core.parser import LegacyParser
from lcm_engine.core.chunker import SemanticChunker
from lcm_engine.core.rag_engine import RAGEngine
from lcm_engine.llm.controller import LLMController
from lcm_engine.verification.z3_solver import Z3Solver
from lcm_engine.verification.symbolic_engine import SymbolicEngine
from lcm_engine.verification.error_analyzer import ErrorAnalyzer

class MigrationResult(BaseModel):
    status: str  # "SUCCESS", "FAILED", "PARTIAL"
    translated_code: Optional[str] = None
    attempts: int = 0
    verification_proof: Dict[str, Any] = {}
    error_log: List[Dict[str, Any]] = []

class MigrationAgent:
    """
    Self-correcting agent that orchestrates the modernization flow.
    Parse -> RAG -> LLM Translate -> Verify -> [Loop Error] -> Success
    """
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
        self.parser = LegacyParser()
        self.chunker = SemanticChunker(self.parser)
        self.rag = RAGEngine()
        self.llm = LLMController()
        
        self.sym_engine = SymbolicEngine()
        self.verifier = Z3Solver()
        self.analyzer = ErrorAnalyzer()
        
    def index_repo(self, source_code: str, file_name: str = "unknown"):
        """Chunk and index the source file into the vector DB."""
        chunks = self.chunker.chunk(source_code, file_name=file_name)
        self.rag.index_chunks(chunks)
        return len(chunks)

    def migrate(self, source_code: str, source_lang: str, target_lang: str) -> MigrationResult:
        """
        End-to-end migration of a piece of legacy code.
        """
        # 1. RAG Context Retrieval
        # We index it first if it hasn't been to get semantic search ability over itself
        chunks = self.chunker.chunk(source_code)
        
        # Simple approach: fetch context for the whole snippet
        context_docs = self.rag.retrieve_context(query=source_code, k=3)
        context_str = "\\n---CONTEXT---\\n".join([c["content"] for c in context_docs])
        
        # 2. Initial Translation Phase
        translated_code = self.llm.translate(
            source_code=source_code,
            source_lang=source_lang,
            target_lang=target_lang,
            context=context_str
        )
        
        result_status = "FAILED"
        final_code = translated_code
        error_log = []
        proof = {}
        
        # 3. Verification Loop
        for attempt in range(self.max_retries):
            # Parse IRs
            source_ir = self.sym_engine.translate_cobol_to_ir(source_code)
            target_ir = self.sym_engine.translate_python_to_ir(final_code)
            variables = self.sym_engine.get_variables(source_ir + target_ir)
            
            # Verify
            is_valid, counter_example, status = self.verifier.verify_equivalence(source_ir, target_ir, variables)
            
            if is_valid:
                result_status = "SUCCESS"
                proof = {"status": "verified equivalent", "variables_checked": variables}
                break
                
            # If invalid:
            error_type = self.analyzer.analyze_error(source_code, final_code, status, counter_example)
            
            log_entry = {
                "attempt": attempt + 1,
                "error_type": error_type,
                "counter_example": counter_example,
                "code": final_code
            }
            error_log.append(log_entry)
            
            if attempt < self.max_retries - 1: # Don't request a new one on the last throw
                # Call LLM Error Correction
                feedback = f"Failed with {error_type}. Example counter-case: {counter_example}"
                final_code = self.llm.correct_translation(
                    source_code=source_code,
                    prev_target=final_code,
                    error_type=error_type,
                    error_feedback=feedback,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
        else:
             # Loop completed without break (failed all retries)
             result_status = "FAILED"
             proof = {"status": "unverified", "reason": "max_retries_exceeded"}

        return MigrationResult(
            status=result_status,
            translated_code=final_code,
            attempts=len(error_log) + 1 if result_status == 'SUCCESS' else self.max_retries,
            verification_proof=proof,
            error_log=error_log
        )
